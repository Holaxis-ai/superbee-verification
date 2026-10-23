#!/usr/bin/env python3
"""Verify exact safe-retry source contracts under the existing Gillian ES5 model."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

from gillian_runtime import checked_toolchain, sha

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-file', type=Path, required=True)
    parser.add_argument('--tool-dir', type=Path, required=True)
    parser.add_argument('--json-out', type=Path)
    parser.add_argument('--evidence-dir', type=Path)
    args = parser.parse_args()
    if args.evidence_dir:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
    tool_pin = ROOT / 'experiments/gillian-settlement/toolchain.json'
    receipt, executables, env = checked_toolchain(args.tool_dir, tool_pin)
    node = shutil.which('node')
    if not node:
        raise SystemExit('Pinned Node must be installed')
    experiment = ROOT / 'experiments/gillian-retry'
    contract = (experiment / 'contract.js').read_text()
    plan = json.loads((experiment / 'cases.json').read_text())
    count = plan['caseCount']
    if count != len(plan['cases']) or contract.count('@pre ') != count or contract.count('@post ') != count or '@onlyspec' in contract:
        raise SystemExit('Contract/case plan mismatch')
    runs, verdicts = [], {}
    def run(label, argv, cwd, expected=0):
        start = time.perf_counter()
        result = subprocess.run(argv, cwd=cwd, env=env, text=True, capture_output=True, timeout=60)
        output = result.stdout + result.stderr
        if args.evidence_dir:
            (args.evidence_dir / (label + '.log')).write_text(output)
        runs.append({'name': label, 'exit': result.returncode, 'seconds': round(time.perf_counter() - start, 4)})
        if result.returncode != expected:
            raise SystemExit(f'{label}: expected {expected}, got {result.returncode}\n{output}')
        return output
    z3_version = run('z3-version', [str(executables['z3']), '--version'], ROOT).strip()
    if not z3_version.startswith('Z3 version 4.16.0 '):
        raise SystemExit('Wrong Z3 version')
    with tempfile.TemporaryDirectory(prefix='superbee-safe-retry-') as directory:
        work = Path(directory)
        run('prepare', [node, str(ROOT / 'scripts/prepare_retry.mjs'), str(args.source_file.resolve()), str(work)], ROOT)
        preparation = json.loads((work / 'preparation.json').read_text())
        for variant_plan in plan['variants']:
            variant, expected_failed = variant_plan['name'], set(variant_plan['failedCases'])
            if not expected_failed <= set(range(count)):
                raise SystemExit('Invalid expected case identity')
            target = work / variant
            subject = (target / 'subject.js').read_text()
            marker = 'function ' + plan['procedure']
            if subject.count(marker) != 1:
                raise SystemExit('Unexpected complete emitted subject')
            annotated = target / 'verify.js'
            annotated.write_text(subject.replace(marker, contract + '\n' + marker, 1))
            results = target / 'results'
            output = run('verify-' + variant, [str(executables['gillian']), 'verify', str(annotated), '-l', 'disabled',
                         '--result-dir', str(results)], target, expected=1 if expected_failed else 0)
            if args.evidence_dir:
                shutil.copytree(target, args.evidence_dir / variant, dirs_exist_ok=True)
            records = json.loads((results / 'verif_results.json').read_text())
            actual = {}
            for entry in records:
                (procedure, (case, path)), passed = entry
                if procedure != plan['procedure'] or type(case) is not int or type(path) is not int or type(passed) is not bool or case not in range(count):
                    raise SystemExit('Unexpected structured verdict identity: ' + repr(entry))
                actual[case] = actual.get(case, True) and passed
            failed = {case for case, passed in actual.items() if not passed}
            statuses = re.findall(r'^Verifying one spec of procedure ' + re.escape(plan['procedure']) + r'\.\.\. [sf ]*(Success|Failure)$', output, re.M)
            success_lines, failure_lines = statuses.count('Success'), statuses.count('Failure')
            if set(actual) != set(range(count)) or failed != expected_failed or success_lines != count - len(failed) or failure_lines != len(failed):
                raise SystemExit('Wrong/incomplete structured specification verdicts: ' + variant + '\n' + output)
            if expected_failed:
                if 'Analysis failures!' not in output:
                    raise SystemExit('Missing analysis-failure diagnostics: ' + variant)
                errors = re.findall(r'^\d+\. (.+)$', output.split('Analysis failures!', 1)[1], re.M)
                if len(errors) < len(failed) or any(error != "Couldn't satisfy postcondition" for error in errors):
                    raise SystemExit('Mutant failed outside intended postconditions: ' + variant + '\n' + output)
            elif 'All specs succeeded:' not in output:
                raise SystemExit('Missing successful verification summary: ' + variant)
            verdicts[variant] = {'analyzedCases': len(actual), 'verifiedCases': count - len(failed),
                'failedCases': sorted(failed), 'failedCaseNames': [plan['cases'][i]['name'] for i in sorted(failed)],
                'postconditionFailurePaths': len(errors) if expected_failed else 0,
                'annotatedSha256': sha(annotated)}
        stale = work / 'stale.ts'
        stale.write_bytes(args.source_file.read_bytes() + b'\n// changed source identity\n')
        drift = run('reject-source-drift', [node, str(ROOT / 'scripts/prepare_retry.mjs'), str(stale), str(work / 'stale')], ROOT, expected=1)
        if 'Source pin mismatch' not in drift:
            raise SystemExit('Drift rejected for unrelated reason')
        # A receipt cannot authorize a different executable while retaining the reviewed archive pin.
        forged_dir = work / 'forged-tools'
        forged_dir.mkdir()
        forged = dict(receipt)
        fake = forged_dir / 'fake-gillian'
        fake.write_text('fake executable bytes, never invoked\n')
        forged['gillian'], forged['gillianSha256'] = str(fake), sha(fake)
        for archive in receipt['archives']:
            source = args.tool_dir / Path(archive['archive']).name
            os.symlink(source.resolve(), forged_dir / source.name)
        (forged_dir / 'receipt.json').write_text(json.dumps(forged))
        try:
            checked_toolchain(forged_dir, tool_pin)
        except SystemExit as error:
            if str(error) != 'Executable differs from pinned archive: gillian':
                raise
            tamper_control = str(error)
        else:
            raise SystemExit('Forged tool receipt was accepted')
        if args.evidence_dir:
            for variant in preparation['variants']:
                shutil.copytree(work / variant, args.evidence_dir / variant, dirs_exist_ok=True)
            shutil.copyfile(work / 'preparation.json', args.evidence_dir / 'preparation.json')
            (args.evidence_dir / 'tool-tamper-control.json').write_text(json.dumps({'rejected': tamper_control, 'fakeInvoked': False}) + '\n')
    inputs = ['scripts/check_retry.py', 'scripts/prepare_retry.mjs', 'scripts/gillian_runtime.py', 'scripts/setup_gillian.py',
              'experiments/gillian-retry/source-pin.json', 'experiments/gillian-retry/contract.js', 'experiments/gillian-retry/cases.json',
              'experiments/gillian-settlement/toolchain.json', 'package-lock.json']
    report = {'status': 'PASS', 'verdicts': verdicts, 'preparation': preparation, 'toolReceipt': receipt,
              'checkedInputHashes': {path: sha(ROOT / path) for path in inputs}, 'z3Version': z3_version,
              'nodeVersion': subprocess.check_output([node, '--version'], text=True).strip(),
              'runs': runs, 'totalSeconds': round(sum(run['seconds'] for run in runs), 4),
              'toolTamperRejected': tamper_control,
              'claim': 'Gillian symbolic verification of complete isolated emitted retry guard on bounded-real field projections covering safe integer inputs, with explicit optional-field and descriptor/prototype domains; compiler/model/solver/runtime and evidence/caller/atomicity assumptions remain'}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
