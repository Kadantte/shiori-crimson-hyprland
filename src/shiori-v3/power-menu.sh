#!/usr/bin/env bash
# Shiori Crimson v3.3.2 — centered GTK power menu, safe Wofi fallback.
# The v3.3.1 launch.sh power action remains completely unchanged.
set -Eeuo pipefail
DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
case "${1:-}" in ''|--preview) ;; *) printf 'Usage: %s [--preview]\n' "$0" >&2; exit 2 ;; esac
if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] && \
   /usr/bin/python3 "$DIR/power_ui.py" --probe >/dev/null 2>&1; then
    exec /usr/bin/python3 "$DIR/power_ui.py" "$@"
fi
exec bash "$DIR/power-fallback.sh" "$@"
