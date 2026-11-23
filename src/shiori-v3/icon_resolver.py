"""Resolve third-party app icons from the *installed* desktop, not bundled files.

Pure matching/CSS helpers are dependency-free; GTK/Gio is imported by the runtime
renderer only. No network calls and no writes in this module.
"""
from pathlib import Path

# Exact desktop IDs (case-insensitive) preferred; hints are fallback matches.
APPS = {
    'chrome': (('google-chrome.desktop', 'google-chrome-stable.desktop',
                'chromium.desktop', 'org.chromium.Chromium.desktop'), ('chrome', 'chromium')),
    'discord': (('com.discordapp.Discord.desktop', 'discord.desktop',
                 'discord-canary.desktop'), ('discord',)),
    'docker': (('docker-desktop.desktop', 'com.docker.desktop.desktop'), ('docker desktop',)),
    'spotify': (('com.spotify.Client.desktop', 'spotify.desktop'), ('spotify',)),
}

def call(obj, name, default=''):
    f = getattr(obj, name, None)
    if not callable(f):
        return default
    try:
        return f() or default
    except (TypeError, AttributeError, ValueError, OSError):
        return default

def choose_app(apps, action):
    """Prefer exact installed desktop IDs over heuristics; ignore hidden apps."""
    ids, hints = APPS[action]
    ids = [x.casefold() for x in ids]
    valid = [app for app in apps if not call(app, 'get_is_hidden', False)
             and not call(app, 'get_nodisplay', False)]
    for wanted in ids:
        for app in valid:
            if str(call(app, 'get_id')).casefold() == wanted:
                return app
    for app in valid:
        names = (' '.join((str(call(app, 'get_name')),
                           str(call(app, 'get_id'))))).casefold()
        if any(hint in names for hint in hints):
            return app
    return None

def safe_local_path(path):
    """Only local supported images, never a URL or remote resource."""
    if not path or not isinstance(path, (str, Path)):
        return None
    p = Path(path)
    if not p.is_absolute() or p.suffix.lower() not in ('.png', '.svg', '.jpg', '.jpeg'):
        return None
    return p.resolve() if p.is_file() else None

def resolve_gicon_file(gicon, theme):
    """Handle Gio.FileIcon or Gtk IconTheme lookup. No downloaded icons."""
    if gicon is None:
        return None
    gio_file = call(gicon, 'get_file', None)
    if gio_file is not None:
        path = safe_local_path(call(gio_file, 'get_path', None))
        if path: return path
    if theme is None: return None
    try:
        info = theme.lookup_by_gicon(gicon, 48, 0)
        return safe_local_path(info.get_filename()) if info else None
    except (AttributeError, TypeError, ValueError, OSError):
        return None

def css_for_icons(icons):
    """Only insert file:// URLs for verified local paths; no text hiding otherwise."""
    out = ['/* generated from locally installed desktop entries; no assets redistributed */']
    for action in ('chrome', 'discord', 'docker', 'spotify'):
        path = safe_local_path(icons.get(action))
        if not path: continue
        # URI encoding ensures spaces, quotes and unusual filenames are escaped.
        uri = path.as_uri()
        out.append(f"""window#waybar.shiori-dock #custom-dock-{action} {{
  background-image: url("{uri}");
  background-repeat: no-repeat;
  background-position: center;
  background-size: 35px 35px;
  min-width: 40px;
  min-height: 38px;
  color: transparent;
}}""")
    return '\n'.join(out) + '\n'
