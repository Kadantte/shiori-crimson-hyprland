# Claude Code instructions — Shiori Crimson Hyprland

## Mission
Maintain a safe, public-beta repository for Shiori Crimson Hyprland, separately from the Shiori application. The known-good live baseline on Asura is v3.3.3.1. The v3.4 readiness audit has five passing manual tests, but the release gate remains pending.

## Safety policy

- **Never modify the live desktop** (`~/.config/hypr`, `~/.config/waybar`, user service files, active HUD/dock scripts, home dotfiles) without specific owner permission.
- No privileged commands, package installations/upgrades, logout/reboot, Hyprland reload, service restart, process termination, power management, GPU polling, or external network calls without task-specific authorization.
- Repository-local, requested changes are permitted after reviewing their effect; do not silently import personal files or overwrite existing repository content.
- Use dry-run first for source imports. Never follow symlinks or copy a directory wholesale.
- Treat Asura's connectors, monitor identifiers, keyboard layout and audio devices as machine-specific; parameterize for other systems.
- **Do not fabricate** missing live source, v3.4 fixes, timing data, historical commits, audits, or release approval.
- Every change needs tests, risk assessment, rollback notes and source provenance.
- Before GitHub publication, run local prepublication checks and manually review the staged diff, files, third-party licenses, screenshot/asset rights, and leaks.
- Original Kadantte-owned Shiori artwork is **free for private, personal non-commercial Shiori desktop use only**. Commercial use, resale, standalone redistribution or public reuse in another project require prior express written permission. The MIT license covers eligible original code and documentation only. Brand icons/logos from Google Chrome, Discord, Docker, etc. retain their owners' independent licensing/trademark terms; do not package them until distribution rights are verified, and never relicense them as Shiori assets.
- Do not push, create remote repositories, publish releases, or change repository visibility without explicit owner authorization.

## Release gate
Keep v3.3.3.1 as a known-good live reference; no v3.4 stable claim until code review, startup timing evidence, regression and rollback verification, and owner sign-off.
