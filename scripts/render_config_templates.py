#!/usr/bin/env python3
"""Render machine-specific Shiori templates to a NEW preview folder only.

No installation, session changes, subprocess, sudo, network, or overwrites.
Default is DRY RUN. Even --write refuses ~/.config and existing targets.
"""
import argparse
import json
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]
FILES=('configs/hypr/hyprland.conf','configs/hypr/hyprpaper.conf',
       'configs/waybar/config','configs/waybar/style.css')
OUTPUT_RE=re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,48}$')


def safe_output_folder(p):
    p=p.expanduser().resolve()
    home=Path.home().resolve()
    forbidden=(home/'.config',home/'.local',home/'.ssh',home/'.gnupg')
    if p==home or any(p==q or p.is_relative_to(q) for q in forbidden):
        raise ValueError('refusing to write to live configuration or private directories')
    if p.exists():
        raise ValueError('output directory already exists; never overwrite')
    return p


def values(args):
    for name in ('main_output','portrait_output'):
        if not OUTPUT_RE.fullmatch(getattr(args,name)):
            raise ValueError('invalid monitor connector: '+name)
    if args.main_output==args.portrait_output:
        raise ValueError('main and portrait outputs must differ')
    wallpaper_paths=[]
    for image in (args.main_wallpaper,args.portrait_wallpaper):
        if not image.expanduser().is_file():
            raise ValueError('wallpaper file not found: '+str(image))
        wallpaper_paths.append(str(image.expanduser().resolve()))
    # Templates are string-substituted in multiple formats; prevent escaping strings.
    for v in (str(Path.home()),*wallpaper_paths):
        if any(c in v for c in ('"','\n','\r','\\','{{','}}')):
            raise ValueError('unsupported quote or control characters in path')
    return {
        '{{HOME}}':str(Path.home()),
        '{{MAIN_OUTPUT}}':args.main_output,
        '{{PORTRAIT_OUTPUT}}':args.portrait_output,
        '{{MAIN_WALLPAPER}}':wallpaper_paths[0],
        '{{PORTRAIT_WALLPAPER}}':wallpaper_paths[1]
    }


def render(contents, substitutions):
    for key,val in substitutions.items():
        contents=contents.replace(key,val)
    if '{{' in contents or '}}' in contents:
        raise ValueError('unresolved template token')
    return contents


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--main-output',required=True)
    p.add_argument('--portrait-output',required=True)
    p.add_argument('--main-wallpaper',required=True,type=Path)
    p.add_argument('--portrait-wallpaper',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path,help='new preview folder only')
    p.add_argument('--write',action='store_true',help='create preview folder and files')
    args=p.parse_args()
    try:
        output=safe_output_folder(args.output)
        mapping=values(args)
        for rel in FILES:
            t=render((ROOT/rel).read_text(encoding='utf8'),mapping)
            if rel=='configs/waybar/config': json.loads(t)
        if not args.write:
            print('DRY RUN: valid templates; would render',len(FILES),'files into',output)
            return 0
        output.mkdir(parents=True)
        try:
            for rel in FILES:
                dest=output/rel
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_text(render((ROOT/rel).read_text(encoding='utf8'),mapping),encoding='utf8')
        except Exception:
            shutil.rmtree(output)
            raise
        print('Rendered preview only:',output)
        print('No live configuration changed. No services reloaded.')
        return 0
    except (ValueError,OSError,json.JSONDecodeError) as error:
        p.error(str(error))

if __name__=='__main__':
    raise SystemExit(main())
