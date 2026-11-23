# Compatibility — candidate source, not generally validated

**Observed reference:** Ubuntu 26.04.1 LTS, Hyprland 0.53.x, LG DP-6 (2560×1440, landscape), ASUS DP-5 (portrait), NVIDIA RTX 3080 Ti, French AZERTY.

The 19-file real source has been included for inspection. Templates can render connector/path values for other machines, **but the HUD and power UI still select LG hardware by model** and the keyboard, audio, monitor geometry, and Waybar fonts are Asura-specific. A general release must introduce and test actual configurable monitors, fallback behavior, and a safe installer. No other distributions have been tested here.

**Required runtime components:** Hyprland, Waybar, Python 3, PyGObject/GTK3, gtk-layer-shell introspection bindings, psutil, icon theme and supporting desktop tools. Optional: Flatpak/Snap integration, playerctl, nvidia-smi (NVIDIA only), wofi, zenity, GNOME Settings, hyprlock/swaylock, kitty, hyprpaper. Check package availability per Linux distribution.

No release should assume the names `DP-5` and `DP-6`, one Ethernet device, NVIDIA, or a specific monitor arrangement. See [`2026-11-23-source-review.md`](2026-11-23-source-review.md).
