#!/usr/bin/env python3
"""One bounded candidate/checker attempt against frozen executable Rocq source."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'experiments/rocq-work-cycle/contract.json'
IMAGE = 'ghcr.io/theorem-labs/oss-fuzz-theorems-checker@sha256:cc9ae43a9f4b0dd59d7c8d30727d36e039bfe72a2a9f9c4a99c68e413037e902'
# This is runner-owned code, not candidate-editable proof or theorem text.
CHECK = r'''set -u
ulimit -f 32768
cp -R /input/. /work/
cd /work
rocq --version > /evidence/versions.log 2>&1
code=$?; printf '%s\n' "$code" > /evidence/setup.exit
[ "$code" = 0 ] || exit "$code"
for module in Kernel Specification; do
  rocq compile -q -native-compiler no -Q /work/Base Retirement /work/Base/$module.v >> /evidence/base.log 2>&1
  code=$?; [ "$code" = 0 ] || break
done
printf '%s\n' "$code" > /evidence/base.exit
[ "$code" = 0 ] || exit "$code"
rocq compile -q -native-compiler no -Q /work/Base Retirement -Q /work/Candidate Candidate /work/Candidate/Proof.v > /evidence/candidate.log 2>&1
code=$?; printf '%s\n' "$code" > /evidence/candidate.exit
[ "$code" = 0 ] || exit "$code"
for source in Base/Kernel.v Base/Specification.v Wrapper.v; do
  cmp -s "/input/$source" "/work/$source" || exit 91
done
rocq compile -q -native-compiler no -Q /work/Base Retirement -Q /work/Candidate Candidate /work/Wrapper.v > /evidence/wrapper.log 2>&1
code=$?; printf '%s\n' "$code" > /evidence/wrapper.exit
exit "$code"
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ordinary_bytes(path, limit=262144):
    if path.is_symlink():
        raise ValueError('Symlink input refused')
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
        raise ValueError('Input must be a bounded ordinary single-link file')
    return path.read_bytes()


def atomic_json(path, data):
    temporary = path.with_name(path.name + '.pending')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--json-out', type=Path, required=True)
    parser.add_argument('--container-name', default='superbee-rocq-cycle-' + uuid.uuid4().hex)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'superbee-rocq-cycle-[A-Za-z0-9-]+', args.container_name):
        parser.error('Invalid unique container name')
    report = {'v': 1, 'status': 'error', 'scope': 'typed executable Rocq retirement source only',
              'native_checks_run': False, 'substantial_component_milestone': False,
              'commands': [], 'checker': IMAGE}
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_root.mkdir(parents=True, exist_ok=True)
    attempted = False
    evidence = None
    row = None
    ledger = None
    started = time.monotonic()
    lock = None

    def command(label, argv, timeout):
        item = {'label': label, 'argv': argv}
        report['commands'].append(item)
        before = time.monotonic()
        with (evidence / (label + '.log')).open('wb') as output:
            try:
                result = subprocess.run(argv, stdout=output, stderr=subprocess.STDOUT,
                                        timeout=timeout, check=False)
                item['exit'] = result.returncode
            except subprocess.TimeoutExpired:
                item['exit'] = 'timeout'
                raise RuntimeError(label + ' timed out') from None
            finally:
                item['seconds'] = round(time.monotonic() - before, 3)
        return item['exit']

    def interrupted(signum, _frame):
        raise InterruptedError('Interrupted by signal ' + str(signum))

    previous = {s: signal.signal(s, interrupted) for s in (signal.SIGTERM, signal.SIGINT)}
    try:
        contract_bytes = ordinary_bytes(CONTRACT)
        contract = json.loads(contract_bytes)
        if (contract['v'] != 1 or contract['checker'] != IMAGE or contract['allowed_axioms'] != []
                or contract['limits'] != {'max_attempts': 3, 'total_seconds': 900, 'attempt_seconds': 240}
                or set(contract['frozen_sources']) != {'Kernel.v', 'Specification.v'}
                or contract['additional_theorems'] != [
                    {'type': 'Retirement.Specification.refuse_all_incorrect', 'theorem': 'refuse_all_fails'},
                    {'type': 'Retirement.Specification.drop_all_incorrect', 'theorem': 'drop_all_fails'}]):
            raise ValueError('Unsupported frozen contract')
        # Fully-qualified identifiers only; never interpolate caller-controlled Rocq source.
        if not re.fullmatch(r'Retirement\.Specification\.[A-Za-z][A-Za-z0-9_]*', contract['theorem_type']):
            raise ValueError('Invalid frozen theorem type')
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', contract['candidate_theorem']):
            raise ValueError('Invalid frozen candidate theorem')
        frozen = {}
        for name, expected in contract['frozen_sources'].items():
            data = ordinary_bytes(ROOT / 'experiments/rocq-retirement' / name)
            if digest(data) != expected:
                raise ValueError('Frozen source identity mismatch: ' + name)
            frozen[name] = data
        candidate = ordinary_bytes(args.candidate.absolute())
        report.update(contract_sha256=digest(contract_bytes), frozen_source_sha256=contract['frozen_sources'],
                      candidate_sha256=digest(candidate), theorem_type=contract['theorem_type'])
        if args.validate_only:
            report['status'] = 'inputs_validated_only'
        else:
            # The local ledger is trusted coordinator state, not a tamper-proof audit service.
            lock = args.ledger.with_name(args.ledger.name + '.lock').open('a+')
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            ledger = json.loads(args.ledger.read_text()) if args.ledger.exists() else {
                'v': 1, 'contract_sha256': report['contract_sha256'], 'attempts': []}
            if (ledger.get('v') != 1 or ledger.get('contract_sha256') != report['contract_sha256']
                    or not isinstance(ledger.get('attempts'), list)):
                raise ValueError('Ledger belongs to another frozen contract')
            limits = contract['limits']
            spent = sum(a['charged_seconds'] for a in ledger['attempts'])
            if len(ledger['attempts']) >= limits['max_attempts'] or spent >= limits['total_seconds']:
                raise RuntimeError('Attempt or wall-time budget exhausted')
            deadline = min(limits['attempt_seconds'], limits['total_seconds'] - spent)
            attempt_number = len(ledger['attempts']) + 1
            evidence = args.evidence_root.resolve() / ('attempt-%03d' % attempt_number)
            evidence.mkdir(exist_ok=False)
            report.update(attempt=attempt_number, evidence_directory=str(evidence))
            (evidence / 'contract.json').write_bytes(contract_bytes)
            (evidence / 'candidate.v').write_bytes(candidate)
            row = {'attempt': attempt_number, 'candidate_sha256': digest(candidate), 'status': 'running',
                   'charged_seconds': deadline, 'evidence_directory': str(evidence)}
            ledger['attempts'].append(row)
            # Reserve worst-case cost before execution: interrupted/lost attempts remain charged.
            atomic_json(args.ledger, ledger)
            forbidden = bool(re.search(r'\b(Admitted|Axioms?|Parameters?|admit)\b', candidate.decode('utf-8')))
            if command('daemon-platform', ['docker', 'version', '--format', '{{.Server.Os}}/{{.Server.Arch}}'], 15) != 0 or (evidence / 'daemon-platform.log').read_text().strip() != 'linux/amd64':
                raise RuntimeError('Native Linux/amd64 Docker daemon required')
            if command('image-inspect', ['docker', 'image', 'inspect', IMAGE], 15) != 0:
                raise RuntimeError('Pull the exact pinned checker separately')
            with tempfile.TemporaryDirectory(prefix='superbee-rocq-cycle-') as temp:
                subset = Path(temp)
                (subset / 'Base').mkdir()
                (subset / 'Candidate').mkdir()
                for name, data in frozen.items():
                    (subset / 'Base' / name).write_bytes(data)
                (subset / 'Candidate/Proof.v').write_bytes(candidate)
                wrapper = ('From Retirement Require Import Specification.\n'
                           'From Candidate Require Import Proof.\n'
                           'Definition certified : ' + contract['theorem_type'] + ' := Candidate.Proof.' + contract['candidate_theorem'] + '.\n'
                           'Definition certified_refuse_all : Retirement.Specification.refuse_all_incorrect := Candidate.Proof.refuse_all_fails.\n'
                           'Definition certified_drop_all : Retirement.Specification.drop_all_incorrect := Candidate.Proof.drop_all_fails.\n'
                           'Set Printing Fully Qualified.\nPrint Assumptions certified.\n'
                           'Print Assumptions certified_refuse_all.\nPrint Assumptions certified_drop_all.\n')
                (subset / 'Wrapper.v').write_text(wrapper)
                (evidence / 'Wrapper.v').write_text(wrapper)
                # Ordinary .v source only, never caller-supplied compiled libraries.
                argv = ['docker', 'run', '--name', args.container_name, '--rm', '--pull=never',
                        '--platform', 'linux/amd64', '--network=none', '--read-only', '--cap-drop=ALL',
                        '--security-opt=no-new-privileges', '--cpus=2', '--memory=6g', '--memory-swap=6g',
                        '--pids-limit=256', '--user', str(os.getuid()) + ':' + str(os.getgid()),
                        '--tmpfs', '/work:rw,nosuid,nodev,noexec,size=1g,mode=1777',
                        '--tmpfs', '/tmp:rw,nosuid,nodev,noexec,size=128m,mode=1777',
                        '--mount', 'type=bind,src=' + str(subset) + ',dst=/input,readonly',
                        '--mount', 'type=bind,src=' + str(evidence) + ',dst=/evidence',
                        '--env', 'HOME=/tmp', '--workdir', '/work', IMAGE, 'bash', '-c', CHECK]
                attempted = True
                remaining = deadline - (time.monotonic() - started) - 15  # reserve cleanup time
                if remaining <= 0:
                    raise RuntimeError('Attempt wall-time budget exhausted before checker')
                code = command('container', argv, remaining)
            for stage in ['setup', 'base', 'candidate', 'wrapper']:
                path = evidence / (stage + '.exit')
                report[stage + '_exit'] = int(path.read_text()) if path.exists() else None
            report['native_checks_run'] = report['candidate_exit'] is not None
            if report['setup_exit'] != 0 or report['base_exit'] != 0:
                raise RuntimeError('Native tool setup or frozen base failed')
            if report['candidate_exit'] is None:
                raise RuntimeError('Missing candidate exit record')
            if report['candidate_exit'] != 0:
                report['status'] = 'needs_revision'
            elif report['wrapper_exit'] is None:
                raise RuntimeError('Missing trusted-wrapper exit record')
            elif report['wrapper_exit'] != 0:
                report['status'] = 'rejected'
                report['diagnostic'] = 'Candidate does not satisfy the frozen statement'
            elif code != 0:
                raise RuntimeError('Container failed despite successful checker markers')
            else:
                assumptions = (evidence / 'wrapper.log').read_text().strip()
                if forbidden or assumptions.splitlines() != ['Closed under the global context'] * 3:
                    report['status'] = 'rejected'
                    report['diagnostic'] = 'Candidate admission token or assumption audit is not exactly closed under the global context'
                else:
                    report['status'] = 'accepted'
                    report['assumptions'] = []
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, InterruptedError) as error:
        report['status'] = 'error'
        report['diagnostic'] = str(error)
    finally:
        if attempted:
            try:
                report['cleanup_exit'] = command('cleanup', ['docker', 'rm', '-f', args.container_name], 15)
            except (OSError, RuntimeError):
                report['cleanup_exit'] = 'failed'
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        report['seconds'] = round(time.monotonic() - started, 3)
        if row is not None:
            row.update(status=report['status'], charged_seconds=report['seconds'])
            atomic_json(args.ledger, ledger)
        if evidence is not None:
            report['evidence_sha256'] = {str(f.relative_to(evidence)): digest(f.read_bytes())
                                         for f in sorted(evidence.rglob('*')) if f.is_file()}
            atomic_json(evidence / 'result.json', report)
        atomic_json(args.json_out, report)
        if lock is not None:
            lock.close()
    print(json.dumps({k: report[k] for k in ['status', 'native_checks_run', 'substantial_component_milestone']}))
    return 0 if report['status'] in ['accepted', 'inputs_validated_only'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
