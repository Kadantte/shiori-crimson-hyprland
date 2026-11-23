# Publishing Kadantte/shiori-crimson-hyprland

**Target:** https://github.com/Kadantte/shiori-crimson-hyprland. The owner already configured SSH/Git remote on Asura. **This ZIP does not create or push a GitHub repository.**

## Current state

19 real Shiori source files are included in this *beta source candidate*, together with modified portable templates and local icon resolver. There is **no approved installer or stable v3.4 tag**. The README must explicitly say **BETA / USE AT YOUR OWN RISK**. Asura's tested v3.3.3.1 environment is not modified by this package.

## Required before the first public push

1. Review all `git status` entries, new source and diffs. The original 19-file SHA256 manifest is in `docs/source-provenance.json`, and transformations are documented in `docs/2026-11-23-source-review.md`.
2. Run all tests, Python/Bash syntax checks and prepublish scanning. Review Git history for secrets separately; scripts only scan the current tree.
3. Test the Waybar local-installed-icon CSS generator and HUD pinned app icons on actual Asura hardware, without overwriting the live config. The wrapper is not proven in this sandbox.
4. Verify portable template generation, installation/rollback plans and dependency list in a test account/VM. Do not run legacy `activate.sh`/`restore.sh` casually.
5. Review each original image (if added later) for actual ownership and record public distribution approval in `assets/ASSET-REGISTER.csv`. Owner-owned artwork is personal/non-commercial-use only. No third-party Chrome/Discord/Docker/Spotify artwork is included here; those apps' local icons are resolved on the user's machine.
6. Obtain explicit owner sign-off before the first push, visibility change, tag or release.

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
