#!/usr/bin/env python3
"""Established-tool symbolic verification of an exact type-erased pure function."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from gillian_runtime import checked_toolchain
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-file', type=Path, required=True)
    parser.add_argument('--tool-dir', type=Path, required=True)
    parser.add_argument('--json-out', type=Path)
    parser.add_argument('--evidence-dir', type=Path)
    args = parser.parse_args()
    if args.evidence_dir:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
    pin_path = ROOT / 'experiments/gillian-settlement/toolchain.json'
    receipt, executables, env = checked_toolchain(args.tool_dir, pin_path)
    node = shutil.which('node')
    if not node:
        raise SystemExit('Pinned Node must be installed')
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
        raise SystemExit('Wrong Z3 version: ' + z3_version)
    contract_path = ROOT / 'experiments/gillian-settlement/contract.js'
    contract = contract_path.read_text()
    if contract.count('@pre ') != 4 or contract.count('@post ') != 4 or '@onlyspec' in contract:
        raise SystemExit('Expected four executable verification contracts')
    with tempfile.TemporaryDirectory(prefix='superbee-gillian-settlement-') as directory:
        work = Path(directory)
        run('prepare', [node, str(ROOT / 'scripts/prepare_settlement.mjs'), str(args.source_file.resolve()), str(work)], ROOT)
        preparation = json.loads((work / 'preparation.json').read_text())
        for variant, expected_failures in [('base', 0), ('wrong-comparison', 2), ('wrong-version', 1), ('unconditional-promotion', 3), ('equivalent-null-check', 0)]:
            target = work / variant
            subject = (target / 'subject.js').read_text()
            if subject.count('function settleAgainstIntent') != 1:
                raise SystemExit('Unexpected emitted subject')
            annotated = target / 'verify.js'
            annotated.write_text(subject.replace('function settleAgainstIntent', contract + '\nfunction settleAgainstIntent', 1))
            output = run('verify-' + variant, [str(executables['gillian']), 'verify', str(annotated), '-l', 'disabled',
                         '--result-dir', str(target / 'results')], target, expected=1 if expected_failures else 0)
            successes = len(re.findall(r'Verifying one spec of procedure settleAgainstIntent\.\.\. s Success', output))
            failures = len(re.findall(r'Verifying one spec of procedure settleAgainstIntent\.\.\. f Failure', output))
            if 'Obtained 4 symbolic tests in total' not in output or successes + failures != 4 or failures != expected_failures:
                raise SystemExit('Incomplete or unexpected verification result: ' + variant + '\n' + output)
            if expected_failures:
                if output.count("Couldn't satisfy postcondition") != expected_failures:
                    raise SystemExit('Mutant failed outside intended postconditions: ' + variant + '\n' + output)
            elif 'All specs succeeded:' not in output:
                raise SystemExit('Missing successful analysis summary: ' + variant)
            verdicts[variant] = {'verifiedCases': successes, 'postconditionFailures': failures,
                                 'annotatedSha256': sha(annotated)}
        # A stale source cannot silently be assessed against the pinned contract.
        stale = work / 'stale.ts'
        stale.write_bytes(args.source_file.read_bytes() + b'\n// changed source identity\n')
        output = run('reject-source-drift', [node, str(ROOT / 'scripts/prepare_settlement.mjs'), str(stale), str(work / 'stale')], ROOT, expected=1)
        if 'Source pin mismatch' not in output:
            raise SystemExit('Drift rejection failed for an unrelated reason')
        if args.evidence_dir:
            for variant in preparation['variants']:
                shutil.copytree(work / variant, args.evidence_dir / variant, dirs_exist_ok=True)
            shutil.copyfile(work / 'preparation.json', args.evidence_dir / 'preparation.json')
    inputs = ['scripts/check_settlement.py', 'scripts/prepare_settlement.mjs', 'scripts/setup_gillian.py',
              'experiments/gillian-settlement/contract.js', 'experiments/gillian-settlement/source-pin.json',
              'experiments/gillian-settlement/toolchain.json', 'scripts/gillian_runtime.py', 'package-lock.json']
    report = {'status': 'PASS', 'verdicts': verdicts, 'preparation': preparation, 'toolReceipt': receipt,
              'z3Version': z3_version, 'nodeVersion': subprocess.check_output([node, '--version'], text=True).strip(),
              'checkedInputHashes': {path: sha(ROOT / path) for path in inputs},
              'runs': runs, 'totalSeconds': round(sum(run['seconds'] for run in runs), 4),
              'claim': 'Gillian separation-logic symbolic verification of the isolated emitted ES5 function for distinct extensible standard-prototype records with writable/enumerable/configurable owned data fields; trusted TypeScript/Gillian/ES5/solver/string/runtime boundary, not Lean-kernel or binary verification'}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
