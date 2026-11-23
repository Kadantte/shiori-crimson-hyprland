# Source architecture — 2026-11-23

The actual implementation is now present in `src/shiori-v3/` (19-file source ZIP imported) rather than being a placeholder.

```text
Hyprland (config templates, not directly deployable)
  ├─ session-init.sh → Wayland/XDG_DATA_DIRS environment
  ├─ start.sh → GTK3 HUD (Unix socket, resources + MPRIS + launcher)
  │    ├─ hud/shiori_hud.py → app_catalog.py → Gio.AppInfo
  │    └─ power-menu.sh → power_ui.py / power-fallback.sh
  └─ start-waybar.sh → render_waybar_icons.py → icon_resolver.py
      └─ Waybar: main bar / portrait bar / dock-state modules
            └─ dock_state.py → read-only hyprctl clients + focused window
```

The `launch.sh` actions focus existing application windows first and launch apps only if needed. `render_waybar_icons.py` resolves installed local app icons through Gio/GTK and writes a **cache-only** CSS overlay when Waybar is started via the wrapper. There are no bundled third-party icon binaries.

**Limitations:** The HUD launcher and power menu are pinned to LG hardware identity. The ASUS Waybar launcher button invokes the same HUD toggle socket, so the modal's actual placement needs independent validation. The media refresh runs multiple synchronous `playerctl` subprocesses, and eight dock modules poll every 3s. `activate.sh`/`restore.sh` can change running desktop state and are not approved installers. `shiori-cursor-reset` cycles a physical monitor and is opt-in only.

For review details, see [`2026-11-23-source-review.md`](2026-11-23-source-review.md).
