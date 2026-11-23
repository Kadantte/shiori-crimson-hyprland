# v0.1.0-beta.1 — disposable test-account installation and rollback

> **Experimental / at your own risk. Not approved for daily use.** The project remains a public beta. **Never install over Asura's working environment**, existing Hyprland or Waybar dotfiles, or a machine you cannot recover from a TTY. The original wallpapers are NOT included; README screenshots are not wallpaper assets. The HUD and power menu currently require a physically detected LG monitor; Asura-specific screen modes and French keyboard layout remain in the template. Do not attempt this on other hardware until the monitor handling is generalized and tested.

## Requirements

- Ubuntu 26.04-era Linux with Hyprland and a working login/TTY recovery path; two display outputs available. **Test in a separate disposable Linux user account, not the account currently running Shiori Crimson.**
- Already-installed packages/binaries: `hyprctl`, `waybar`, `hyprpaper`, Python 3, GTK 3, PyGObject (`gi`), GtkLayerShell 0.1, `psutil`; plus `kitty`, `mako`, `nm-applet`, `playerctl`, `wpctl` for particular features. Names/packaging vary. The installer does not run any package manager or use `sudo`.
- A physical LG display is required for the current HUD and power menu implementation. No automatic monitor/GPU detection or configuration occurs in the installer. Confirm output names, supported refresh rates, transform, and workspace layout yourself before signing in.
- Two user-owned/readable local wallpaper files with normal, non-symlink paths. Check portrait rotation and paths. The installer **references** images, never copies or uploads them.

## Read-only preparation in your fresh test account

Run commands **as the disposable test user**, never with sudo:

```bash
cd ~/Desktop/Projects/shiori-crimson-hyprland
python3 -m unittest discover -s tests -v
python3 scripts/prepublish.py
python3 scripts/beta_install.py plan \
  --main-output DP-6 --portrait-output DP-5 \
  --main-wallpaper "$HOME/Pictures/landscape.png" \
  --portrait-wallpaper "$HOME/Pictures/portrait.png"
```

The monitor connectors and paths above are **examples**, not guesses about your machine. Verify them independently (e.g. `hyprctl monitors` in a separate, temporary session). The plan refuses if any installation destination file already exists, or a link redirects it. It does not touch or restart your current desktop. Review the exact resulting configuration via `scripts/render_config_templates.py --help` and the documented preview renderer before attempting an install. **Do not install until you have manually verified the Asura-specific monitor modes and input settings in the template.**

## Opt-in install — only in an empty fresh test home

The tool installs new files to `~/.config/hypr/`, `~/.config/waybar/` and `~/.config/shiori-v3/` and creates an exact-hash installation manifest at `~/.local/state/shiori-crimson-beta1/install.json`. It does NOT install dependencies, start Waybar, reload Hyprland, log out or reboot. It refuses existing files, running Hyprland sessions, missing required command binaries, or missing consent.

Only after inspecting the source, installation plan, layouts and requirements above, from a **non-Hyprland TTY or login** in the disposable test user:

```bash
python3 scripts/beta_install.py install \
  --main-output DP-6 --portrait-output DP-5 \
  --main-wallpaper "$HOME/Pictures/landscape.png" \
  --portrait-wallpaper "$HOME/Pictures/portrait.png" \
  --ack-lg-only --confirm INSTALL-SHIORI-BETA-TEST-ACCOUNT --apply
```

**Do not do this in Asura's main account.** On next test Hyprland login, logs can be found in the test account's `~/.cache/` if the session components run. Power UI buttons perform real logout/reboot/shutdown after confirmation—do not use them during smoke tests. The historic `src/shiori-v3/activate.sh` and `restore.sh` are deliberately NOT installed. No claim of runtime compatibility follows from the static test suite.

## Rollback and recovery

From a TTY or another **non-Hyprland session** as the same disposable test user:

```bash
python3 scripts/beta_install.py status
python3 scripts/beta_install.py rollback
# Review the preview. If all tracked files are unchanged:
python3 scripts/beta_install.py rollback --apply \
  --confirm ROLLBACK-SHIORI-BETA
```

The rollback checks SHA256 digests of **every tracked file before it removes any of them**. If a file changed or disappeared unexpectedly, rollback refuses to delete anything; preserve its contents and investigate. A pending manifest can also help recover a partially interrupted installation. Rollback removes only manifest-listed unchanged files and empty directories, never wallpapers or other user files. It does not restart or reload desktop components. Retain a TTY and alternate session for recovery.

## Known limitations and non-goals

- The original HUD and power UI are LG-model pinned. Portrait Waybar button presence is not proof of an ASUS-local launcher popup. The installer does not fix those behaviors.
- The display modes and `kb_layout = fr` are still Asura-oriented. The installer is a **controlled test facility**, not a generalized setup wizard.
- The beta has no deployable Shiori character wallpaper bundled. Use your own appropriately licensed pictures.
- The code still has synchronous media commands and periodic dock polling. No unattended installation, updates, privileged operations, automatic backups of existing dotfiles, or production migration is supported.
