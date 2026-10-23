"""Shared pinned archive/executable validation for isolated Gillian experiments."""
import hashlib
import json
import os
from pathlib import Path
import tarfile
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_toolchain(tool_dir, pin_path):
    receipt = json.loads((tool_dir / 'receipt.json').read_text())
    if receipt['manifestSha256'] != sha(pin_path):
        raise SystemExit('Tool receipt does not match committed pins')
    pin = json.loads(pin_path.read_text())
    selected = pin['platforms'][receipt['platform']]
    archive_rows = {row['asset_id']: row for row in pin['archives']}
    executables = {}
    for name in ['gillian', 'z3']:
        row = archive_rows[selected[name + '_asset_id']]
        archive = tool_dir / row['archive']
        if not archive.is_file() or archive.stat().st_size != row['bytes'] or sha(archive) != row['sha256']:
            raise SystemExit('Pinned archive identity mismatch: ' + name)
        if name == 'gillian':
            with tarfile.open(archive, 'r:gz') as data:
                expected = hashlib.sha256(data.extractfile('gillian-js').read()).hexdigest()
        else:
            with zipfile.ZipFile(archive) as data:
                expected = hashlib.sha256(data.read(archive.name[:-4] + '/bin/z3')).hexdigest()
        path = Path(receipt[name])
        if not path.is_file() or sha(path) != expected or receipt[name + 'Sha256'] != expected:
            raise SystemExit('Executable differs from pinned archive: ' + name)
        executables[name] = path.resolve()
    env = dict(os.environ, PATH=str(executables['z3'].parent) + os.pathsep + os.environ.get('PATH', ''))
    env.pop('GILLIAN_JS_RUNTIME_PATH', None)
    return receipt, executables, env
