"""Application discovery/search for Shiori Crimson. Uses existing Gio.AppInfo objects.

Unlike Gio.AppInfo.should_show(), filters Hidden and NoDisplay but does not
exclude GNOME-only desktop entries just because the session is Hyprland.
This is intentional for the full application catalogue and System Settings.
"""
from pathlib import Path
import os


def _get(app, method, default=None):
    fn = getattr(app, method, None)
    if not callable(fn):
        return default
    try:
        value = fn()
        return default if value is None else value
    except (AttributeError, OSError, ValueError, TypeError):
        return default


def _desktop_file(app):
    path = _get(app, 'get_filename')
    if path and Path(path).is_file():
        return Path(path)
    desktop_id = str(_get(app, 'get_id', '') or '')
    if not desktop_id.endswith('.desktop') or '/' in desktop_id or '..' in desktop_id:
        return None
    roots = [os.environ.get('XDG_DATA_HOME') or str(Path.home() / '.local/share')]
    roots += (os.environ.get('XDG_DATA_DIRS') or '/usr/local/share:/usr/share').split(':')
    for root in roots:
        if not root:
            continue
        file = Path(root) / 'applications' / desktop_id
        if file.is_file():
            return file
    return None


def _flags_from_desktop(path):
    """Read only Desktop Entry flags; ignore localized groups and secondary actions."""
    flags = {}
    if path is None:
        return flags
    try:
        in_section = False
        with path.open('r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    in_section = line == '[Desktop Entry]'
                elif in_section and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    if key in ('Hidden', 'NoDisplay', 'Type'):
                        flags[key] = value.strip()
    except (OSError, UnicodeError):
        return {}
    return flags


def is_settings(app):
    aid = str(_get(app, 'get_id', '')).lower()
    exe = str(_get(app, 'get_executable', '')).lower()
    name = str(_get(app, 'get_name', '')).casefold()
    return aid in ('org.gnome.settings.desktop', 'gnome-control-center.desktop') or (
        'gnome-control-center' in exe and name in ('settings', 'system settings', 'gnome settings', 'paramètres')
    )


def is_visible_app(app):
    if not _get(app, 'get_name', ''):
        return False
    hidden = _get(app, 'get_is_hidden')
    no_display = _get(app, 'get_nodisplay')
    if hidden is True or no_display is True:
        return False
    flags = _flags_from_desktop(_desktop_file(app))
    if flags.get('Hidden', '').lower() == 'true' or flags.get('NoDisplay', '').lower() == 'true':
        return False
    if flags.get('Type', 'Application') not in ('Application', ''):
        return False
    if hidden is None and no_display is None and not flags:
        # Some Gio wrappers don't expose DesktopAppInfo metadata. In that case
        # honor should_show(), except for the requested GNOME Settings launcher.
        should_show = _get(app, 'should_show', True)
        if not should_show and not is_settings(app):
            return False
    return True


def app_search_text(app):
    fields = []
    for name in ('get_name', 'get_display_name', 'get_generic_name',
                 'get_description', 'get_executable', 'get_id',
                 'get_keywords', 'get_categories'):
        value = _get(app, name)
        if isinstance(value, (tuple, list)):
            fields.extend(str(v) for v in value)
        elif value:
            fields.append(str(value))
    if is_settings(app):
        fields.append('settings system settings preferences control center display sound network bluetooth')
    return ' '.join(fields).casefold()


def discover(apps):
    unique = {}
    for app in apps:
        if not is_visible_app(app):
            continue
        key = _get(app, 'get_id') or (
            str(_get(app, 'get_name', '')).casefold(), str(_get(app, 'get_executable', '')).casefold()
        )
        if key not in unique:
            unique[key] = app
    return sorted(unique.values(), key=lambda app: (
        0 if is_settings(app) else 1,
        str(_get(app, 'get_name', '')).casefold(),
        str(_get(app, 'get_id', '')).casefold(),
    ))


def search(apps, query):
    tokens = query.casefold().split()
    if not tokens:
        return list(apps)
    return [app for app in apps if all(token in app_search_text(app) for token in tokens)]
