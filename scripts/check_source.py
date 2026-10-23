#!/usr/bin/env python3
"""Offline pin comparison against an explicitly supplied product checkout; never changes it."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

if len(sys.argv) != 2:
    raise SystemExit('Usage: python3 scripts/check_source.py /path/to/superbee-checkout')
root = Path(__file__).resolve().parents[1]
pin = json.loads((root / 'experiments/journal-retirement/source-pin.json').read_text())
checkout = Path(sys.argv[1]).resolve()
commit = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
if commit != pin['commit']:
    raise SystemExit('STALE: checkout differs from pinned source; no current-source proof claim.')
for path, expected in pin['paths'].items():
    if hashlib.sha256((checkout / path).read_bytes()).hexdigest() != expected['sha256']:
        raise SystemExit('STALE: pinned file differs: ' + path)
print('Source pin matches checkout bytes. Mathematical correspondence is NOT established by this check.')
