# Changelog

## v0.1.0-beta.1 — experimental prerelease preparation (2026-11-23)

- Added guarded **fresh-test-account only** install/rollback with dry-run default, exact file-hash manifest, strict no-overwrite policy, and no live session/privileged actions.
- Added 7 isolated installer safety/rollback tests and release-notes/checklist documentation.
- Included the two owner-provided screenshots in the README; artworks remain under separate personal, non-commercial terms.
- **Known limitations:** LG-specific HUD and power UI; Asura-oriented monitor configuration; no deployable wallpapers; no real cross-machine GTK/Waybar install acceptance yet. This is not stable and must not be used for ordinary production desktops.

## Earlier — real-source beta candidate (2026-11-23)

- Imported 19-file Shiori desktop source-review snapshot into the repository, preserving execute bits and generating SHA256 provenance evidence.
- Added machine-specific config templates and a **non-installing** rendering preview tool.
- Removed three bundled third-party brand image CSS references and HUD's branded PNG fallback; added Gio/GTK local icon resolution for Waybar with generic fallback.
- Added source-level audit report, portability/installation caveats, and explicit beta readiness gates.
- This is **not** a stable v3.4 release; no actual Asura desktop configuration has been modified by the packaging work.
