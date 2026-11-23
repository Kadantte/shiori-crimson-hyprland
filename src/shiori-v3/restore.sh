#!/usr/bin/env bash
set -Eeuo pipefail
D="$HOME/.config/shiori-v3"
[[ -f "$D/last-backup.txt" ]] || { echo 'No Shiori v3 backup pointer found.' >&2; exit 1; }
BK="$(cat "$D/last-backup.txt")"
[[ -d "$BK" && -f "$BK/hyprland.conf" && -f "$BK/hyprpaper.conf" && -f "$BK/waybar-config" ]] || { echo "Backup incomplete: $BK" >&2; exit 1; }
# Preserve current configs before restoring in case user made new changes.
SNAP="$HOME/.local/share/shiori-crimson/backups/v3-rollback-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$SNAP"
for p in "$HOME/.config/hypr/hyprland.conf" "$HOME/.config/hypr/hyprpaper.conf" "$HOME/.config/waybar/config" "$HOME/.config/waybar/style.css"; do
  cp -- "$p" "$SNAP/$(basename "$(dirname "$p")")-$(basename "$p")"
done
# Only remove our specific launcher additions; preserve any user changes made since install.
/usr/bin/python3 - "$HOME/.config/hypr/hyprland.conf" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]); text=p.read_text()
text=re.sub(r'\n# BEGIN SHIORI_V3\n.*?# END SHIORI_V3\n?', '\n', text, flags=re.S)
text=re.sub(r'(?m)^# SHIORI_V3_ORIGINAL: (.*)$',r'\1',text)
p.write_text(text)
PY
/usr/bin/python3 "$D/hud/shiori_hud.py" stop >/dev/null 2>&1 || true
cp -- "$BK/hyprpaper.conf" "$HOME/.config/hypr/hyprpaper.conf"
cp -- "$BK/waybar-config" "$HOME/.config/waybar/config"
cp -- "$BK/waybar-style.css" "$HOME/.config/waybar/style.css"
if [[ -f "$BK/kitty.conf" ]]; then cp -- "$BK/kitty.conf" "$HOME/.config/kitty/kitty.conf"; fi
if [[ -f "$BK/kitty-was-absent" && -f "$HOME/.config/kitty/kitty.conf" ]]; then
  if grep -q '^# Shiori Crimson v3' "$HOME/.config/kitty/kitty.conf"; then rm -- "$HOME/.config/kitty/kitty.conf"; fi
fi
# Do not delete wallpapers or the backup; no monitor settings are altered.
if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]]; then
  hyprctl reload || true
  pkill -x waybar || true
  nohup waybar -c "$HOME/.config/waybar/config" -s "$HOME/.config/waybar/style.css" > "$HOME/.cache/shiori-v3-restore-waybar.log" 2>&1 </dev/null &
  pkill -x hyprpaper || true
  nohup hyprpaper > "$HOME/.cache/shiori-v3-restore-paper.log" 2>&1 </dev/null &
fi
printf 'Shiori v3 reversed. Previous Waybar/Hyprpaper/Kitty restored, v3 binding removed.\n'
printf 'Current files preserved in: %s\n' "$SNAP"
printf 'Your monitor geometry, AZERTY, audio and system settings were untouched.\n'
