#!/usr/bin/env python3
"""Read-only inspection of the 19-file local Shiori review ZIP; optional repo-only staging.

No commands inside the ZIP are run. No changes to ~/.config, Waybar, Hyprland or services.
Risk scans are heuristics; staging is not publication clearance.
"""
from __future__ import annotations

import argparse
import os
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'configs/hypr/hyprland.conf',
    'configs/hypr/hyprpaper.conf',
    'configs/waybar/config',
    'configs/waybar/style.css',
    'scripts/helpers/shiori-gpu-status.sh',
    'scripts/helpers/shiori-cursor-reset',
} | {f'src/shiori-v3/{path}' for path in (
    'activate.sh', 'app_catalog.py', 'dock_state.py', 'hud/shiori_hud.py',
    'launch.sh', 'power-fallback.sh', 'power-menu.css', 'power-menu.sh',
    'power_ui.py', 'restore.sh', 'session-env.sh', 'session-init.sh', 'start.sh'
)}
MAX_SINGLE = 1_000_000
MAX_TOTAL = 4_000_000
SECRET_PATTERNS = {
    'private key': re.compile(r'-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----'),
    'GitHub token': re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})'),
    'AWS access key': re.compile(r'(?:AKIA|ASIA)[A-Z0-9]{16}'),
    'possible credential assignment': re.compile(r'(?im)^\s*(?:export\s+)?(?:password|secret|token|api[_-]?key|client_secret)\s*[:=]\s*\S+'),
}
REVIEW_PATTERNS = {
    'machine-specific home path': re.compile(r'/home/[A-Za-z0-9_.-]+/'),
    'network URL': re.compile(r'https?://[^\s\"\']+'),
    'artwork path reference': re.compile(r'(?i)(?:assets/|\.png\b|\.jpg\b|\.svg\b)'),
    'privileged or destructive command candidate': re.compile(r'(?i)\b(?:sudo|rm\s+-[rRfF]+|reboot|poweroff|shutdown|systemctl)\b'),
}


def inspect(archive: Path):
    """Returns (entries, fatal_errors, warnings, secrets), never prints sensitive text."""
    errors: list[str] = []
    warnings: list[str] = []
    secrets: list[str] = []
    entries: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(archive) as z:
            infos = z.infolist()
            actual_names = [i.filename for i in infos]
            if len(actual_names) != len(set(actual_names)):
                errors.append('archive contains duplicate member names')
            names = set(actual_names)
            if names != EXPECTED:
                errors.append(f'manifest mismatch: missing={len(EXPECTED - names)} unexpected={len(names - EXPECTED)}')
            total = 0
            for i in infos:
                name = i.filename
                pp = PurePosixPath(name)
                if name.startswith('/') or '\\' in name or '..' in pp.parts or pp.is_absolute() or name.endswith('/') or name not in EXPECTED:
                    errors.append('invalid/unexpected archive member (name withheld)')
                    continue
                mode = (i.external_attr >> 16)
                kind = stat.S_IFMT(mode)
                if kind not in (0, stat.S_IFREG):
                    errors.append(f'unsupported file type: {name}')
                    continue
                if i.flag_bits & 1:
                    errors.append(f'encrypted member: {name}')
                    continue
                if i.file_size > MAX_SINGLE:
                    errors.append(f'oversized member: {name}')
                    continue
                total += i.file_size
                if total > MAX_TOTAL:
                    errors.append('archive uncompressed contents exceed size limit')
                    break
                raw = z.read(i)
                if b'\x00' in raw[:4096]:
                    errors.append(f'binary content in code archive: {name}')
                    continue
                try:
                    body = raw.decode('utf-8')
                except UnicodeDecodeError:
                    errors.append(f'non-UTF8 file: {name}')
                    continue
                entries[name] = raw
                for category, pattern in SECRET_PATTERNS.items():
                    for match in list(pattern.finditer(body))[:8]:
                        line = body.count('\n', 0, match.start()) + 1
                        secrets.append(f'{name}:{line}: {category}')
                for category, pattern in REVIEW_PATTERNS.items():
                    count = len(pattern.findall(body))
                    if count:
                        warnings.append(f'{name}: {category} ({count} matches)')
    except (OSError, zipfile.BadZipFile, RuntimeError) as e:
        errors.append(f'cannot inspect ZIP: {type(e).__name__}')
    return entries, errors, warnings, secrets


def stage(entries: dict[str, bytes], root: Path = ROOT) -> Path:
    """Write only to a new, gitignored repo staging tree. No overwrites."""
    staging = root / '_import-staging' / 'source-review'
    if staging.exists() or staging.is_symlink():
        raise FileExistsError('staging destination already exists; refusing to overwrite')
    if (root / '_import-staging').is_symlink():
        raise ValueError('staging parent is symlink; refusing')
    staging.mkdir(parents=True, exist_ok=False)
    try:
        for name, data in sorted(entries.items()):
            dst = staging.joinpath(*PurePosixPath(name).parts)
            dst.parent.mkdir(parents=True, exist_ok=True)
            with dst.open('xb') as file:
                file.write(data)
            if name.endswith('.sh') or name in {'scripts/helpers/shiori-cursor-reset'}:
                os.chmod(dst, 0o700)
            else:
                os.chmod(dst, 0o600)
    except Exception:
        # Keep explicit staging to inspect/recover from partial errors.
        raise
    return staging


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--stage', action='store_true', help='Explicitly stage local ZIP into gitignored repo folder')
    args = parser.parse_args()
    entries, errors, warnings, secrets = inspect(args.archive.expanduser())
    print(f'Shiori code-only archive review: {len(entries)}/{len(EXPECTED)} expected files')
    for warning in warnings:
        print('REVIEW:', warning)
    for error in errors:
        print('ERROR:', error)
    for secret in secrets:
        print('SENSITIVE:', secret)
    if errors or secrets or set(entries) != EXPECTED:
        print('REFUSED: archive is incomplete, unsafe, or contains possible credentials; do not publish.')
        return 2
    if not args.stage:
        print('DRY RUN: archive inspection only. To create private gitignored staging, pass --stage.')
        return 0
    try:
        target = stage(entries)
    except (OSError, ValueError) as e:
        print(f'REFUSED: {e}', file=sys.stderr)
        return 2
    print(f'STAGED INSIDE REPO ONLY: {target}')
    print('No live desktop files modified. Review files manually before any promotion or commit.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
