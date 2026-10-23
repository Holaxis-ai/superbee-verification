#!/usr/bin/env python3
"""Fetch pinned official executables into a caller-owned directory; no installs or analysis.

Network: at most two curl invocations, each 60s. Emit JSON paths, not shell assignments.
Gillian is a mutable nightly release name; SHA256 pins bytes and fails closed on replacement.
The observed nightly tag/source commit is metadata, not a reproducible-build attestation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import stat
import subprocess
import tarfile
import tempfile
import time
import zipfile


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_name(name):
    parsed = PurePosixPath(name)
    if not name or parsed.is_absolute() or ".." in parsed.parts or "\\" in name or ":" in name:
        raise ValueError("Unsafe archive path: " + name)
    return parsed


def extract(archive, target):
    """Write only regular files/directories, never links or archive-supplied permissions."""
    if archive.name.endswith(".tar.gz"):
        with tarfile.open(archive, "r:gz") as data:
            entries = data.getmembers()
            if len(entries) != 1 or entries[0].name != "gillian-js" or not entries[0].isfile():
                raise ValueError("Unexpected Gillian archive layout")
            entry = entries[0]
            safe_name(entry.name)
            if entry.size > 200 * 1024 * 1024:
                raise ValueError("Oversize Gillian executable")
            with data.extractfile(entry) as src, (target / entry.name).open("xb") as dst:
                shutil.copyfileobj(src, dst)
        executable = target / "gillian-js"
    else:
        with zipfile.ZipFile(archive) as data:
            entries = data.infolist()
            if sum(entry.file_size for entry in entries) > 600 * 1024 * 1024 or len(entries) > 10000:
                raise ValueError("Oversize Z3 archive")
            names = set()
            for entry in entries:
                path = safe_name(entry.filename)
                if path in names:
                    raise ValueError("Duplicate archive path")
                names.add(path)
                mode = entry.external_attr >> 16
                kind = stat.S_IFMT(mode)
                if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise ValueError("Archive contains non-regular file")
                out = target.joinpath(*path.parts)
                if entry.is_dir():
                    out.mkdir(parents=True, exist_ok=True)
                else:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    with data.open(entry) as src, out.open("xb") as dst:
                        shutil.copyfileobj(src, dst)
        root = archive.name[:-4]
        executable = target / root / "bin" / "z3"
    if not executable.is_file() or executable.is_symlink():
        raise ValueError("Expected executable missing")
    executable.chmod(0o755)
    return executable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", type=Path, required=True, help="Caller-owned directory for archives/executables")
    parser.add_argument("--pin", type=Path, required=True, help="Reviewed platform/archive manifest")
    args = parser.parse_args()
    started = time.monotonic()
    key = (platform.system(), platform.machine())
    if key not in (("Darwin", "arm64"), ("Linux", "x86_64")):
        raise SystemExit("Only Darwin arm64 and Linux x86_64 are supported")
    if key[0] == "Linux":
        family, version = platform.libc_ver()
        if family != "glibc" or tuple(map(int, version.split(".")[:2])) < (2, 39):
            raise SystemExit("Pinned Linux Z3 requires glibc >=2.39 (Ubuntu24.04)")
    pin_bytes = args.pin.read_bytes()
    manifest_hash = hashlib.sha256(pin_bytes).hexdigest()
    pin = json.loads(pin_bytes)
    selected = pin["platforms"]["-".join(key)]
    archives_by_id = {row["asset_id"]: row for row in pin["archives"]}
    selected_archives = [archives_by_id[selected[name + "_asset_id"]] for name in ("gillian", "z3")]
    dest = args.dir.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    if not dest.is_dir():
        raise ValueError("Destination must be a directory")
    tools = Path(tempfile.mkdtemp(prefix="verified-tools-", dir=dest))
    records = []
    executables = []
    try:
        for row in selected_archives:
            name, url, digest, length, asset_id = (row[k] for k in ("archive", "url", "sha256", "bytes", "asset_id"))
            if Path(name).name != name or not url.startswith("https://github.com/") or not isinstance(length, int) or not 0 < length < 100 * 1024 * 1024:
                raise ValueError("Invalid reviewed asset pin")
            if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                raise ValueError("Invalid SHA256 pin")
            if time.monotonic() - started > 140:
                raise TimeoutError("Tool preparation exceeded bounded budget")
            archive = dest / name
            if archive.is_symlink():
                raise ValueError("Refusing archive symlink")
            if not archive.exists():
                fd, temporary = tempfile.mkstemp(prefix="download-", dir=dest)
                os.close(fd)
                try:
                    subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error", "--max-time", "60", "--output", temporary, url], check=True, timeout=65)
                    downloaded = Path(temporary)
                    if downloaded.stat().st_size != length or sha256(downloaded) != digest:
                        raise ValueError("Downloaded bytes do not match pinned asset: " + name)
                    os.replace(temporary, archive)
                finally:
                    Path(temporary).unlink(missing_ok=True)
            if not archive.is_file() or archive.stat().st_size != length or sha256(archive) != digest:
                raise ValueError("Cached bytes do not match pinned asset: " + name)
            target = tools / ("gillian" if name.startswith("gillian") else "z3")
            target.mkdir()
            executable = extract(archive, target)
            executables.append(str(executable))
            records.append({"archive": str(archive), "url": url, "asset_id": asset_id, "sha256": digest, "bytes": length, "executable_sha256": sha256(executable)})
        result = {
            "manifestSha256": manifest_hash,
            "platform": "-".join(key),
            "gillian": executables[0],
            "gillianSha256": sha256(Path(executables[0])),
            "z3": executables[1],
            "z3Sha256": sha256(Path(executables[1])),
            "path_prepend": str(Path(executables[1]).parent),
            "unset_environment": ["GILLIAN_JS_RUNTIME_PATH"],
            "z3_version": pin["z3_version"],
            "gillian_observed_release_tag_commit": pin["gillian_release_tag_observed_commit"],
            "identity_scope": pin["gillian_identity_scope"],
            "archives": records,
            "prepare_seconds": round(time.monotonic() - started, 4),
        }
        encoded = json.dumps(result, indent=2) + "\n"
        (tools / "manifest.json").write_text(encoded)
        receipt_tmp = tools / "receipt.tmp"
        receipt_tmp.write_text(encoded)
        os.replace(receipt_tmp, dest / "receipt.json")
        print(encoded, end="")
    except BaseException:
        shutil.rmtree(tools)
        raise


if __name__ == "__main__":
    main()
