#!/usr/bin/env python3
"""Source-derived semantic proof experiment; trusted parser/lowering/semantics remain explicit."""
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
ALLOWED = {'propext', 'Quot.sound', 'Classical.choice'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-file', type=Path, required=True)
    parser.add_argument('--json-out', type=Path)
    parser.add_argument('--evidence-dir', type=Path)
    args = parser.parse_args()
    if args.evidence_dir:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
    lean, node = shutil.which('lean'), shutil.which('node')
    if not lean or not node:
        raise SystemExit('Installed pinned Lean and Node required; npm ci in this repository first.')
    version = subprocess.check_output([lean, '--version'], cwd=ROOT, text=True, timeout=60).strip()
    if 'version 4.27.0,' not in version:
        raise SystemExit('Wrong Lean version')
    source = args.source_file.resolve()
    runs, extractions, audits = [], {}, {}
    def run(label, argv, env, expected=0):
        start = time.perf_counter()
        p = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
        if args.evidence_dir:
            (args.evidence_dir / (label + '.log')).write_text(p.stdout + p.stderr)
        runs.append({'name': label, 'exit': p.returncode, 'seconds': round(time.perf_counter() - start, 4)})
        if p.returncode != expected:
            print(p.stdout + p.stderr)
            raise SystemExit(f'{label}: expected {expected}, got {p.returncode}')
        return p.stdout + p.stderr
    with tempfile.TemporaryDirectory(prefix='superbee-source-proof-') as directory:
        work = Path(directory)
        common = work / 'common'
        (common / 'Bridge').mkdir(parents=True)
        env = dict(os.environ, LEAN_PATH=str(common))
        run('semantics', [lean, '-DwarningAsError=true', '-o', str(common / 'Bridge/Semantics.olean'), 'Bridge/Semantics.lean'], env)
        for variant in ['base', 'and-to-or', 'wrong-code']:
            target = work / variant
            run('extract-' + variant, [node, 'scripts/extract_classifier.mjs', str(source), str(target), variant], env)
            receipt = json.loads((target / 'extraction.json').read_text())
            if receipt['nativePolicyDifferences'] != 0 and variant == 'base':
                raise SystemExit('Baseline native function violates independent policy fixtures')
            if receipt['nativePolicyDifferences'] == 0 and variant != 'base':
                raise SystemExit('Semantic mutant did not change policy behavior')
            extractions[variant] = receipt
            variant_env = dict(os.environ, LEAN_PATH=os.pathsep.join([str(target), str(common)]))
            run('generated-' + variant, [lean, '-R', str(target), '-DwarningAsError=true', '-o', str(target / 'SourceGenerated.olean'), str(target / 'SourceGenerated.lean')], variant_env)
            proof = run('universal-policy-' + variant, [lean, '-DwarningAsError=true', 'Bridge/ClassifierProof.lean'], variant_env,
                        expected=0 if variant == 'base' else 1)
            if variant == 'base':
                expected_names = set(re.findall(r'^theorem (\w+)', (ROOT / 'Bridge/ClassifierProof.lean').read_text(), re.M))
                dependencies = re.findall(r"'SourceBridge\.([^']+)' depends on axioms: \[([^\]]*)\]", proof)
                if {name for name, _ in dependencies} != expected_names:
                    raise SystemExit('Incomplete baseline axiom audit: ' + proof)
                for name, values in dependencies:
                    found = {v.strip() for v in values.split(',') if v.strip()}
                    if not found <= ALLOWED:
                        raise SystemExit('Unexpected theorem axiom: ' + values)
                audits = dict(dependencies)
            elif 'Bridge/ClassifierProof.lean:' not in proof or 'error:' not in proof:
                raise SystemExit('Mutation failed outside the intended theorem: ' + proof)
            # Kernel reduction replays every observed native result on the generated AST.
            fixtures = json.loads((target / 'native-fixtures.json').read_text())
            def text(value):
                return '[' + ', '.join(map(str, value)) + ']'
            def input_term(row):
                code = 'none' if row['code'] is None else '(some ' + text(row['code']) + ')'
                return '({ kind := ' + text(row['kind']) + ', code := ' + code + ' } : Input)'
            pairs = ['(' + input_term(row) + ', ' + str(row['actual']).lower() + ')' for row in fixtures]
            replay = target / 'Replay.lean'
            replay.write_text('import SourceGenerated\nopen SourceBridge\nset_option maxRecDepth 4096\nset_option maxHeartbeats 2000000\n' +
                'def samples : List (Input × Bool) := [' + ',\n'.join(pairs) + ']\n' +
                'theorem native_sample_agreement : samples.all (fun pair => eval SourceGenerated.program SourceGenerated.codes pair.1 == pair.2) = true := by decide\n' +
                '#print axioms native_sample_agreement\n')
            replay_result = run('native-replay-' + variant, [lean, '-R', str(target), '-DwarningAsError=true', str(replay)], variant_env)
            if 'sorryAx' in replay_result or 'Lean.ofReduceBool' in replay_result:
                raise SystemExit('Untrusted replay axiom')
            if variant != 'base':
                witness = target / 'Counterexample.lean'
                if variant == 'and-to-or':
                    statement = '''def badInput : Input := { kind := refusedTag, code := some (ascii "OTHER") }
 theorem mutation_breaks_policy : eval SourceGenerated.program SourceGenerated.codes badInput = true ∧ ¬ Policy badInput := by
  constructor
  · decide
  · simpa [Policy, badInput] using (by decide : ascii "OTHER" ∉ policyCodes)
'''
                else:
                    statement = '''def badInput : Input := { kind := refusedTag, code := some (ascii "FORBIDDEN") }
 theorem mutation_breaks_policy : eval SourceGenerated.program SourceGenerated.codes badInput = false ∧ Policy badInput := by
  constructor
  · decide
  · exact ⟨rfl, ascii "FORBIDDEN", rfl, by decide⟩
'''
                witness.write_text('import SourceGenerated\nopen SourceBridge\n' + statement + '\n#print axioms mutation_breaks_policy\n')
                result = run('counterexample-' + variant, [lean, '-R', str(target), '-DwarningAsError=true', str(witness)], variant_env)
                axioms = re.search(r'depends on axioms: \[([^\]]*)\]', result)
                if not axioms or not {v.strip() for v in axioms.group(1).split(',') if v.strip()} <= ALLOWED:
                    raise SystemExit('Unexpected counterexample axiom output: ' + result)
        unsupported = run('reject-unsupported-call', [node, 'scripts/extract_classifier.mjs', str(source), str(work / 'unsupported'), 'unsupported-call'], env, expected=1)
        if 'Unsupported expression' not in unsupported:
            raise SystemExit('Unsupported syntax rejected for wrong reason')
        stale = work / 'stale.ts'
        stale.write_bytes(source.read_bytes() + b'\n// source identity probe\n')
        drift = run('reject-stale-source', [node, 'scripts/extract_classifier.mjs', str(stale), str(work / 'stale')], env, expected=1)
        if 'Source pin mismatch' not in drift:
            raise SystemExit('Stale input rejected for wrong reason')
        generated_bytes = sum(p.stat().st_size for p in work.rglob('*.lean'))
        if args.evidence_dir:
            for variant in ['base', 'and-to-or', 'wrong-code']:
                saved = args.evidence_dir / variant
                saved.mkdir(exist_ok=True)
                for path in (work / variant).iterdir():
                    if path.suffix in ['.lean', '.json', '.ts', '.js']:
                        shutil.copyfile(path, saved / path.name)
    inputs = ['Bridge/Semantics.lean', 'Bridge/ClassifierProof.lean', 'scripts/extract_classifier.mjs',
              'scripts/check_bridge.py', 'package-lock.json', 'lean-toolchain', 'experiments/source-classifier/source-pin.json']
    report = {'status': 'PASS', 'leanVersion': version, 'nodeVersion': subprocess.check_output([node, '--version'], text=True).strip(),
              'checkedInputHashes': {path: sha(ROOT / path) for path in inputs}, 'extractions': extractions,
              'axioms': audits, 'runs': runs, 'totalSeconds': round(sum(r['seconds'] for r in runs), 4),
              'generatedLeanBytesIncludingNativeReplays': generated_bytes,
              'claim': 'source-derived restricted semantic proof; parser/lowering and ECMAScript adequacy trusted; not full shipped-JS or binary proof'}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
