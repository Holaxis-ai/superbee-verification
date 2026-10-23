#!/usr/bin/env python3
"""Kernel-reduced independent decoding of pinned declaration bytes, not full JS verification."""
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-file', type=Path, required=True)
    parser.add_argument('--json-out', type=Path)
    parser.add_argument('--evidence-dir', type=Path)
    args = parser.parse_args()
    lean = shutil.which('lean')
    if not lean:
        raise SystemExit('Pinned Lean must be installed')
    pin = json.loads((ROOT / 'experiments/source-classifier/source-pin.json').read_text())
    source = args.source_file.read_bytes()
    if hashlib.sha256(source).hexdigest() != pin['sha256']:
        raise SystemExit('Independent source pin mismatch')
    spans = pin['declarationByteSpans']
    if len(spans) != 2 or not (0 <= spans[0]['start'] < spans[0]['end'] <= spans[1]['start'] < spans[1]['end'] <= len(source)):
        raise SystemExit('Invalid declaration spans')
    fragments = [source[s['start']:s['end']] for s in spans]
    original = b'\n\n'.join(fragments) + b'\n'
    variants = {'base': original,
                'and-to-or': original.replace(b' && ', b' || ', 1),
                'wrong-code': original.replace(b'"FORBIDDEN"', b'"NOT_FORBIDDEN"', 1)}
    if len(set(variants.values())) != 3:
        raise SystemExit('Controlled byte mutations did not change source')
    if args.evidence_dir:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
    runs, axioms = [], {}
    def run(label, argv, env=None, expected=0):
        start = time.perf_counter()
        p = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
        if args.evidence_dir:
            (args.evidence_dir / (label + '.log')).write_text(p.stdout + p.stderr)
        runs.append({'name': label, 'exit': p.returncode, 'seconds': round(time.perf_counter() - start, 4)})
        if p.returncode != expected:
            raise SystemExit(f'{label}: expected {expected}, got {p.returncode}\n{p.stdout}{p.stderr}')
        return p.stdout + p.stderr
    def audit(label, output, expected_names):
        found = dict(re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", output))
        if set(found) != set(expected_names):
            raise SystemExit('Incomplete axiom audit: ' + label + '\n' + output)
        for values in found.values():
            if not {v.strip() for v in values.split(',') if v.strip()} <= ALLOWED:
                raise SystemExit('Unexpected axiom: ' + values)
        axioms[label] = found
    def bytes_term(value):
        return '[' + ','.join(map(str, value)) + ']'
    def save(path, label):
        if args.evidence_dir:
            shutil.copyfile(path, args.evidence_dir / label)
    with tempfile.TemporaryDirectory(prefix='superbee-decoded-source-') as directory:
        work = Path(directory)
        # Run existing source/native/mutation checks once and retain their exact evidence.
        prior = work / 'prior'
        report_file = work / 'prior.json'
        run('source-bridge-suite', ['python3', 'scripts/check_bridge.py', '--source-file', str(args.source_file.resolve()),
                                  '--json-out', str(report_file), '--evidence-dir', str(prior)])
        prior_report = json.loads(report_file.read_text())
        if args.evidence_dir:
            shutil.copytree(prior, args.evidence_dir / 'source-bridge', dirs_exist_ok=True)
            save(report_file, 'source-bridge-result.json')
        common = work / 'common'
        (common / 'Bridge').mkdir(parents=True)
        env = dict(os.environ, LEAN_PATH=str(common))
        for name in ['Semantics', 'SourceDecode']:
            run('compile-' + name, [lean, '-DwarningAsError=true', '-o', str(common / f'Bridge/{name}.olean'), f'Bridge/{name}.lean'], env)
        certificate = '''import SourceGenerated
import Bridge.SourceDecode
set_option maxRecDepth 16384
set_option maxHeartbeats 8000000
def declarationBytes : List Nat := BYTES
theorem source_decodes : SourceBridge.decode declarationBytes = some (SourceGenerated.program, SourceGenerated.codes) := by decide +kernel
#print axioms source_decodes
'''
        for variant, raw in variants.items():
            target = prior / variant
            if (target / 'source-function.ts').read_bytes() != raw:
                raise SystemExit('Independent byte spans disagree with extracted declarations: ' + variant)
            variant_env = dict(os.environ, LEAN_PATH=os.pathsep.join([str(target), str(common)]))
            generated = target / 'SourceGenerated.lean'
            run('compile-generated-' + variant, [lean, '-R', str(target), '-o', str(target / 'SourceGenerated.olean'), str(generated)], variant_env)
            cert = target / 'SourceBytes.lean'
            cert.write_text(certificate.replace('BYTES', bytes_term(raw)))
            output = run('decode-' + variant, [lean, '-R', str(target), '-DwarningAsError=true', '-o', str(target / 'SourceBytes.olean'), str(cert)], variant_env)
            audit('decode-' + variant, output, ['source_decodes'])
            save(cert, 'SourceBytes-' + variant + '.lean')
            if variant == 'base':
                proof = target / 'ClassifierProof.lean'
                shutil.copyfile(ROOT / 'Bridge/ClassifierProof.lean', proof)
                run('compile-policy', [lean, '-R', str(target), '-DwarningAsError=true', '-o', str(target / 'ClassifierProof.olean'), str(proof)], variant_env)
                linked = target / 'DecodedPolicy.lean'
                linked.write_text('''import SourceBytes
import ClassifierProof
open SourceBridge
theorem decoded_source_policy (program : Expr) (codes : List Text)
    (decoded : decode declarationBytes = some (program, codes)) (input : Input) :
    eval program codes input = true ↔ Policy input := by
  rw [source_decodes] at decoded
  cases Option.some.inj decoded
  exact source_classifier_exact input
#print axioms decoded_source_policy
''')
                output = run('decoded-policy', [lean, '-R', str(target), '-DwarningAsError=true', str(linked)], variant_env)
                audit('decoded-policy', output, ['decoded_source_policy'])
                save(linked, 'DecodedPolicy.lean')
        base_generated = (prior / 'base/SourceGenerated.lean').read_text()
        corruptions = {
            'program': re.sub(r'def program : SourceBridge.Expr := .*', 'def program : SourceBridge.Expr := .literal false', base_generated),
            'encoding': base_generated.replace('[114, 101, 102, 117, 115, 101, 100]', '[115, 101, 102, 117, 115, 101, 100]', 1),
            'codes': base_generated.replace('[65, 85, 84, 72, 95, 82, 69, 81, 85, 73, 82, 69, 68]', '[66, 85, 84, 72, 95, 82, 69, 81, 85, 73, 82, 69, 68]', 1),
        }
        for label, corrupted in corruptions.items():
            if corrupted == base_generated:
                raise SystemExit('Corruption did not change generated input: ' + label)
            target = work / ('corrupt-' + label)
            target.mkdir()
            generated = target / 'SourceGenerated.lean'
            generated.write_text(corrupted)
            probe_env = dict(os.environ, LEAN_PATH=os.pathsep.join([str(target), str(common)]))
            run('compile-corrupt-' + label, [lean, '-R', str(target), '-o', str(target / 'SourceGenerated.olean'), str(generated)], probe_env)
            cert = target / 'SourceBytes.lean'
            cert.write_text(certificate.replace('BYTES', bytes_term(original)))
            output = run('reject-corrupt-' + label, [lean, '-R', str(target), '-DwarningAsError=true', str(cert)], probe_env, expected=1)
            if 'error:' not in output or 'source_decodes' not in output:
                raise SystemExit('Corrupted certificate failed outside intended check: ' + label)
            save(generated, 'CorruptGenerated-' + label + '.lean')
        rejected = {
            'return-newline': original.replace(b'return outcome', b'return \n outcome', 1),
            'extra-statement': original.replace(b'return outcome.kind', b'false; return outcome.kind', 1),
            'optional-field': original.replace(b'outcome.kind', b'outcome?.kind', 1),
            'default-parameter': original.replace(b'outcome: Outcome | RecordedWriteOutcome', b'outcome: Outcome | RecordedWriteOutcome = fallback', 1),
            'extra-call': original.replace(b'outcome.kind === "refused"', b'console.log("refused")', 1),
            'escaped-literal': original.replace(b'"refused"', b'"re\\x66used"', 1),
            'trailing-declaration': original + b'export const unexpected = true;',
        }
        target = work / 'rejections'
        target.mkdir()
        probe = target / 'Rejections.lean'
        declarations = ['import Bridge.SourceDecode', 'set_option maxRecDepth 16384', 'set_option maxHeartbeats 8000000']
        for i, (label, raw) in enumerate(rejected.items()):
            if raw == original:
                raise SystemExit('Rejection probe unchanged: ' + label)
            declarations.append(f'theorem rejected_{i} : SourceBridge.decode {bytes_term(raw)} = none := by decide +kernel')
            declarations.append(f'#print axioms rejected_{i}')
        probe.write_text('\n'.join(declarations) + '\n')
        output = run('reject-unsupported-bytes', [lean, '-R', str(target), '-DwarningAsError=true', str(probe)], env)
        audit('rejections', output, [f'rejected_{i}' for i in range(len(rejected))])
        save(probe, 'Rejections.lean')
    inputs = ['Bridge/Semantics.lean', 'Bridge/SourceDecode.lean', 'Bridge/ClassifierProof.lean',
              'scripts/check_source_decode.py', 'scripts/check_bridge.py', 'scripts/extract_classifier.mjs',
              'experiments/source-classifier/source-pin.json', 'package-lock.json', 'lean-toolchain']
    report = {'status': 'PASS', 'sourceByteSpans': spans, 'sourceSha256': pin['sha256'],
              'declarationSha256': hashlib.sha256(original).hexdigest(),
              'checkedInputHashes': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in inputs},
              'axioms': axioms, 'runs': runs, 'totalSeconds': round(sum(r['seconds'] for r in runs), 4),
              'sourceBridgeSeconds': prior_report['totalSeconds'], 'rejectedByteProbes': list(rejected),
              'claim': 'kernel-checked restricted-source decoding and policy; grammar/ECMAScript adequacy, acquisition/context and runtime remain trusted'}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
