# Licensing and public-distribution review

**A public repository is not proof of rights clearance.** This is a **mixed-license** project, and every imported file requires a provenance review.

| Content | Applicable terms | Release condition |
| --- | --- | --- |
| Original code/documentation owned by Kadantte | [MIT](../LICENSE) | Source and ownership verified |
| Original Kadantte-created artwork | [Personal, non-commercial use](../assets/ASSET-LICENSE.md) | Owner-controlled, explicitly approved for GitHub redistribution with personal-use grant |
| Google Chrome / Discord / Docker imagery | [Third-party notices](../assets/THIRD-PARTY-NOTICES.md) and official upstream guidelines | Exact image's source and distribution rights must be verified; currently **withheld** |
| Third-party fonts, themes, icon packs and code | Actual applicable upstream license | Preserve attribution/license texts, check redistribution/derivatives |
| Images found only in backups or caches | Unknown | Exclude until independently reviewed |

## Two registries

- `assets/ASSET-REGISTER.csv`: every actual image copied into the repo, with source, copyright/rights owner, permission basis and `public_distribution_approved=yes`.
- `assets/THIRD-PARTY-REGISTER.csv`: any proposed brand assets; requires source provenance, official brand terms, a **documented redistribution basis**, and `review_status=approved` before the image may be included.

A brand's `brand guidelines` link is NOT a blanket copyright license. For restrictive or unclear terms, use system-installed icon theme / .desktop icons at runtime or request authorization; do not upload its PNG to GitHub.

## Review tasks before pushing

1. Inspect actual 19 source/config files for home paths, URLs, secrets, executable commands, absolute asset paths and compatibility.
2. Keep backup and historic snapshots out of the repo; preserve `.gitignore` and inspect `git ls-files` not merely working tree.
3. Verify every artwork file's author and whether the project owner can allow personal non-commercial desktop redistribution.
4. Determine licensing and required notices for each third-party font, icon, library, and theme snippet.
5. Audit screenshot metadata and possible names, private services, artwork and window titles.
6. Run tests and `python3 scripts/prepublish.py`; manually inspect staged changes **and Git history**.
7. Do not add MIT headers to third-party code or brand artwork. Avoid falsely claiming the entire repository is MIT.

## Status (2026-11-23)

The user has identified 19 active code/configuration files on Asura, and a local ZIP was created **on Asura**. This kit does **not** include that ZIP; the actual code has not been reviewed here. The current packaging therefore remains **public beta starter / no complete install**. No brand-icon distribution has been approved based on file provenance.

## 2026-11-23 actual source candidate

The 19 reviewed *code/config* files have now been incorporated from an owner-provided ZIP. Their content is not automatically licensed by mere import; the owner must confirm authorship and rights before the MIT grant is relied upon. None of the requested pictures were present in the ZIP. Chrome/Discord/Docker/Spotify assets are not packaged; installed-system icons are referenced locally at runtime (see `docs/icon-resolution.md`). Any future included image requires an individual rights decision and registration.
