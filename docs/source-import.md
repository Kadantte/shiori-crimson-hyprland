# Source import and provenance — completed for candidate, not yet a release

The user-supplied `shiori-source-review.zip` contained **19 source/configuration files**. These were inspected and incorporated into this repository candidate on 2026-11-23. The unmodified original file checksums and archive hash are recorded in [`source-provenance.json`](source-provenance.json). The new public source is **not a verbatim archive**: review [`2026-11-23-source-review.md`](2026-11-23-source-review.md) for the exact adjustments (template substitutions, brand icon changes, fallback behavior).

No image binaries were included in the upload, so no user-owned artwork or third-party brand images were bundled. No service or live config was altered in Asura by the import.

## Source structure

- `src/shiori-v3/`: application, HUD, dock state, power menu and session helpers; `activate.sh` and `restore.sh` are **potentially disruptive** and must **not be used for testing**.
- `configs/hypr/`: **templates** for developer monitor layout and hyprpaper; not directly deployable.
- `configs/waybar/`: **templates** plus CSS baseline with runtime icon backgrounds separated.
- `scripts/helpers/`: on-demand GPU status and an opt-in **Asura-specific** display-reset utility.

## Future changes

Use git diffs and unit tests before each alteration. Never copy entire live configuration directories or their backups into Git. The existing `scripts/review_source_archive.py` is retained for independent verification of older source ZIPs; private `_import-staging/` is ignored from Git and by the heuristic publication scanner. Importing another snapshot over these reviewed files requires explicit per-file diff review, not the overwrite-by-default utility.

For portability, see [`portability.md`](portability.md); for icon resolution, see [`icon-resolution.md`](icon-resolution.md). The final public release still needs owner authorization after runtime checks and rights review.
