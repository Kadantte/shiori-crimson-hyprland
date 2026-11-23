#!/usr/bin/env bash
# Hyprland-only login integration, idempotent, non-privileged.
set -u
[[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] || exit 0
source "$HOME/.config/shiori-v3/session-env.sh"
mkdir -p "$HOME/.cache"
log="$HOME/.cache/shiori-v3.3-session.log"
{
  echo "[$(date -Is)] Shiori environment initialization"
  printf 'XDG_SESSION_TYPE=%s XDG_CURRENT_DESKTOP=%s WAYLAND_DISPLAY=%s\n' \
    "${XDG_SESSION_TYPE:-unset}" "${XDG_CURRENT_DESKTOP:-unset}" "${WAYLAND_DISPLAY:-unset}"
  if command -v dbus-update-activation-environment >/dev/null 2>&1; then
    # Export only known desktop variables. Do not export secrets or the entire environment.
    dbus-update-activation-environment --systemd \
      XDG_SESSION_TYPE XDG_CURRENT_DESKTOP XDG_DATA_DIRS \
      WAYLAND_DISPLAY HYPRLAND_INSTANCE_SIGNATURE || echo 'DBus import failed; investigate user session.'
  fi
  if command -v systemctl >/dev/null 2>&1; then
    systemctl --user import-environment XDG_SESSION_TYPE XDG_CURRENT_DESKTOP \
      XDG_DATA_DIRS WAYLAND_DISPLAY HYPRLAND_INSTANCE_SIGNATURE || echo 'Systemd-user import failed.'
  fi
} >> "$log" 2>&1
exit 0
