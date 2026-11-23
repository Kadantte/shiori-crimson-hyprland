#!/usr/bin/env python3
"""Copy ONE reviewed source file into this repo. Dry-run by default.

No network, sudo, system reloads, or writes outside this repository.
"""
from __future__ import annotations
import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2_000_000
ALLOWED_PREFIXES = ("configs/hypr/", "configs/waybar/", "configs/launchers/", "scripts/hud/", "scripts/dock/", "scripts/helpers/", "src/shiori-v3/")
FORBIDDEN_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "token.json", "known_hosts"}
FORBIDDEN_SUFFIXES = {".pem", ".p12", ".pfx", ".key", ".kdbx", ".db", ".sqlite", ".sqlite3", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}


def validate(source: Path, destination: str, root: Path = ROOT) -> Path:
    if source.is_symlink() or not source.is_file():
        raise ValueError("source must be an existing regular file, not a symlink")
    if source.stat().st_size > MAX_BYTES:
        raise ValueError("source exceeds the maximum file size; inspect manually")
    if source.name in FORBIDDEN_NAMES or source.suffix.lower() in FORBIDDEN_SUFFIXES:
        raise ValueError("this file type/name requires separate manual review; do not import with this utility")
    target_rel = Path(destination)
    if target_rel.is_absolute() or '..' in target_rel.parts or not destination.startswith(ALLOWED_PREFIXES):
        raise ValueError("destination must be under an approved configs/ or scripts/ subdirectory")
    target = root / target_rel
    if target.exists() or target.is_symlink():
        raise ValueError("destination exists; refusing overwrite")
    parent = target.parent
    while parent != root:
        if parent.is_symlink():
            raise ValueError("destination parent is symlink; refusing import")
        parent = parent.parent
    if source.resolve() == target.resolve():
        raise ValueError("source and destination are the same file")
    if source.is_symlink() or any(p.is_symlink() for p in source.parents):
        raise ValueError("symlinked source path is not accepted")
    if b'\x00' in source.read_bytes()[:1024]:
        raise ValueError("binary file; refusing import")
    return target


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--destination', required=True, help='Repo-relative path, e.g. configs/hypr/hyprland.conf')
    p.add_argument('--apply', action='store_true', help='Explicitly copy the reviewed file into repo, not the live desktop')
    args = p.parse_args()
    try:
        target = validate(args.source.expanduser(), args.destination)
    except (OSError, ValueError) as ex:
        print(f"REFUSED: {ex}", file=sys.stderr)
        return 2
    print(f"source: {args.source.expanduser()}")
    print(f"target: {target}")
    if not args.apply:
        print("DRY RUN: no files were changed. Review content and license before --apply.")
        return 0
    # Re-check immediately before copy; refuse overwrite to preserve the repo.
    if target.exists() or target.is_symlink():
        print("REFUSED: destination appeared during review", file=sys.stderr)
        return 2
    target.parent.mkdir(parents=True, exist_ok=True)
    # 'x' is exclusive: never overwrite a path created concurrently.
    with args.source.expanduser().open('rb') as src, target.open('xb') as dst:
        shutil.copyfileobj(src, dst)
    os.chmod(target, args.source.expanduser().stat().st_mode & 0o777)
    print("COPIED into repository only. Run prepublish.py and manually review before committing.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
