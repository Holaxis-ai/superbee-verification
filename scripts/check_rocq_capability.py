#!/usr/bin/env python3
"""Run the pinned upstream toy binary controls, not a Superbee correctness proof."""
import argparse
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
PIN = ROOT / 'experiments/rocq-binary-capability/pins.json'
# Authoritative upstream commands; the actual container argv below records the
# Bash invocation needed on our noexec work mount without changing script bytes.
COMMANDS = ['dune build --root . @theories/default @tests/default', './tests/check.sh']
# Keep the upstream build and checker unchanged. Their own exits decide acceptance;
# the wrapper additionally binds their inputs and generated binary identities.
CHECK = r'''set -u
cp -R /input/. /work/
cd /work
rocq --version > /evidence/versions.log 2>&1 && dune --version >> /evidence/versions.log 2>&1 && elf-snapshot --help >> /evidence/versions.log 2>&1
setup_exit=$?
printf '%s\n' "$setup_exit" > /evidence/setup.exit
if [ "$setup_exit" -ne 0 ]; then exit "$setup_exit"; fi
dune build --root . @theories/default @tests/default > /evidence/build.log 2>&1
build_exit=$?
printf '%s\n' "$build_exit" > /evidence/build.exit
if [ "$build_exit" -ne 0 ]; then exit "$build_exit"; fi
# /work remains noexec; interpret the pinned, unchanged Bash control script.
bash tests/check.sh > /evidence/checker.log 2>&1
checker_exit=$?
printf '%s\n' "$checker_exit" > /evidence/checker.exit
for f in tests/toy/exit0/exit0.plain tests/toy/exit0/exit0.padded tests/toy/exit1/exit1.plain; do
  sha256sum "_build/default/$f"
done > /evidence/binary-sha256.txt
exit "$checker_exit"
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_sources(source, pins):
    identities = {}
    for relative, expected in pins['files'].items():
        part = Path(relative)
        if part.is_absolute() or '..' in part.parts:
            raise ValueError('Unsafe pinned source path')
        path = source / part
        # Reject symlink traversal, not merely a symlink final leaf.
        for parent in [path, *path.parents]:
            if parent == source:
                break
            if parent.is_symlink():
                raise ValueError('Symlink source: ' + relative)
        if not stat.S_ISREG(path.stat().st_mode) or path.stat().st_size != expected['bytes'] or sha(path) != expected['sha256']:
            raise ValueError('Source identity mismatch: ' + relative)
        identities[relative] = expected
    return identities


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--evidence-dir', required=True, type=Path)
    parser.add_argument('--json-out', required=True, type=Path)
    parser.add_argument('--validate-only', action='store_true', help='Hash inputs only; never reports native acceptance')
    parser.add_argument('--container-name', default='superbee-rocq-' + uuid.uuid4().hex)
    args = parser.parse_args()
    if not re.fullmatch(r'superbee-rocq-[a-zA-Z0-9-]+', args.container_name):
        parser.error('Container name must be a unique superbee-rocq-* name')
    evidence = args.evidence_dir.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    report = {'v': 1, 'status': 'failed', 'scope': 'upstream Rocq/LPS toy binary capability only',
              'substantial_component_milestone': False, 'native_checks_run': False, 'commands': []}
    pins = json.loads(PIN.read_text())
    report.update(upstream_revision=pins['commit'], checker=pins['checker'], pin_sha256=sha(PIN))
    container_attempted = False
    start = time.monotonic()

    def command(label, argv, timeout):
        before = time.monotonic()
        path = evidence / (label + '.log')
        row = {'label': label, 'argv': argv}
        report['commands'].append(row)
        with path.open('wb') as output:
            try:
                result = subprocess.run(argv, stdout=output, stderr=subprocess.STDOUT, timeout=timeout, check=False)
                row['exit'] = result.returncode
            except subprocess.TimeoutExpired:
                row['exit'] = 'timeout'
                raise RuntimeError(label + ' exceeded its wall-clock limit') from None
            finally:
                row['seconds'] = round(time.monotonic() - before, 3)
        return row['exit']

    def interrupted(signum, _frame):
        raise InterruptedError('Interrupted by signal ' + str(signum))

    previous = {s: signal.signal(s, interrupted) for s in (signal.SIGINT, signal.SIGTERM)}
    try:
        if pins['official_commands'] != COMMANDS or not re.fullmatch(r'ghcr.io/theorem-labs/oss-fuzz-theorems-checker@sha256:[0-9a-f]{64}', pins['checker']):
            raise ValueError('Unexpected checker or official commands')
        source = args.source_root.resolve()
        report['inputs'] = checked_sources(source, pins)
        if args.validate_only:
            report['status'] = 'inputs_validated_only'
        else:
            if command('daemon-platform', ['docker', 'version', '--format', '{{.Server.Os}}/{{.Server.Arch}}'], 30) != 0 or (evidence / 'daemon-platform.log').read_text().strip() != pins['platform']:
                raise RuntimeError('Requires a native Linux/amd64 Docker daemon; no emulation qualification')
            if command('docker-version', ['docker', 'version', '--format', '{{.Client.Version}} / {{.Server.Version}}'], 30) != 0:
                raise RuntimeError('Cannot record Docker client/server versions')
            if command('image-inspect', ['docker', 'image', 'inspect', pins['checker']], 30) != 0:
                raise RuntimeError('Pinned checker is not present; pull its exact digest separately')
            with tempfile.TemporaryDirectory(prefix='superbee-rocq-inputs-') as directory:
                subset = Path(directory)
                for relative in pins['files']:
                    target = subset / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source / relative, target)
                # Rehash the actual copied bytes mounted for execution.
                checked_sources(subset, pins)
                (evidence / 'controls').mkdir()
                argv = ['docker', 'run', '--name', args.container_name, '--rm', '--pull=never',
                        '--platform', pins['platform'], '--network=none', '--read-only',
                        '--cap-drop=ALL', '--security-opt=no-new-privileges', '--cpus=2',
                        '--memory=6g', '--memory-swap=6g', '--pids-limit=256',
                        '--user', str(os.getuid()) + ':' + str(os.getgid()),
                        '--tmpfs', '/work:rw,nosuid,nodev,size=4g,mode=1777',
                        '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m,mode=1777',
                        '--mount', 'type=bind,src=' + str(subset) + ',dst=/input,readonly',
                        '--mount', 'type=bind,src=' + str(evidence) + ',dst=/evidence',
                        '--env', 'HOME=/tmp', '--env', 'TMPDIR=/evidence/controls',
                        '--workdir', '/work', pins['checker'], 'bash', '-c', CHECK]
                container_attempted = True
                report['native_execution_attempted'] = True
                code = command('container', argv, 900)
                for name in ['setup', 'build', 'checker']:
                    path = evidence / (name + '.exit')
                    report[name + '_exit'] = int(path.read_text()) if path.exists() else None
                if code != 0 or any(report[name + '_exit'] != 0 for name in ['setup', 'build', 'checker']):
                    raise RuntimeError('Native setup, build or upstream checker failed; inspect retained exits/logs')
                binary_rows = (evidence / 'binary-sha256.txt').read_text().splitlines()
                observed = {line.split()[1].removeprefix('_build/default/'): line.split()[0] for line in binary_rows}
                report['binary_sha256'] = observed
                if observed != pins['binary_sha256']:
                    raise ValueError('Generated binary identity mismatch')
                report['status'] = 'passed'
    except (OSError, ValueError, RuntimeError, InterruptedError) as error:
        report['error'] = str(error)
    finally:
        if container_attempted:
            # Also run the matching always() workflow cleanup for forceful cancellation.
            try:
                report['cleanup_exit'] = command('cleanup', ['docker', 'rm', '-f', args.container_name], 30)
            except (OSError, RuntimeError):
                report['cleanup_exit'] = 'failed'
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        for name in ['setup', 'build', 'checker']:
            marker = evidence / (name + '.exit')
            report[name + '_exit'] = int(marker.read_text()) if marker.exists() else None
        report['native_checks_run'] = report['checker_exit'] is not None
        report['seconds'] = round(time.monotonic() - start, 3)
        report['evidence_sha256'] = {str(f.relative_to(evidence)): sha(f) for f in sorted(evidence.rglob('*')) if f.is_file()}
        args.json_out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['status', 'native_checks_run', 'substantial_component_milestone']}))
    return 0 if report['status'] in ['passed', 'inputs_validated_only'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
