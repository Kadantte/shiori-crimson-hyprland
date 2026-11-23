# Shiori Crimson Hyprland ⛩️

> **v0.1.0-beta.1 — EXPERIMENTAL PRERELEASE. NOT STABLE.** Use at your own risk. A guarded installer is available **only for fresh, disposable test accounts on LG-compatible setups**. It is not validated on an everyday desktop and will refuse existing configuration files. Never run historic `activate.sh` or `restore.sh` to install this beta.

A crimson-themed Hyprland / Wayland desktop setup featuring a GTK3 layer-shell HUD, application launcher, three Waybar bars, dock-state feedback, power menu and a dual-monitor desktop concept. Developed on Asura (Ubuntu 26.04, Hyprland 0.53.x). Owned/maintained by [Kadantte](https://github.com/Kadantte). Public repository: [Kadantte/shiori-crimson-hyprland](https://github.com/Kadantte/shiori-crimson-hyprland).

## Screenshots

A preview of Shiori Crimson running on **Asura**. These are real desktop captures, not installation previews; the appearance and monitor layout may change during beta development.

### Desktop overview

<p align="center">
  <img src="assets/screenshots/shiori-desktop-overview.png" alt="Shiori Crimson Hyprland desktop on Asura, featuring a crimson wallpaper, Waybar and bottom dock" width="1000">
</p>

### Fastfetch system identity

<p align="center">
  <img src="assets/screenshots/shiori-fastfetch-asura.png" alt="Shiori Crimson themed Fastfetch terminal displaying Asura's system information" width="850">
</p>

> **Screenshots and artwork:** These images are supplied to demonstrate the project and include Shiori Crimson character art. Personal, non-commercial desktop use is allowed only as described in the [artwork license](assets/ASSET-LICENSE.md); separate redistribution, commercial use and sale require permission. Third-party logos and icons visible **inside screenshots** retain their respective owners' rights. Screenshots may show developer-specific system information and do not represent universal defaults.

## v0.1.0-beta.1 — Try it safely

This is an **experimental source prerelease**, not a production installer. Read the [beta release notes](docs/releases/v0.1.0-beta.1.md) and [fresh-test-account installation guide](docs/installation.md) first. The new `scripts/beta_install.py` has a dry-run `plan` and a narrowly gated `install`/`rollback` flow. It **will not overwrite an existing Hyprland/Waybar/Shiori configuration** and refuses to install or roll back from an active Hyprland session. We have only tested the installer against temporary simulated home directories; real GTK/layer-shell behavior still needs an independent test in a disposable account or VM.

**Screenshots are documentation, not installable wallpapers.** Bring your own locally available landscape/portrait images with the appropriate rights. The HUD and power menu still require an LG monitor; the `hyprland.conf` source still includes Asura-oriented display settings and AZERTY. Other hardware is **not currently supported by the beta installer**. No packages or services are installed automatically.

## State of the project

- **Real source imported:** 19 code/config files from the developer's working Asura snapshot, with provenance recorded in [`docs/source-provenance.json`](docs/source-provenance.json).
- **Baseline:** v3.3.3.1 working desktop on Asura. **v3.4 engineering readiness remains open.** Don't interpret this source candidate as a finished v3.4 release.
- **Guarded test-account installer:** optional, explicit opt-in, never overwrites existing configs or starts services. Templates, HUD and power UI remain LG/Asura-specific; do not run it on your daily Asura login.
- **Artwork:** only the two documentation screenshots below are included; deployable wallpaper/character-art binaries are not packaged. Screenshots follow the separate personal/non-commercial image license. Third-party app icons are resolved from installed applications, not redistributed as standalone images.

### Features in the source

| Component | Notes |
| --- | --- |
| Hyprland | Developer's dual-output concepts; monitor connectors/refresh rates and AZERTY are **personal settings**, not defaults for everyone |
| Waybar | Top bars on main/portrait plus bottom application dock with focus/running states |
| HUD | GTK3 / gtk-layer-shell resource/media widgets and search launcher |
| Applications | Gio desktop-entry discovery, Flatpak-aware environment, fast search observed on Asura |
| Icons | Native `Gio.AppInfo` in launcher; cache-only Waybar CSS generated from installed app icons |
| Power menu | Lock/logout/reboot/shutdown with explicit confirmation; **do not test casually** |

## How to inspect safely

```bash
python3 -m unittest discover -s tests -v
python3 scripts/prepublish.py
python3 -m compileall -q src/shiori-v3 scripts
bash -n src/shiori-v3/*.sh src/shiori-v3/start-waybar.sh scripts/helpers/*.sh
```

See [portability and preview rendering](docs/portability.md), [source review findings](docs/2026-11-23-source-review.md), [icon-resolution design](docs/icon-resolution.md), and [installation and recovery](docs/installation.md). The rendering tool creates previews **outside live config** and does not enable or restart anything.

## Install/test prerequisites

- Requires a **fresh disposable Linux user account**, a supported Hyprland session, an LG primary monitor, manually installed runtime dependencies and two separately supplied wallpapers. **Not for an existing daily desktop or a VM without appropriate test displays.**
- Start with `python3 scripts/beta_install.py plan --help` and follow [docs/installation.md](docs/installation.md) for exact commands. Plan runs without writing files; installation requires an explicit consent phrase and acknowledgement of the LG-only constraint.
- Use `python3 scripts/beta_install.py rollback` for a read-only uninstall preview. Rollback removes **only files the installer created and that have not been modified**. It does not reset services, reinstall dependencies or delete your wallpapers. Run rollback outside Hyprland.

## Important limits

The ASUS Waybar launcher button passed manual click testing, but source inspection shows that the **HUD launcher itself currently targets the LG monitor**. This is not yet a general per-monitor popup solution. Multiple synchronous media subprocess calls may block the UI under stalls; the dock polls multiple scripts every 3 s. Real test-account installation/rollback, portability work, and independent security/licensing review remain prerequisites for broader release endorsement.

## License and intellectual property

- **Original project code/documentation:** MIT, to the extent the maintainer holds the applicable rights. [LICENSE](LICENSE).
- **Original Shiori picture assets:** **All rights reserved with a limited personal, non-commercial desktop-use permission** for individually approved and included files. Selling, monetizing, reselling or independently redistributing them is not permitted without prior express written permission. [Artwork license](assets/ASSET-LICENSE.md).
- **Chrome, Discord, Docker, Spotify and other brand assets:** remain the property of their respective owners, and may be loaded from their installed apps. **Not bundled, sublicensed, or covered by MIT.** See [brand notices](assets/THIRD-PARTY-NOTICES.md).
- **Fonts and third-party code:** retain their original terms. [License review](docs/licensing-review.md).

This repository is an independent desktop customization. It does not claim sponsorship, endorsement or affiliation with Google, Discord, Docker, Spotify, Canonical, or the Hyprland maintainers. This Linux project is separate from the Shiori Windows anime/manga application.

**Beta safety:** Test in a spare account/VM with TTY recovery before attempting any real install. Keep known-good backups, avoid forceful compositor changes, and do not run `activate.sh`, `restore.sh`, power actions or a cursor-reset utility merely to inspect this repository.
