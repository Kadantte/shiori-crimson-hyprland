# Release gates — Shiori Crimson Hyprland

## Repository/source candidate

- [x] Source archive reviewed structurally: 19/19 files
- [x] Originals hashed in `docs/source-provenance.json`
- [x] Machine-specific configs converted to explicit templates
- [x] Third-party brand PNG fallbacks removed from source/CSS
- [x] Local installed-app icon resolver added with offline fallback
- [x] No image files bundled without separate permission/registration
- [ ] Runtime icon rendering tested on Asura with GTK3, Waybar, native + Flatpak apps
- [ ] Dry-run config rendering tested with actual user-supplied wallpapers
- [ ] Independent source/security and licensing audit
- [x] Initial source and README screenshot commits pushed by the owner to GitHub (2026-11-23)

## Stable/release readiness

- [x] Original developer-reported manual checks: 5/5 passing
- [ ] ASUS launcher genuinely displays on ASUS (button click != popup placement)
- [ ] Async media calls / UI worst-case stall handling
- [ ] Cold login and long-run performance evidence
- [ ] Dock polling refactor acceptance or documented risk decision
- [ ] General installer and tested recovery, non-Asura monitor support
- [ ] Public artwork ownership confirmed per image and notices included
- [ ] Controlled deployment and rollback tests in spare account / VM

**Do not tag or announce a stable v3.4 release based on tests in this archive.**

## v0.1.0-beta.1 additional gate (experimental)

- [x] Source baseline and README screenshots present in repository candidate
- [x] Guarded fresh-test-account installer and hash-based rollback added (opt-in; not general installer)
- [x] Simulated fresh home install/rollback, no-overwrite, symlink and modified-file refusal unit tests
- [ ] Actual test-account/VM install and rollback observed by maintainer with LG monitor
- [ ] Actual GTK layer-shell and Waybar icon tests using installed apps and missing-app fallback
- [ ] Manual review of Asura-oriented video modes / AZERTY in config before test login
- [ ] GitHub Actions green on release commit, explicit signed tag and prerelease publication

**Interpretation:** Passing static checks does not approve installation on an existing user's machine. The beta is intended for technically proficient experimenters who have a spare account and a recovery path. No auto-update or unattended install.
