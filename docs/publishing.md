# Publishing Kadantte/shiori-crimson-hyprland

**Target:** https://github.com/Kadantte/shiori-crimson-hyprland. The owner already configured SSH/Git remote on Asura. **This ZIP does not create or push a GitHub repository.**

## Current state

19 real Shiori source files are included, together with modified portable templates and a local icon resolver. A fresh-test-account-only experimental installer is included in beta.1; no general installer or stable v3.4 tag exists. The README must explicitly say **BETA / USE AT YOUR OWN RISK**. Asura's tested v3.3.3.1 environment is not modified by this package.

## Original public source publication checks (completed for source candidate)

1. Review all `git status` entries, new source and diffs. The original 19-file SHA256 manifest is in `docs/source-provenance.json`, and transformations are documented in `docs/2026-11-23-source-review.md`.
2. Run all tests, Python/Bash syntax checks and prepublish scanning. Review Git history for secrets separately; scripts only scan the current tree.
3. Test the Waybar local-installed-icon CSS generator and HUD pinned app icons on actual Asura hardware, without overwriting the live config. The wrapper is not proven in this sandbox.
4. Verify portable template generation, installation/rollback plans and dependency list in a test account/VM. Do not run legacy `activate.sh`/`restore.sh` casually.
5. Review each original image (if added later) for actual ownership and record public distribution approval in `assets/ASSET-REGISTER.csv`. Owner-owned artwork is personal/non-commercial-use only. No third-party Chrome/Discord/Docker/Spotify artwork is included here; those apps' local icons are resolved on the user's machine.
6. The owner completed and confirmed the initial public source push on 2026-11-23. A prerelease tag and release remain separately gated by the beta.1 checklist.

## Preview only

```bash
cd ~/Desktop/Projects/shiori-crimson-hyprland
python3 -m unittest discover -s tests -v
python3 scripts/prepublish.py
git status --short
git add -n .
git diff --check
```

Do not force-push to an existing repository. Do not claim this is stable or generally installable.

## v0.1.0-beta.1 prerelease publication

The code and README have already been published on GitHub; this prerelease adds an isolated-account installation experiment. Follow [release notes](releases/v0.1.0-beta.1.md) and [installation](installation.md). **Do not create the tag until a real disposable-account test has passed.** GitHub's *Set as a pre-release* checkbox must be enabled; do not mark this as latest stable.

The maintainer, not this source patch, performs signed commit/tag, push, GitHub prerelease and any uploaded archives. A public beta designation is not a claim that the installer can safely replace an existing Hyprland configuration.
