#!/usr/bin/env python3
"""Generate a Waybar CSS *preview/cache* from locally installed app icons.

No network, sudo, live config changes, or service reload. Safe by default:
requires --write to save, only permits outputs inside ~/.cache/shiori-crimson/.
"""
import argparse
from pathlib import Path
import sys
from icon_resolver import APPS, choose_app, resolve_gicon_file, css_for_icons


def resolve_all():
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gio, Gtk
        apps = Gio.AppInfo.get_all()
        theme = Gtk.IconTheme.get_default()
        return {action: resolve_gicon_file((app.get_icon() if app else None), theme)
                for action in APPS for app in [choose_app(apps, action)]}
    except (ImportError, ValueError, RuntimeError, AttributeError) as error:
        print('GTK/Gio unavailable; generic dock glyphs will be used:', type(error).__name__, file=sys.stderr)
        return {}


def allowed_cache_output(output, home=None):
    home = home or Path.home()
    parent = home/'.cache/shiori-crimson'
    if parent.is_symlink():
        return False
    safe = parent.resolve()
    dest = output.expanduser().resolve()
    return dest != safe and dest.is_relative_to(safe) and not output.is_symlink()


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--base', required=True, type=Path, help='Read-only Waybar CSS source')
    cli.add_argument('--output', required=True, type=Path, help='Cache-only stylesheet path')
    cli.add_argument('--write', action='store_true', help='Opt in to writing cache CSS')
    cli.add_argument('--replace', action='store_true', help='Replace an existing cache CSS file')
    args=cli.parse_args()
    if not args.base.is_file() or args.base.is_symlink():
        cli.error('base CSS is missing or a symlink')
    if not allowed_cache_output(args.output):
        cli.error('output must be within ~/.cache/shiori-crimson/ and must not be a symlink')
    icons=resolve_all()
    css=args.base.read_text(encoding='utf-8')+'\n'+css_for_icons(icons)
    print('Resolved installed app icons:', ', '.join(sorted(a for a,p in icons.items() if p)) or 'none (generic fallback)')
    if not args.write:
        print('DRY RUN: no cache files changed. Pass --write to save.')
        return 0
    if args.output.exists() and not args.replace:
        cli.error('target exists; --replace is required for updating cache CSS')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp=args.output.with_name(args.output.name+'.tmp')
    if tmp.exists() or tmp.is_symlink():
        cli.error('temporary output already exists')
    try:
        tmp.write_text(css,encoding='utf-8')
        tmp.replace(args.output)
    finally:
        if tmp.exists(): tmp.unlink()
    print('Wrote cache-only CSS:', args.output)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
