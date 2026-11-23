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
- [ ] Actual public GitHub push authorized and verified

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
