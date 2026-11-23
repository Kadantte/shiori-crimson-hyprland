#!/usr/bin/env bash
# To be sourced ONLY by Shiori processes. Never fabricate DISPLAY/XWayland.
if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]]; then
  export XDG_SESSION_TYPE=wayland
  export XDG_CURRENT_DESKTOP=Hyprland
  _shiori_system_data="${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
  for _shiori_flatpak in "$HOME/.local/share/flatpak/exports/share" /var/lib/flatpak/exports/share; do
    case ":$_shiori_system_data:" in
      *":$_shiori_flatpak:"*) ;;
      *) _shiori_system_data="$_shiori_flatpak:$_shiori_system_data" ;;
    esac
  done
  export XDG_DATA_DIRS="$_shiori_system_data"
  unset _shiori_flatpak _shiori_system_data
fi
