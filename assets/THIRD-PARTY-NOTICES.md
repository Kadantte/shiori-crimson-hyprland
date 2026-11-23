# Third-party icon and brand notices

These notices document the relevant **upstream owners and terms**. They do **not** imply that Shiori Crimson owns a third-party mark, has received permission to ship a particular icon file, or can sublicense the artwork. **No third-party logo binaries are supplied in this repository kit.**

| Brand | Rights holder | Official terms / license source | Current Shiori status |
| --- | --- | --- | --- |
| Google Chrome | Google LLC | [Google Brand Resource Center](https://about.google/intl/en/brand-resource-center/brand-terms/), [Google trademark guidance](https://partnermarketinghub.withgoogle.com/brands/google/trademarks-and-terms/trademark-guidelines-for-proper-usage/) | Chrome icon candidate **withheld** pending file provenance and redistribution clearance |
| Discord | Discord Inc. | [Discord Brand Guidelines](https://discord.com/branding) | Discord icon candidate **withheld** pending file provenance and usage review |
| Docker | Docker Inc. | [Docker Trademark Guidelines](https://www.docker.com/legal/trademark-guidelines/), [Docker media resources](https://www.docker.com/company/newsroom/media-resources/) | Docker icon candidate **withheld** pending rights holder approval/allowance; official rules can be restrictive |

## Rules for future imports

1. Record **each actual file** in `assets/ASSET-REGISTER.csv` and, for company/brand assets, `assets/THIRD-PARTY-REGISTER.csv`.
2. Document who made the exact bytes, where the file came from, the exact license/permission relied upon, any required copyright notices, and whether repository redistribution and modifications are permitted.
3. Where the original creator is unknown or terms do not clearly authorize shipping the file in a public GitHub repository, **do not include it**. Linking to official terms alone does not establish permission.
4. Honor any naming, proportions, color, trademark or non-endorsement requirements. Do not alter logos if the brand rules prohibit that.
5. Prefer resolving an application's icon **locally at runtime** through the OS desktop entry (`Icon` field) or icon theme rather than bundling the brand artwork. This avoids redistributing private copies of brand icons, although runtime uses must still comply with applicable requirements.
6. Do not state or imply that Google, Discord, Docker, or any other brand endorses or is affiliated with Shiori Crimson.
7. The repo's MIT license and Kadantte's personal-use art license do **not** apply to external branding.

## Additional brands and code dependencies

Other icons, logos, fonts, themes, libraries, and third-party code must be individually recorded with their **own** exact license and attribution requirements. Use `assets/THIRD-PARTY-REGISTER.csv` for visual brands and `docs/third-party-code.md` for code/components. Keep mandatory original license copies where redistribution terms require them.

**Review date:** 2026-11-23. Official terms can change; re-check at publication time. This is a compliance inventory, not legal advice.
