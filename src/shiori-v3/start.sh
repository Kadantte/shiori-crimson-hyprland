#!/usr/bin/env bash
set -euo pipefail
D="$HOME/.config/shiori-v3"
mkdir -p "$HOME/.cache"
if /usr/bin/python3 "$D/hud/shiori_hud.py" status 2>/dev/null; then exit 0; fi
nohup /usr/bin/python3 "$D/hud/shiori_hud.py" > "$HOME/.cache/shiori-v3-hud.log" 2>&1 </dev/null &
disown || true
