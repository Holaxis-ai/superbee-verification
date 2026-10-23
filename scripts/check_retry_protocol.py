#!/usr/bin/env python3
"""Run actual pinned TLC over the bounded protocol and exact negative controls."""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / 'experiments/retry-protocol'
TLC_SHA = '936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88'
RUNS = {'safe': None, 'guard-only': None, 'stale-claim': 'Invariant NoUnsafeClaim is violated.',
        'absence-evidence': 'Invariant PrefixSound is violated.',
        'foreign-rollback': 'Invariant PrefixSound is violated.',
        'initial-wire': 'Invariant NoInitialWire is violated.',
        'rollback-retry': 'Invariant NoRollbackRetry is violated.',
        'crash-late-apply': 'Invariant NoCrashLateApply is violated.',
        'crash-lookup': 'Invariant NoCrashLookup is violated.',
        'recovery': None, 'deny-recovery': 'Temporal properties were violated.'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tlc-jar', type=pathlib.Path, required=True)
    p.add_argument('--java', default='java')
    p.add_argument('--evidence-dir', type=pathlib.Path, required=True)
    p.add_argument('--json-out', type=pathlib.Path, required=True)
    p.add_argument('--source-root', type=pathlib.Path)
    a = p.parse_args()
    if sha(a.tlc_jar) != TLC_SHA:
        raise SystemExit('Pinned official TLC archive hash mismatch')
    a.tlc_jar = a.tlc_jar.resolve()
    java = shutil.which(a.java)
    if not java:
        raise SystemExit('Java executable unavailable')
    a.evidence_dir.mkdir(parents=True, exist_ok=True)
    source = json.loads((MODEL/'source-pin.json').read_text())
    if a.source_root:
        for rel, digest in source['files'].items():
            if sha(a.source_root / rel) != digest:
                raise SystemExit('Product source drift: ' + rel)
    paths = [MODEL/'RetryProtocol.tla', MODEL/'source-pin.json', pathlib.Path(__file__).resolve()]
    paths += sorted((MODEL/'configs').glob('*.cfg'))
    hashes = {str(f.relative_to(ROOT)): sha(f) for f in paths}
    for f in paths:
        retained = a.evidence_dir / 'inputs' / f.relative_to(ROOT)
        retained.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, retained)
    version = subprocess.run([java, '-version'], text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=10)
    if version.returncode:
        raise SystemExit('Java runtime probe failed: '+version.stdout)
    report = {'status': 'PASS', 'bounded_model_only': True, 'tlc_sha256': TLC_SHA,
              'java_version': version.stdout, 'java_executable_sha256': sha(pathlib.Path(java)),
              'checked_input_hashes': hashes, 'source_bytes_checked': bool(a.source_root), 'runs': []}
    for name, failure in RUNS.items():
        out = a.evidence_dir/name
        out.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='retry-protocol-') as tmp:
            work = pathlib.Path(tmp)
            shutil.copy2(MODEL/'RetryProtocol.tla', work/'RetryProtocol.tla')
            shutil.copy2(MODEL/'configs'/f'{name}.cfg', work/'run.cfg')
            argv = [java, '-Xmx768m', '-XX:+UseParallelGC', '-cp', str(a.tlc_jar),
                    'tlc2.TLC', '-workers', '1', '-deadlock', '-metadir', str(work/'states'),
                    '-config', 'run.cfg', 'RetryProtocol.tla']
            start = time.monotonic()
            try:
                result = subprocess.run(argv, cwd=work, text=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, timeout=60)
                raw, code = result.stdout, result.returncode
            except subprocess.TimeoutExpired as e:
                raw = e.stdout or b''
                if isinstance(raw, bytes): raw=raw.decode(errors='replace')
                code = None
            elapsed=time.monotonic()-start
            (out/'tlc.log').write_text(raw)
            completed = 'Model checking completed. No error has been found.' in raw
            trace = 'The behavior up to this point is:' in raw or 'The following behavior constitutes a counter-example:' in raw
            errors = re.findall(r'^Error: (.*)$', raw, re.M)
            if failure:
                passed = code is not None and code != 0 and trace and failure in errors
                passed = passed and all(x in [failure, 'The behavior up to this point is:',
                    'The following behavior constitutes a counter-example:'] for x in errors)
            else:
                passed = code == 0 and completed and not errors and bool(re.search(r'\d+ distinct states found',raw))
            receipt={'variant':name, 'argv':argv, 'elapsed_seconds':round(elapsed,4),
                     'exit_code':code, 'expected_error':failure, 'errors':errors,
                     'pass':passed, 'log_sha256':sha(out/'tlc.log'),
                     'state_summary':re.findall(r'^.*states generated.*$',raw,re.M)}
            (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
            report['runs'].append(receipt)
            if not passed: report['status']='FAIL'
        if not passed: break
    report['inputs_unchanged'] = all(sha(ROOT/rel)==digest for rel,digest in hashes.items())
    if not report['inputs_unchanged']: report['status']='FAIL'
    a.json_out.parent.mkdir(parents=True,exist_ok=True)
    a.json_out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())
