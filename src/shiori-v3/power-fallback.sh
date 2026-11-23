#!/usr/bin/env bash
# Shiori Crimson v3.3.1 — safe power menu for Asura / Hyprland.
# All destructive actions require an explicit second confirmation.
set -Eeuo pipefail
DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${XDG_CACHE_HOME:-$HOME/.cache}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/shiori-v3.3.1-power.log"
log() { printf '%s %s\n' "$(date '+%F %T')" "$*" >> "$LOG"; }
notice() {
    log "$*"
    if command -v notify-send >/dev/null 2>&1; then
        notify-send 'Shiori Crimson · Power' "$*" >/dev/null 2>&1 || true
    else
        printf '%s\n' "$*" >&2
    fi
}

# Preview is a safe, non-executing way to inspect the menu's appearance.
PREVIEW=0
case "${1:-}" in
    '') ;;
    --preview) PREVIEW=1 ;;
    *) printf 'Usage: %s [--preview]\n' "$0" >&2; exit 2 ;;
esac

can_lock=0
if command -v hyprlock >/dev/null 2>&1 || command -v swaylock >/dev/null 2>&1; then
    can_lock=1
fi
options=('Log Out' 'Restart' 'Shut Down' 'Cancel')
if ((can_lock)); then options=('Lock Screen' "${options[@]}"); fi

# Prefer themed Wofi under Wayland, with Zenity as a GTK fallback.
select_action() {
    if command -v wofi >/dev/null 2>&1; then
        printf '%s\n' "${options[@]}" | wofi --dmenu --prompt 'SHIORI // ASURA POWER' \
            --style "$DIR/power-menu.css" --location center --width 440 --height 320 2>> "$LOG"
    elif command -v zenity >/dev/null 2>&1; then
        zenity --list --title='Shiori Crimson · Power' \
            --text='Choose an action for Asura' --column='Action' --print-column=1 \
            --width=420 --height=340 "${options[@]}" 2>> "$LOG"
    else
        notice 'Neither wofi nor zenity is available; no action taken.'
        return 1
    fi
}

confirm_action() {
    local label="$1" message="${2:-}"
    if command -v wofi >/dev/null 2>&1; then
        local answer
        answer="$(printf 'Cancel\nYes, %s\n' "$label" | wofi --dmenu \
            --prompt "$message" --style "$DIR/power-menu.css" \
            --width 460 --height 190 2>> "$LOG")" || return 1
        [[ "$answer" == "Yes, $label" ]]
    elif command -v zenity >/dev/null 2>&1; then
        zenity --question --title='Shiori Crimson · Confirm' \
            --text="$message" --ok-label="$label" --cancel-label='Cancel' \
            --width=440 2>> "$LOG"
    else
        return 1
    fi
}

run_action() {
    local action="$1"; shift
    log "confirmed action: $action"
    if "$@" >> "$LOG" 2>&1; then
        log "action returned successfully: $action"
    else
        local rc=$?
        notice "$action could not be completed (exit $rc). See $LOG"
        return "$rc"
    fi
}

action="$(select_action)" || exit 0
case "$action" in
    'Cancel'|'') exit 0 ;;
    'Lock Screen'|'Log Out'|'Restart'|'Shut Down') ;;
    *) notice 'Unrecognized menu selection; no action taken.'; exit 0 ;;
esac
if ((PREVIEW)); then
    notice "Preview only: selected $action. No action performed."
    exit 0
fi

case "$action" in
    'Lock Screen')
        if command -v hyprlock >/dev/null 2>&1; then
            run_action 'Lock Screen' hyprlock
        elif command -v swaylock >/dev/null 2>&1; then
            run_action 'Lock Screen' swaylock
        else
            notice 'No compatible screen locker is installed.'
        fi ;;
    'Log Out')
        if [[ -z "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]]; then
            notice 'This logout command only runs from a Hyprland session.'
            exit 1
        fi
        if confirm_action 'Log Out' 'Log out of Hyprland? Save your work first.'; then
            run_action 'Log Out' hyprctl dispatch exit
        fi ;;
    'Restart')
        if confirm_action 'Restart' 'Restart Asura? Unsaved work will be lost.'; then
            run_action 'Restart' systemctl reboot
        fi ;;
    'Shut Down')
        if confirm_action 'Shut Down' 'Shut down Asura? Unsaved work will be lost.'; then
            run_action 'Shut Down' systemctl poweroff
        fi ;;
esac
