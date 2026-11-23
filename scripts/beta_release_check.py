#!/usr/bin/env python3
"""Offline source-beta validation: AST, shell syntax, tests, asset policy, version.

Does not install, configure, restart, log out or access the network/GPU.
Unit test discovery may create normal Python bytecode caches in the checkout.
"""
from __future__ import annotations
import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'v0.1.0-beta.1'


def main() -> int:
    problems = []
    if (ROOT/'VERSION').read_text(encoding='utf8').strip() != VERSION:
        problems.append('VERSION does not match release candidate')
    for path in sorted(ROOT.rglob('*.py')):
        if '.git' in path.parts or '__pycache__' in path.parts:
            continue
        try: ast.parse(path.read_text(encoding='utf8'), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as e: problems.append(f'Python syntax: {path.relative_to(ROOT)} ({type(e).__name__})')
    for path in sorted((ROOT/'src/shiori-v3').rglob('*.sh')) + sorted((ROOT/'scripts/helpers').rglob('*.sh')):
        r = subprocess.run(['bash', '-n', str(path)], capture_output=True, text=True, check=False)
        if r.returncode: problems.append(f'Bash syntax: {path.relative_to(ROOT)}')
    for rel in ('configs/waybar/config', 'docs/source-provenance.json'):
        try: json.loads((ROOT/rel).read_text(encoding='utf8'))
        except (ValueError,OSError) as e: problems.append(f'JSON invalid: {rel}: {type(e).__name__}')
    for rel in ('README.md', 'assets/ASSET-LICENSE.md', 'assets/ASSET-REGISTER.csv', 'docs/installation.md', 'docs/releases/v0.1.0-beta.1.md'):
        if not (ROOT/rel).is_file(): problems.append('missing documentation: '+rel)
    if problems:
        print('FAIL:', *problems, sep='\n  ')
        return 1
    checks = [
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
        [sys.executable, 'scripts/prepublish.py']
    ]
    for cmd in checks:
        r = subprocess.run(cmd, cwd=ROOT, check=False)
        if r.returncode:
            print('FAIL:', cmd, 'returned', r.returncode)
            return r.returncode
    print('PASS: offline release source checks, installer simulation tests, syntax, registered images.')
    print('NOT VERIFIED: real GTK/Hyprland session, complete security/license clearance, installer on spare account.')
    return 0

if __name__=='__main__': raise SystemExit(main())
