# Actual-source review — 2026-11-23 (candidate, NOT a release approval)

Source: user-supplied, 19-file ZIP, extracted and reviewed without running the code. SHA256 evidence is in [source-provenance.json](source-provenance.json). This repository copy is deliberately **not** a deployment of the source to Asura. Python syntax, Bash syntax, JSON, unit tests and heuristic checks are validated; a real Hyprland/GTK/Waybar runtime is **not available** in this packaging environment.

## Confirmed code behaviors

1. **Monitor routing:** `hud/shiori_hud.py` `find_lg()` selects an LG monitor by model/manufacturer or refuses startup. The central launcher window is initialized against that LG monitor and the socket `toggle` command has no monitor target. The ASUS Waybar button calls the same toggle. Therefore the button being clickable on ASUS **does not prove that the modal appears on ASUS**. Leave this behavior untouched until the developer tests a monitor-aware alternative.
2. **Synchronous UI commands:** `run()` calls `subprocess.run(timeout=3)` on the GTK main thread; `refresh_music()` makes multiple sequential playerctl calls; `refresh_gpu()` queries nvidia-smi on the UI thread once at startup and on demand. A slow subprocess can visibly stall the HUD even though normal measured times were ~5 ms. Asynchronous refactor remains an engineering task.
3. **Dock overhead:** Eight `custom/dock-*` modules invoke Python every 3 s; each state call may invoke two `hyprctl` commands. Approx. 160 dock-script launches/minute, potentially 320 `hyprctl` invocations/minute under healthy conditions. This is an upper-level work estimate, not a measured resource claim.
4. **Recovery / power:** `activate.sh` stops and restarts Waybar/hyprpaper; `restore.sh` copies old config files, may delete a generated Kitty file, and reloads Hyprland; `power_ui.py` can launch logout/reboot/shutdown after confirmation. None of these scripts were run here. **Do not execute `activate.sh` or `restore.sh` merely to test the repository.**
5. **Screen reset:** The Asura-specific cursor helper explicitly turns DP-6 off and back on after a delay. It is excluded from rendered default startup and should not be enabled on other machines.
6. **Network:** `launch.sh` can open the official Discord web app if Discord isn't installed. HUD artwork fetching can make HTTPS requests only to an explicit Spotify image-host allowlist, without redirects, with a 2MB cap and timeout. The launcher and other code do not require hosted third-party icon images.
7. **Artwork:** The real HUD refers to `album-fallback.png` and `shiori-menu-portrait.png`; the ZIP did **not** include those files. The candidate displays a generic album icon when the album image is absent. Original artwork may be added only after rights review and an approved entry in `assets/ASSET-REGISTER.csv`. See [asset licensing](../assets/ASSET-LICENSE.md).
8. **Machine specificity:** Monitor connectors, refresh rates, output geometry, input layout, audio environment, and power-menu wording currently reflect Asura. The config files are **templates**, not universal dotfiles. See [portability](portability.md).

## Source changes in this candidate compared to the uploaded ZIP

- Shipped all 19 code/config files in reviewed repository locations, with executable permissions preserved.
- Converted Hyprland/hyprpaper/Waybar personal path/output bindings to **renderable template tokens**. Removed the hardcoded Ethernet interface. Default cursor-reset autostart disabled.
- Replaced `exec-once = waybar` in the Hyprland template with `start-waybar.sh` (runs local app icon rendering on login **only after an explicit future installation**).
- Removed CSS references to three bundled Chrome, Discord and Docker PNGs. These binaries are **not included**.
- Removed HUD pinned-launcher PNG fallback; kept installed Gio icons and GTK theme fallbacks. Added missing album-art fallback without a bundled image.
- Added `icon_resolver.py`, `render_waybar_icons.py`, `start-waybar.sh` to generate Waybar icon backgrounds from installed desktop entries and theme files, in the user's cache only.
- Added configuration-preview rendering tool; deliberately **no installer** or automatic migration.
- Changed three blank dock-state fallback glyphs to neutral visible symbols.

## Outstanding before publishing a general-purpose release

- Real dual-monitor test on a **non-Asura** display layout and explicit ASUS-local popup placement.
- Real Waybar CSS/icon rendering test on Ubuntu 26.04 / GTK3 with native and Flatpak icons; verify Chrome, Discord, Docker and Spotify while installed and when missing.
- Apply/package and rollback plan validated in a test account or VM; no automatic installation script is supplied.
- Fresh-login and long-running profiling, with sync subprocess UI-stall fixes if needed.
- Confirm fonts, user-owned visual artwork, third-party terms and any added images. No images shipped in this candidate.
- Security audit including symlink paths, socket permissions, file reads and user-writable code paths.

**Release classification:** repository **beta source candidate**, not production-ready, not fully portable, not approved for final public release. The v3.3.3.1 Asura live desktop remains the known-good configuration.
