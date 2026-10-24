#!/usr/bin/env python3
"""Finite actual-adapter observations checked against a proved typed decision."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
PINS = ROOT / 'experiments/production-retirement/pins.json'
VARIANTS = ['baseline', 'equivalent', 'guard-bypass', 'allow-unacknowledged', 'overbroad-removal', 'caller-alias']
UNDEFINED = object()
MAX_SOURCE = 16 * 1024 * 1024


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(tag):
    kind = tag[0]
    if kind == 'undefined':
        assert len(tag) == 1
        return UNDEFINED
    if kind == 'null':
        assert len(tag) == 1
        return None
    if kind in ['string', 'boolean', 'natural']:
        assert len(tag) == 2
        value = tag[1]
        assert ((kind == 'string' and isinstance(value, str)) or
                (kind == 'boolean' and type(value) is bool) or
                (kind == 'natural' and type(value) is int and 0 <= value <= 2**53-1))
        return value
    if kind == 'array':
        assert len(tag) == 2
        return [decode(x) for x in tag[1]]
    assert kind == 'object' and len(tag) == 2
    assert all(type(key) is str for key, _ in tag[1])
    assert len({key for key, _ in tag[1]}) == len(tag[1])
    return {key: decode(value) for key, value in tag[1]}


def encode(value):
    if value is UNDEFINED:
        return ['undefined']
    if value is None:
        return ['null']
    if type(value) is bool:
        return ['boolean', value]
    if type(value) is int:
        assert 0 <= value <= 2**53-1
        return ['natural', value]
    if isinstance(value, str):
        return ['string', value]
    if isinstance(value, list):
        return ['array', [encode(x) for x in value]]
    assert type(value) is dict
    # JavaScript's default key sort compares UTF16 code units.
    return ['object', [[key, encode(value[key])] for key in sorted(value, key=lambda x: x.encode('utf-16-be', 'surrogatepass'))]]


class Projection:
    def __init__(self):
        self.codes = {}
        self.values = []

    def atom(self, value):
        tagged = encode(value)
        assert encode(decode(tagged)) == tagged
        canonical = json.dumps(tagged, ensure_ascii=True, separators=(',', ':'))
        if canonical not in self.codes:
            self.codes[canonical] = len(self.values) + 1
            self.values.append(tagged)
        return str(self.codes[canonical])

    def words(self, value):
        return '[' + self.atom(value) + ']'

    def metadata_value(self, value):
        return 'None' if value is UNDEFINED else '(Some ' + self.words(value) + ')'

    def document(self, value):
        assert value is None or (type(value) is dict and set(value) == {'version', 'raw'} and type(value['version']) is str and type(value['raw']) is str)
        return 'None' if value is None else '(Some (Document ' + self.words(value['version']) + ' ' + self.words(value['raw']) + '))'

    def record(self, row):
        assert type(row) is dict and all(type(row[key]) is str for key in ['requestId', 'target', 'state', 'content'])
        status = {'pending': 'Pending', 'in_flight': 'InFlight', 'acknowledged': 'Acknowledged', 'refused': 'Refused', 'conflict': 'Conflict', 'unknown': 'Unknown'}[row['state']]
        assert type(row['sequence']) is int and 0 <= row['sequence'] <= 2**53-1
        assert row['sequence'] < 1000  # Bound unary nat emission for this finite fixture domain.
        # Full record, including every own tagged field, is retained in residual.
        return '(JournalRecord ' + ' '.join([self.atom(row['requestId']), self.atom(row['target']), str(row['sequence']), status, self.words(row['content']), self.words(row)]) + ')'

    def records(self, rows):
        return '[' + ';'.join(self.record(row) for row in rows) + ']'

    def metadata(self, rows):
        assert type(rows) is list and all(type(row) is list and len(row) == 2 and type(row[0]) is str for row in rows)
        return '[' + ';'.join('(' + self.atom(key) + ',' + self.metadata_value(value) + ')' for key, value in rows) + ']'

    def nats(self, values):
        assert type(values) is list and all(type(value) is str for value in values)
        return '[' + ';'.join(self.atom(value) for value in values) + ']'

    def input(self, before, options):
        guard = options['guard']
        assert type(before['target']) is str and type(guard['target']) is str
        assert set(options) <= {'guard', 'requestIds', 'removeMeta'}
        assert set(guard) == {'target', 'document', 'intents', 'meta'}
        assert before['target'] == guard['target'], 'Target mismatch outside the fixed typed projection'
        assert guard['document'] is None or set(guard['document']) == {'version', 'raw'}
        expected_meta = []
        assert type(guard['meta']) is list and type(guard['intents']) is list
        for premise in guard['meta']:
            assert type(premise['key']) is str
            assert set(premise) == {'key', 'expected'}
            expected = premise['expected']
            assert type(expected['present']) is bool
            assert set(expected) == ({'present', 'value'} if expected['present'] else {'present'})
            observation = '(Some ' + self.metadata_value(expected['value']) + ')' if expected['present'] else 'None'
            expected_meta.append('(' + self.atom(premise['key']) + ',' + observation + ')')
        return '(RetirementInput ' + ' '.join([self.atom(guard['target']), self.document(before['document']), self.document(guard['document']),
            self.records([row for row in before['records'] if row['target'] == guard['target']]), self.records(guard['intents']),
            self.metadata(before['metadata']), '[' + ';'.join(expected_meta) + ']', self.nats(options['requestIds']), self.nats(options.get('removeMeta', []))]) + ')'

    def observed(self, snapshot, target):
        assert snapshot['target'] == target, 'Observed target outside projection domain'
        return '(Some (' + self.records([row for row in snapshot['records'] if row['target'] == target]) + ',' + self.metadata(snapshot['metadata']) + ',' + self.document(snapshot['document']) + '))'


HEADER = '''From Stdlib Require Import List.
From Retirement Require Import Kernel Specification.
From Accepted Require Import Proof.
Import ListNotations.
Definition accepted_reference : retirement_correct := retirement_correct_holds.
Print Assumptions accepted_reference.
Definition state_view (result : option retirement_output) :=
  match result with
  | None => None
  | Some o => Some (remaining_records o, remaining_metadata o, unchanged_document o)
  end.
'''


def generate(observations, destination):
    assert [v['name'] for v in observations['variants']] == VARIANTS
    projection = Projection()
    summaries = []
    for variant in observations['variants']:
        assert len(variant['results']) == 28
        source_bytes = 0
        for adapter in ['file', 'indexeddb']:
            lines = [HEADER]
            selected = [case for case in variant['results'] if case['adapter'] == adapter]
            assert len(selected) == 14
            for case in selected:
                before, options, after, reopened = [decode(case[key]) for key in ['before', 'options', 'after', 'reopened']]
                for key, original in [('before', before), ('options', options), ('after', after), ('reopened', reopened)]:
                    assert encode(original) == case[key]
                assert case['outcome'] in ['accepted', 'refused']
                name = adapter + '_' + case['name'].replace('-', '_')
                observed = 'None' if case['outcome'] == 'refused' else projection.observed(after, options['guard']['target'])
                facts = ['state_view (decision ' + projection.input(before, options) + ') = ' + observed,
                         projection.words(after) + ' = ' + projection.words(reopened)]
                foreign = lambda snap: {'document': snap['foreignDocument'], 'records': [row for row in snap['records'] if row['target'] != options['guard']['target']]}
                facts.append(projection.words(foreign(before)) + ' = ' + projection.words(foreign(after)))
                if case['outcome'] == 'refused':
                    facts.append(projection.words(before) + ' = ' + projection.words(after))
                lines.append('Example ' + name + ' :\n  ' + ' /\\\n  '.join(facts) + '.\nProof. vm_compute. repeat split; reflexivity. Qed.\n')
            text = '\n'.join(lines)
            source_bytes += len(text.encode())
            assert source_bytes <= MAX_SOURCE
            (destination / (variant['name'].replace('-', '_') + '_' + adapter + '.v')).write_text(text)
        summaries.append({'variant': variant['name'], 'cases': len(variant['results']), 'source_bytes': source_bytes,
                          'host_violations': [{'case': c['adapter'] + '/' + c['name'], 'violations': c['hostViolations']} for c in variant['results'] if c['hostViolations']]})
    assert len(projection.values) <= 8192, 'Finite projection dictionary exceeds its declared bound'
    assert len(projection.codes) == len(projection.values)
    assert len({json.dumps(x, ensure_ascii=True, separators=(',', ':')) for x in projection.values}) == len(projection.values)
    (destination / 'projection-table.json').write_text(json.dumps({'scope': 'trusted finite injective tagged-value reifier, not JS semantics',
        'entries': [{'code': i+1, 'tagged_value': value} for i, value in enumerate(projection.values)]}, ensure_ascii=True, indent=2) + '\n')
    assert sum(path.stat().st_size for path in destination.glob('*.v')) <= MAX_SOURCE
    return summaries


CONTAINER_CHECK = r'''set -eu
cp -R /input/. /work/
cd /work
rocq --version > /evidence/rocq-version.log 2>&1
for module in Kernel Specification; do
  rocq compile -q -native-compiler no -Q /work/Base Retirement /work/Base/$module.v >> /evidence/reference.log 2>&1
done
rocq compile -q -native-compiler no -Q /work/Base Retirement -Q /work/Reference Accepted /work/Reference/Proof.v >> /evidence/reference.log 2>&1
printf '0\n' > /evidence/reference.exit
set +e
for variant in baseline equivalent guard-bypass allow-unacknowledged overbroad-removal caller-alias; do
  for adapter in file indexeddb; do
    module="${variant//-/_}_$adapter"
    rocq compile -q -native-compiler no -Q /work/Base Retirement -Q /work/Reference Accepted "/work/Cases/$module.v" > "/evidence/$variant-$adapter.log" 2>&1
    printf '%s\n' "$?" > "/evidence/$variant-$adapter.exit"
  done
done
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--evidence-dir', required=True, type=Path)
    parser.add_argument('--json-out', required=True, type=Path)
    parser.add_argument('--node-only', action='store_true')
    args = parser.parse_args()
    evidence = args.evidence_dir.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    report = {'v': 1, 'status': 'failed', 'scope': 'actual adapter testing and kernel-checked finite observations only',
              'universal_typescript_proof': False, 'native_rocq_run': False, 'commands': []}
    pins = json.loads(PINS.read_text())
    container = 'superbee-production-retirement-' + uuid.uuid4().hex
    start = time.monotonic()
    attempted = False

    def run(label, argv, timeout):
        before = time.monotonic()
        row = {'label': label, 'argv': argv}
        report['commands'].append(row)
        with (evidence / (label + '.log')).open('wb') as stream:
            try:
                row['exit'] = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout, check=False).returncode
            except subprocess.TimeoutExpired:
                row['exit'] = 'timeout'
                raise RuntimeError(label + ' timed out') from None
            finally:
                row['seconds'] = round(time.monotonic()-before, 3)
        return row['exit']

    def interrupted(signum, _frame):
        raise InterruptedError('Signal ' + str(signum))

    handlers = {sig: signal.signal(sig, interrupted) for sig in [signal.SIGINT, signal.SIGTERM]}
    try:
        for file, expected in pins['reference_files'].items():
            assert sha(ROOT/file) == expected, 'Proved reference source drift'
        report.update(product_revision=pins['product_revision'], reference_files=pins['reference_files'], checker=pins['checker'],
                      harness_sha256={str(p.relative_to(ROOT)): sha(p) for p in [Path(__file__).resolve(), ROOT/'scripts/production_retirement_observations.mjs', PINS]})
        observer = ROOT/'scripts/production_retirement_observations.mjs'
        if run('node-observations', ['node', str(observer), '--source-root', str(args.source_root.resolve()), '--out-dir', str(evidence/'observations')], 300) != 0:
            raise RuntimeError('Actual Node/compiler execution failed, not a semantic mutant kill')
        observations = json.loads((evidence/'observations/observations.json').read_text())
        cases = evidence/'cases'
        cases.mkdir()
        report['variants'] = generate(observations, cases)
        report['node_execution_completed'] = True
        if args.node_only:
            report['status'] = 'observations_ready_unchecked_by_rocq'
        else:
            if run('docker-platform', ['docker', 'version', '--format', '{{.Server.Os}}/{{.Server.Arch}}'], 30) != 0 or (evidence/'docker-platform.log').read_text().strip() != 'linux/amd64':
                raise RuntimeError('Native Linux/amd64 Docker daemon required')
            if run('image-inspect', ['docker', 'image', 'inspect', pins['checker']], 30) != 0:
                raise RuntimeError('Pull the exact pinned public checker before checking')
            with tempfile.TemporaryDirectory(prefix='production-retirement-proof-') as directory:
                inputs = Path(directory)
                for folder in ['Base', 'Reference', 'Cases']:
                    (inputs/folder).mkdir()
                for module in ['Kernel', 'Specification']:
                    shutil.copyfile(ROOT/f'experiments/rocq-retirement/{module}.v', inputs/f'Base/{module}.v')
                shutil.copyfile(ROOT/'experiments/rocq-retirement/Proof.v', inputs/'Reference/Proof.v')
                for case in cases.glob('*.v'):
                    shutil.copyfile(case, inputs/'Cases'/case.name)
                rocq = evidence/'rocq'; rocq.mkdir()
                argv = ['docker','run','--name',container,'--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only',
                        '--cap-drop=ALL','--security-opt=no-new-privileges','--cpus=2','--memory=6g','--memory-swap=6g','--pids-limit=256',
                        '--label','superbee.production-retirement='+os.environ.get('RETIREMENT_RUN_LABEL', container),'--user',f'{os.getuid()}:{os.getgid()}','--tmpfs','/work:rw,nosuid,nodev,noexec,size=4g,mode=1777',
                        '--tmpfs','/tmp:rw,nosuid,nodev,noexec,size=256m,mode=1777','--env','HOME=/tmp',
                        '--mount',f'type=bind,src={inputs},dst=/input,readonly','--mount',f'type=bind,src={rocq},dst=/evidence',
                        pins['checker'],'bash','-c',CONTAINER_CHECK]
                attempted = True
                if run('rocq-container', argv, 900) != 0:
                    raise RuntimeError('Reference/setup failed; no mutant classified as killed')
                assert (rocq/'reference.exit').read_text().strip() == '0'
                report['native_rocq_run'] = True
                for variant in report['variants']:
                    name = variant['variant']
                    variant['rocq_exits'] = {}
                    for adapter in ['file', 'indexeddb']:
                        label = name + '-' + adapter
                        code = int((rocq/(label+'.exit')).read_text())
                        log = (rocq/(label+'.log')).read_text()
                        variant['rocq_exits'][adapter] = code
                        if name in ['baseline','equivalent']:
                            assert code == 0 and log.strip() == 'Closed under the global context', 'Baseline/equivalent equality or assumption audit failed'
                        else:
                            assert code == 1 and 'Unable to unify' in log, 'Mutant failed outside native semantic equality'
                            assert any(v['case'].startswith(adapter+'/') for v in variant['host_violations']), 'No actual observed mutant change'
                            location = re.search(r'line (\d+)', log)
                            assert location, 'No native counterexample location'
                            source = (cases/(name.replace('-', '_')+'_'+adapter+'.v')).read_text().splitlines()
                            prefix = '\n'.join(source[:int(location.group(1))])
                            witnesses = re.findall(r'^Example ([A-Za-z0-9_]+) :', prefix, re.MULTILINE)
                            expected = {'guard-bypass': 'same_version_stale_raw', 'allow-unacknowledged': 'select_pending',
                                        'overbroad-removal': 'multi_reopen', 'caller-alias': 'queued_caller_alias'}[name]
                            assert witnesses and witnesses[-1] == adapter+'_'+expected, 'Mutant failed outside its intended semantic witness'
                            variant.setdefault('native_counterexamples', {})[adapter] = witnesses[-1]
                report['status'] = 'passed_finite_production_qualification'
    except (OSError, ValueError, RuntimeError, AssertionError, InterruptedError) as error:
        report['error'] = str(error)
    finally:
        if attempted:
            try:
                run('cleanup', ['docker','rm','-f',container], 30)
            except (OSError, RuntimeError):
                pass
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
        # A failed observer may leave its private graph copy or dependency link.
        # Remove only fixed children of this newly-created evidence directory.
        for variant in VARIANTS:
            folder = evidence/'observations'/variant
            if folder.is_symlink():
                continue
            dependency = folder/'node_modules'
            if dependency.is_symlink():
                dependency.unlink()
            graph = folder/'dist'
            if graph.is_symlink():
                graph.unlink()
            elif graph.is_dir():
                shutil.rmtree(graph)
        report['seconds'] = round(time.monotonic()-start, 3)
        report['evidence_sha256'] = {str(p.relative_to(evidence)): sha(p) for p in evidence.rglob('*') if p.is_file() and not p.is_symlink()}
        args.json_out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['status','native_rocq_run','universal_typescript_proof']}))
    return 0 if report['status'] in ['observations_ready_unchecked_by_rocq','passed_finite_production_qualification'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
