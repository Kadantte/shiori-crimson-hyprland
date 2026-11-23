#!/usr/bin/env python3
"""Shiori v3.3: read-only Hyprland taskbar state and exact-address focusing.

Waybar calls `state APP`; launcher calls `focus APP`. No shell commands,
window moves, monitor changes, Docker mutation or NVIDIA polling.
"""
import json
import re
import subprocess
import sys

APPS = {
    'chrome':  [r'^(google-chrome(-stable)?|chrome|chromium|chromium-browser)$'],
    'code':    [r'^(code|code-oss|codium|vscodium|Code)$'],
    'kitty':   [r'^(kitty)$'],
    'nautilus':[r'^(org\.gnome\.Nautilus|nautilus|Nautilus)$'],
    'monitor': [r'^(gnome-system-monitor|org\.gnome\.SystemMonitor)$'],
    'discord': [r'^(discord|Discord|discord-canary|com\.discordapp\.Discord)$'],
    'spotify': [r'^(spotify|Spotify|com\.spotify\.Client)$'],
    'docker':  [r'^(docker-desktop|Docker Desktop|com\.docker\.desktop)$'],
}
FALLBACK = {
    'chrome':'◎', 'code':'', 'kitty':'', 'nautilus':'',
    'monitor':'', 'discord':'◉', 'spotify':'', 'docker':'▣'
}
ADDRESS = re.compile(r'^0x[0-9a-fA-F]+$')


def hypr_json(command):
    try:
        proc = subprocess.run(['hyprctl', '-j', command], capture_output=True,
                              text=True, timeout=2, check=False)
        return json.loads(proc.stdout) if proc.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def matches(app, client):
    name = str(client.get('class') or client.get('initialClass') or '')
    title = str(client.get('title') or '')
    if app == 'docker' and name.lower() == 'kitty':
        return title.startswith('Shiori Docker')
    return any(re.fullmatch(pattern, name, re.IGNORECASE) for pattern in APPS[app])


def eligible_clients(app, clients):
    out=[]
    for c in clients if isinstance(clients, list) else []:
        if not isinstance(c, dict):
            continue
        ws = c.get('workspace') or {}
        # Ignore special/minimized/hidden workspaces; never move windows.
        if not isinstance(ws, dict) or not isinstance(ws.get('id'), int) or ws['id'] <= 0:
            continue
        if not ADDRESS.fullmatch(str(c.get('address', ''))):
            continue
        if matches(app, c):
            out.append(c)
    return out


def current_address():
    active = hypr_json('activewindow')
    return str(active.get('address') or '') if isinstance(active, dict) else ''


def state(app):
    clients=eligible_clients(app, hypr_json('clients'))
    active=current_address()
    current = any(c['address']==active for c in clients)
    state_name='focused' if current else 'running' if clients else 'idle'
    return {'text':FALLBACK[app], 'class':[state_name],
            'tooltip':f'{app.capitalize()} — {"focused" if current else "running (click to focus)" if clients else "click to launch"}'}


def focus(app):
    clients=eligible_clients(app, hypr_json('clients'))
    if not clients:
        return 1
    active=current_address()
    # If already focused, treat click as success; never open a second instance.
    if any(c['address']==active for c in clients):
        return 0
    # Hyprland reports focusHistoryID=0 for most recently focused window.
    clients.sort(key=lambda c: (int(c.get('focusHistoryID', 99999)) if str(c.get('focusHistoryID', '')).lstrip('-').isdigit() else 99999))
    addr=clients[0]['address']
    try:
        result=subprocess.run(['hyprctl','dispatch','focuswindow',f'address:{addr}'],
                              capture_output=True, text=True, timeout=2, check=False)
        return 0 if result.returncode == 0 and 'error' not in result.stdout.lower() else 1
    except (OSError, subprocess.TimeoutExpired):
        return 1


def main():
    if len(sys.argv)!=3 or sys.argv[1] not in ('state','focus') or sys.argv[2] not in APPS:
        print('Usage: dock_state.py state|focus chrome|code|kitty|nautilus|monitor|discord|spotify|docker',file=sys.stderr)
        return 2
    action,app=sys.argv[1:]
    if action=='state':
        print(json.dumps(state(app), ensure_ascii=False))
        return 0
    return focus(app)


if __name__=='__main__':
    raise SystemExit(main())
