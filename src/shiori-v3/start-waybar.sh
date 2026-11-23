#!/usr/bin/env bash
# Starts Waybar, resolving custom dock icons from locally installed apps.
# Invocation is an explicit session-start action, not part of repo installation.
set -Eeuo pipefail
DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BASE="$HOME/.config/waybar/style.css"
OUTPUT="$HOME/.cache/shiori-crimson/waybar-with-installed-icons.css"
STYLE="$BASE"
if command -v python3 >/dev/null 2>&1 && [[ "$OUTPUT" == "$HOME/.cache/shiori-crimson/"* ]]; then
  if python3 "$DIR/render_waybar_icons.py" --base "$BASE" --output "$OUTPUT" --write --replace >/dev/null 2>&1; then
    STYLE="$OUTPUT"
  fi
fi
exec waybar -c "$HOME/.config/waybar/config" -s "$STYLE"
