# Installation and recovery — beta source candidate (not an installer)

**No reviewed general-purpose installer exists. This documentation is not authorization to change your running desktop.** All files under `configs/` require rendering and careful review before live use. A fresh clone by itself changes nothing.

## Inspect and test only

1. Clone/download to a regular project directory, not directly to `~/.config`.
2. Run `python3 -m unittest discover -s tests -v`, `python3 scripts/prepublish.py`, `bash -n ...`, and `python3 -m compileall` in the project.
3. Review `docs/2026-11-23-source-review.md` for behaviors requiring caution.
4. Use `docs/portability.md` to **dry-run rendering**; create a preview only on a new path outside your live config.
5. Inspect preview monitor/output configuration and all external dependencies before proposing an installation.

## Dependencies (not auto-installed)

Hyprland/Wayland, Waybar, hyprpaper, Python 3, GTK3/GObject introspection (`python3-gi`), GTK layer-shell introspection bindings, `python3-psutil`; plus optional `playerctl`, `nvidia-smi` on NVIDIA, `wofi`, `zenity`, `kitty`, `mako`, `nm-applet`, `hyprlock`/`swaylock`, and GTK theme icons. Flatpak/Snap desktop integration is best-effort. Requirements and package names vary by distribution.

## Deployment is not validated

The included `src/shiori-v3/activate.sh` deliberately **restarts Waybar and hyprpaper**; `restore.sh` changes configs, may remove generated Kitty configuration and reloads Hyprland. These are archived as developer source, **not** approved one-click installation or rollback tools. Do not execute them to validate the ZIP.

A production installer needs: test-account validation, explicit monitor mapping, dependency verification, backup inventory and hashes, per-file consent, no unexpected symlinks, transaction-like apply, independent TTY rollback, and interactive startup testing. The Asura cursor reset is not enabled by default in templates.
