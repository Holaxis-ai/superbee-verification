#!/usr/bin/env python3
"""Clean, bounded proof check using an installed pinned Lean toolchain; no proof cache."""
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

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / 'Journal/Retirement.lean'
ALLOWED = {'propext', 'Quot.sound', 'Classical.choice'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json-out', type=Path)
    args = parser.parse_args()
    lean = shutil.which('lean')
    if not lean:
        raise SystemExit('Install elan and the version in lean-toolchain first.')
    version = subprocess.check_output([lean, '--version'], cwd=ROOT, text=True, timeout=60).strip()
    if 'version 4.27.0,' not in version:
        raise SystemExit('Wrong Lean version: ' + version)
    text = PROOF.read_text()
    names = re.findall(r'^theorem ([A-Za-z_][A-Za-z0-9_\']*)', text, re.M)
    if len(names) < 6:
        raise SystemExit('Expected preservation, sequence, validity and witness/control theorems.')
    runs = []
    def run(label, argv, env, expected=0):
        started = time.perf_counter()
        p = subprocess.run(argv, cwd=ROOT, env=env, text=True, capture_output=True, timeout=60)
        runs.append({'name': label, 'exit': p.returncode, 'seconds': round(time.perf_counter() - started, 4)})
        if p.returncode != expected:
            print(p.stdout + p.stderr)
            raise SystemExit(f'{label}: expected exit {expected}, got {p.returncode}')
        return p.stdout + p.stderr
    with tempfile.TemporaryDirectory(prefix='superbee-proof-') as tmp:
        build = Path(tmp)
        (build / 'Journal').mkdir()
        env = dict(os.environ, LEAN_PATH=str(build))
        run('compile-clean', [lean, '-DwarningAsError=true', '-o', str(build / 'Journal/Retirement.olean'), str(PROOF)], env)
        audit = build / 'Audit.lean'
        audit.write_text('import Journal.Retirement\n' + '\n'.join('#print axioms SuperbeeVerification.' + name for name in names) + '\n')
        output = run('audit-axioms', [lean, '-DwarningAsError=true', str(audit)], env)
        dependencies = re.findall(r"'SuperbeeVerification\.([^']+)' depends on axioms: \[([^\]]*)\]", output)
        if {name for name, _ in dependencies} != set(names):
            raise SystemExit('Incomplete axiom audit: ' + output)
        for name, axioms in dependencies:
            found = {value.strip() for value in axioms.split(',') if value.strip()}
            if not found <= ALLOWED:
                raise SystemExit(f'{name}: unexpected axioms {found - ALLOWED}')
        negative = build / 'MustReject.lean'
        negative.write_text('import Journal.Retirement\nopen SuperbeeVerification\nexample : Preserved (retire witness [1]) := by\n  simp [Preserved, retire, witness]\n')
        rejected = run('reject-false-preservation', [lean, '-DwarningAsError=true', str(negative)], env, expected=1)
        if 'unsolved goals' not in rejected or 'False' not in rejected:
            raise SystemExit('Negative control failed for an unexpected reason: ' + rejected)
    report = {'status': 'PASS', 'toolchain': (ROOT / 'lean-toolchain').read_text().strip(), 'leanVersion': version,
              'proofSha256': hashlib.sha256(PROOF.read_bytes()).hexdigest(), 'proofLines': len(text.splitlines()),
              'proofBytes': PROOF.stat().st_size, 'theorems': names, 'axioms': {n: a for n, a in dependencies},
              'runs': runs, 'totalCheckSeconds': round(sum(row['seconds'] for row in runs), 4),
              'scope': 'abstract atomic retirement only; not a TypeScript refinement proof; no product CI changes'}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
