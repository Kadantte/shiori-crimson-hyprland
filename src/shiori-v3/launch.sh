#!/usr/bin/env bash
# Shiori v3.3 reconciled launchers, focusing open Hyprland windows first.
set -Eeuo pipefail
D="$HOME/.config/shiori-v3"
[[ -r "$D/session-env.sh" ]] && source "$D/session-env.sh"
LOG_DIR="${XDG_CACHE_HOME:-$HOME/.cache}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/shiori-v3.3-launch.log"
log() { printf '%s %s\n' "$(date '+%F %T')" "$*" >> "$LOG"; }
launch_detached() { log "launch: $*"; nohup "$@" >> "$LOG" 2>&1 </dev/null & }
find_chrome() {
  for cmd in google-chrome-stable google-chrome chromium chromium-browser; do
    if command -v "$cmd" >/dev/null 2>&1; then printf '%s\n' "$cmd"; return 0; fi
  done
  return 1
}
notify_missing() {
  if command -v notify-send >/dev/null 2>&1; then
    notify-send 'Shiori Crimson' "$1" || true
  else printf '%s\n' "$1" >&2; fi
}
focus_if_open() {
  if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] && command -v hyprctl >/dev/null 2>&1; then
    if /usr/bin/python3 "$D/dock_state.py" focus "$1"; then
      log "focus: $1 existing Hyprland window"
      return 0
    fi
  fi
  return 1
}
APP="${1:-launcher}"
case "$APP" in
  chrome|code|kitty|nautilus|monitor|discord|spotify|docker)
    if focus_if_open "$APP"; then exit 0; fi ;;
esac
case "$APP" in
  launcher)
    /usr/bin/python3 "$D/hud/shiori_hud.py" toggle 2>/dev/null || wofi --show drun --allow-images
    exit 0 ;;
  chrome)
    if browser="$(find_chrome)"; then launch_detached "$browser"; exit 0; fi
    notify_missing 'Google Chrome was not found.'; exit 1 ;;
  code)
    # Proven Asura launch path; do not rely on a missing X display.
    for cmd in code codium; do
      if command -v "$cmd" >/dev/null 2>&1; then
        launch_detached env XDG_SESSION_TYPE=wayland "$cmd" --ozone-platform=wayland
        exit 0
      fi
    done
    notify_missing 'VS Code / VSCodium not found.'; exit 1 ;;
  kitty|nautilus|monitor)
    case "$APP" in kitty) cmd=kitty ;; nautilus) cmd=nautilus ;; monitor) cmd=gnome-system-monitor ;; esac
    if command -v "$cmd" >/dev/null 2>&1; then launch_detached "$cmd"; exit 0; fi
    notify_missing "$cmd was not found."; exit 1 ;;
  discord)
    if command -v flatpak >/dev/null 2>&1 && flatpak info com.discordapp.Discord >/dev/null 2>&1; then
      log 'Discord Flatpak: native Wayland'
      launch_detached env XDG_SESSION_TYPE=wayland flatpak run com.discordapp.Discord --ozone-platform=wayland
      exit 0
    fi
    for cmd in discord discord-canary Discord; do
      if command -v "$cmd" >/dev/null 2>&1; then
        log "Discord native: native Wayland ($cmd)"
        launch_detached env XDG_SESSION_TYPE=wayland "$cmd" --ozone-platform=wayland
        exit 0
      fi
    done
    if browser="$(find_chrome)"; then launch_detached "$browser" --new-window https://discord.com/app; exit 0; fi
    notify_missing 'Discord Flatpak/native and Chrome are unavailable.'; exit 1 ;;
  spotify)
    if command -v flatpak >/dev/null 2>&1 && flatpak info com.spotify.Client >/dev/null 2>&1; then
      log 'Spotify Flatpak: native Wayland'
      launch_detached env XDG_SESSION_TYPE=wayland flatpak run com.spotify.Client --ozone-platform=wayland
      exit 0
    fi
    if command -v spotify >/dev/null 2>&1; then
      launch_detached env XDG_SESSION_TYPE=wayland spotify --ozone-platform=wayland; exit 0
    fi
    notify_missing 'Spotify Flatpak/native was not found.'; exit 1 ;;
  docker)
    if command -v docker-desktop >/dev/null 2>&1; then launch_detached docker-desktop; exit 0; fi
    if command -v kitty >/dev/null 2>&1 && command -v lazydocker >/dev/null 2>&1; then
      launch_detached kitty --title 'Shiori Docker' lazydocker; exit 0
    fi
    if command -v kitty >/dev/null 2>&1 && command -v docker >/dev/null 2>&1; then
      launch_detached kitty --title 'Shiori Docker' bash -lc 'printf "Docker containers (read-only):\n"; docker ps; printf "\n"; exec bash'; exit 0
    fi
    notify_missing 'Docker Desktop / lazydocker / Docker CLI not found.'; exit 1 ;;
  power)
    exec bash "$D/power-menu.sh" ;;
  *) echo "Unsupported Shiori launch action: $APP" >&2; exit 2 ;;
esac
