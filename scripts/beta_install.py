#!/usr/bin/env python3
"""Shiori Crimson v0.1.0-beta.1: cautious fresh-test-account installer.

No root, package changes, network, GPU probing, service restarts or compositor reload.
DRY RUN by default. Installs only to previously ABSENT files in user's home.
Records exact file hashes so rollback refuses to remove modified files.
Not a production installer: original HUD and power UI require an LG monitor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import render_config_templates as templater

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'v0.1.0-beta.1'
STATE_REL = Path('.local/state/shiori-crimson-beta1/install.json')
REQUIRED = ('waybar', 'hyprpaper', 'hyprctl', 'python3', 'bash')
CONFIRM_INSTALL = 'INSTALL-SHIORI-BETA-TEST-ACCOUNT'
CONFIRM_ROLLBACK = 'ROLLBACK-SHIORI-BETA'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def contents(root: Path, home: Path, args) -> dict[str, tuple[bytes, int]]:
    """Return exact home-relative destination map; no writes."""
    if not root.is_dir() or root.is_symlink():
        raise ValueError('source repository path unsafe')
    user_inputs = SimpleNamespace(
        main_output=args.main_output, portrait_output=args.portrait_output,
        main_wallpaper=Path(args.main_wallpaper), portrait_wallpaper=Path(args.portrait_wallpaper),
    )
    mapping = templater.values(user_inputs)
    mapping['{{HOME}}'] = str(home)
    result: dict[str, tuple[bytes, int]] = {}
    generated = {
        'configs/hypr/hyprland.conf': '.config/hypr/hyprland.conf',
        'configs/hypr/hyprpaper.conf': '.config/hypr/hyprpaper.conf',
        'configs/waybar/config': '.config/waybar/config',
        'configs/waybar/style.css': '.config/waybar/style.css',
    }
    for src, dst in generated.items():
        path = root / src
        if path.is_symlink() or not path.is_file():
            raise ValueError('template file missing or unsafe: ' + src)
        rendered = templater.render(path.read_text(encoding='utf8'), mapping)
        if src.endswith('waybar/config'):
            json.loads(rendered)
        result[dst] = (rendered.encode('utf8'), 0o644)

    source_dir = root / 'src/shiori-v3'
    for path in sorted(source_dir.rglob('*')):
        if path.is_symlink():
            raise ValueError('symlink in source tree: ' + str(path.relative_to(root)))
        if not path.is_file():
            continue
        if '__pycache__' in path.parts or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.name in ('activate.sh', 'restore.sh'):
            # Historical Asura activation/restore scripts manipulate live services.
            continue
        rel = path.relative_to(source_dir)
        dest = (Path('.config/shiori-v3') / rel).as_posix()
        result[dest] = (path.read_bytes(), 0o755 if os.access(path, os.X_OK) else 0o644)
    icon_helper = root / 'scripts/helpers/shiori-gpu-status.sh'
    if icon_helper.is_symlink() or not icon_helper.is_file():
        raise ValueError('GPU-status helper missing or unsafe')
    result['.config/waybar/scripts/shiori-gpu-status.sh'] = (icon_helper.read_bytes(), 0o755)
    return result


def state_path(home: Path) -> Path:
    return home / STATE_REL


def validate_home_targets(home: Path, rels: list[str], *, require_absent: bool) -> None:
    if home.is_symlink() or not home.is_dir():
        raise ValueError('home is missing or symbolic link')
    home = home.resolve()
    for rel in rels:
        p = Path(rel)
        if p.is_absolute() or '..' in p.parts or not p.parts or not rel.startswith('.config/'):
            raise ValueError('unsafe target path')
        target = home / p
        for parent in [*target.parents, target]:
            if parent == home.parent: break
            if parent.is_symlink():
                raise ValueError('symbolic link in target path: ' + str(parent))
        if require_absent and (target.exists() or target.is_symlink()):
            raise ValueError('refusing to overwrite existing file: ' + rel)


def manifest_entries(files: dict[str, tuple[bytes, int]]) -> list[dict]:
    return [dict(path=rel, sha256=digest(data), mode=mode) for rel, (data, mode) in sorted(files.items())]


def safe_parent_create(home: Path, target: Path, created_dirs: list[Path]) -> None:
    missing: list[Path] = []
    q = target.parent
    while not q.exists():
        missing.append(q)
        q = q.parent
    for q in reversed(missing):
        q.mkdir(mode=0o700)
        created_dirs.append(q)


def write_new_file(path: Path, data: bytes, mode: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, mode)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        path.chmod(mode)
    except BaseException:
        try: path.unlink()
        except FileNotFoundError: pass
        raise


def new_state(home: Path, record: dict) -> None:
    st = state_path(home)
    if st.exists() or st.is_symlink():
        raise ValueError('install manifest exists; use status / rollback')
    # The state directory may not redirect through a symbolic link.
    q = st.parent
    while q != home.parent:
        if q.is_symlink():
            raise ValueError('symbolic link in state directory: ' + str(q))
        if q == home:
            break
        q = q.parent
    parents: list[Path] = []
    safe_parent_create(home, st, parents)
    write_new_file(st, (json.dumps(record, indent=2, sort_keys=True) + '\n').encode(), 0o600)


def set_state(home: Path, record: dict) -> None:
    st = state_path(home)
    temp = st.with_name(st.name + '.new')
    write_new_file(temp, (json.dumps(record, indent=2, sort_keys=True) + '\n').encode(), 0o600)
    os.replace(temp, st)


def read_state(home: Path) -> dict:
    st = state_path(home)
    q = st.parent
    while q != home.parent:
        if q.is_symlink():
            raise ValueError('symbolic link in state directory')
        if q == home: break
        q = q.parent
    if not st.is_file() or st.is_symlink():
        raise ValueError('no safe installation manifest found')
    doc = json.loads(st.read_text(encoding='utf8'))
    if doc.get('version') != VERSION or doc.get('state') not in ('pending', 'installed'):
        raise ValueError('unknown manifest version or state')
    return doc


def check_runtime_dependencies() -> None:
    absent = [x for x in REQUIRED if shutil.which(x) is None]
    if absent:
        raise ValueError('required commands missing (install manually): ' + ', '.join(absent))
    interpreter = Path('/usr/bin/python3')
    if not interpreter.exists() or interpreter.is_symlink():
        raise ValueError('/usr/bin/python3 missing or unsafe; original HUD uses this interpreter')
    probe = (
        'import gi,psutil;'
        'gi.require_version("Gtk","3.0");'
        'gi.require_version("GtkLayerShell","0.1");'
        'from gi.repository import Gtk,GtkLayerShell'
    )
    try:
        outcome = subprocess.run([str(interpreter), '-c', probe], timeout=5,
                                 stdin=subprocess.DEVNULL, capture_output=True, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError('GTK3/layer-shell/psutil dependency check failed') from None
    if outcome.returncode:
        raise ValueError('GTK3/layer-shell/psutil unavailable to /usr/bin/python3')


def install(home: Path, args, root=ROOT, check_tools=True) -> int:
    if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
        raise ValueError('refusing installation from an active Hyprland session')
    if args.confirm != CONFIRM_INSTALL or not args.ack_lg_only:
        raise ValueError('explicit fresh-test-account consent and LG-only limitation acknowledgement required')
    if check_tools:
        check_runtime_dependencies()
    files = contents(root, home, args)
    validate_home_targets(home, list(files), require_absent=True)
    rec = {'version': VERSION, 'state': 'pending', 'files': manifest_entries(files)}
    new_state(home, rec)
    try:
        for rel, (data, mode) in files.items():
            target = home / rel
            safe_parent_create(home, target, [])
            write_new_file(target, data, mode)
        rec['state'] = 'installed'
        set_state(home, rec)
    except BaseException:
        # Manifest stays at 'pending' for independent safe rollback after crashes.
        raise
    return len(files)


def rollback(home: Path, *, apply: bool, confirm: str = '', expected_paths: set[str] | None = None) -> int:
    if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
        raise ValueError('refusing rollback from an active Hyprland session')
    doc = read_state(home)
    entries = doc['files']
    rels = [x['path'] for x in entries]
    if len(set(rels)) != len(rels):
        raise ValueError('duplicate manifest paths')
    if expected_paths is None:
        expected_paths = approved_target_paths(ROOT)
    if not set(rels).issubset(expected_paths):
        raise ValueError('manifest includes unknown target path; refusing removal')
    validate_home_targets(home, rels, require_absent=False)
    found = []
    for entry in entries:
        p = home / entry['path']
        if not p.exists():
            if doc['state'] == 'pending': continue
            raise ValueError('installed file missing; inspect manually: ' + entry['path'])
        if not p.is_file() or p.is_symlink() or digest(p.read_bytes()) != entry['sha256']:
            raise ValueError('installed file changed; refusing removal: ' + entry['path'])
        found.append(p)
    if not apply:
        return len(found)
    if confirm != CONFIRM_ROLLBACK:
        raise ValueError('explicit rollback consent is required')
    for p in found:
        p.unlink()
    state_path(home).unlink()
    # Only remove directories if empty, never delete content from other software.
    for p in sorted({x.parent for x in found} | {state_path(home).parent}, key=lambda x: len(x.parts), reverse=True):
        while p != home and p.is_relative_to(home):
            try: p.rmdir()
            except OSError: break
            p = p.parent
    return len(found)


def approved_target_paths(root: Path) -> set[str]:
    # Validate manifest against static source tree, without relying on wallpapers.
    paths = {'.config/hypr/hyprland.conf', '.config/hypr/hyprpaper.conf',
             '.config/waybar/config', '.config/waybar/style.css',
             '.config/waybar/scripts/shiori-gpu-status.sh'}
    for p in (root / 'src/shiori-v3').rglob('*'):
        if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo') and p.name not in ('activate.sh', 'restore.sh'):
            paths.add((Path('.config/shiori-v3') / p.relative_to(root/'src/shiori-v3')).as_posix())
    return paths


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('plan', 'install', 'status', 'rollback'))
    p.add_argument('--main-output')
    p.add_argument('--portrait-output')
    p.add_argument('--main-wallpaper', type=Path)
    p.add_argument('--portrait-wallpaper', type=Path)
    p.add_argument('--apply', action='store_true')
    p.add_argument('--confirm', default='')
    p.add_argument('--ack-lg-only', action='store_true')
    args = p.parse_args()
    home = Path.home()
    try:
        if args.action == 'status':
            doc = read_state(home)
            print(f"{VERSION}: {doc['state']}; {len(doc['files'])} tracked files")
            return 0
        if args.action == 'rollback':
            count = rollback(home, apply=args.apply, confirm=args.confirm)
            print(('ROLLED BACK' if args.apply else 'ROLLBACK PREVIEW') + f': {count} unchanged files. No services restarted.')
            return 0
        if not all((args.main_output, args.portrait_output, args.main_wallpaper, args.portrait_wallpaper)):
            raise ValueError('plan/install require --main-output --portrait-output --main-wallpaper --portrait-wallpaper')
        files = contents(ROOT, home, args)
        validate_home_targets(home, list(files), require_absent=True)
        if state_path(home).exists():
            raise ValueError('installation state already exists')
        print(f'BETA PLAN: {len(files)} fresh files; existing files will NOT be replaced.')
        print('Known limitations: LG-only HUD/power menu; Asura-mode assumptions; no wallpapers bundled.')
        print('No sudo, downloads, package installs, service restarts, reloads, or power actions.')
        if args.action == 'plan' or not args.apply:
            print('DRY RUN ONLY. Install requires --apply --ack-lg-only --confirm ' + CONFIRM_INSTALL)
            return 0
        count = install(home, args)
        print(f'INSTALLED {count} files in fresh test account. No services started. To undo, run rollback preview first.')
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as ex:
        print('REFUSED:', ex, file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
