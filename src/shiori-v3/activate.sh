#!/usr/bin/env bash
set -Eeuo pipefail
D="$HOME/.config/shiori-v3"
[[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] || { echo 'Hyprland session not detected. GNOME fallback is untouched.' >&2; exit 1; }
for cmd in waybar hyprpaper; do command -v "$cmd" >/dev/null || { echo "Missing $cmd" >&2; exit 1; }; done
/usr/bin/python3 - <<'PY'
import gi
gi.require_version('Gtk','3.0')
gi.require_version('GtkLayerShell','0.1')
from gi.repository import Gtk,GtkLayerShell
import psutil
print('GTK3, gtk-layer-shell and psutil loaded')
PY
# No changes to Hyprland monitors, input or reload.
# Start HUD first; Waybar and wallpaper will be restarted only if HUD starts.
"$D/start.sh"
sleep 1
if ! /usr/bin/python3 "$D/hud/shiori_hud.py" status; then
  echo "HUD did not start. Read ~/.cache/shiori-v3-hud.log. Your existing Waybar remains running." >&2
  exit 1
fi
pkill -x waybar || true
nohup "$D/start-waybar.sh" > "$HOME/.cache/shiori-v3-waybar.log" 2>&1 </dev/null &
sleep 1
if ! pgrep -x waybar >/dev/null; then
  echo 'Waybar failed to restart! Use ~/.config/shiori-v3/restore.sh for rollback.' >&2
  exit 1
fi
pkill -x hyprpaper || true
nohup hyprpaper > "$HOME/.cache/shiori-v3-hyprpaper.log" 2>&1 </dev/null &
sleep 1
if ! pgrep -x hyprpaper >/dev/null; then
  echo 'Hyprpaper failed to restart. Rollback is available.' >&2
  exit 1
fi
printf '\nShiori v3 activated. Press Super+D to show the screenshot-style launcher.\n'
printf 'HUD cards render on LG (DP-6); ASUS and both monitor layouts are unchanged.\n'
