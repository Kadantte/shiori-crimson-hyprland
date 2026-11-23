# Installed-application icon policy

**No copies of Google Chrome, Discord, Docker or Spotify PNGs are shipped by this repository.** The icons are supplied locally by the user's installed applications and icon themes. This avoids redistributing those image binaries while supporting proper application identification.

## How it works

- The HUD's pinned launcher already uses `Gio.AppInfo.get_all()` and each matching app's `get_icon()`; this candidate removes the old local `assets/v3.2-icons/*.png` fallback. A generic themed icon appears if no matching application icon exists.
- Waybar's custom dock modules cannot directly embed arbitrary `GIcon` objects. The new `src/shiori-v3/render_waybar_icons.py` resolves local `.desktop` files by exact desktop ID first, then limited name fallbacks, asks GTK's installed icon theme for a *local filename*, and creates CSS `file://` background URLs.
- Generated CSS only writes to `~/.cache/shiori-crimson/`. There are **no web calls** to icon repositories and no downloading, bundling, or copying of brand binaries.
- The `start-waybar.sh` wrapper renders the CSS when Waybar starts; missing applications or missing GTK fall back to visible generic glyphs from `dock_state.py`.
- The icon CSS is recreated at the next Waybar start; newly installed apps require rerendering/restarting Waybar with user consent. No background polling is added.

Dry-run (no files written):

```bash
python3 src/shiori-v3/render_waybar_icons.py \
  --base configs/waybar/style.css \
  --output "$HOME/.cache/shiori-crimson/waybar-with-installed-icons.css"
```

To create a **cache-only preview** (still does not restart Waybar):

```bash
python3 src/shiori-v3/render_waybar_icons.py \
  --base configs/waybar/style.css \
  --output "$HOME/.cache/shiori-crimson/waybar-with-installed-icons.css" \
  --write --replace
```

Requirements: Python 3, PyGObject (`gi`), GTK3/Gio and a usable icon theme. Runtime behavior still needs validation on Asura. No part of the MIT license claims ownership of brand icons loaded from an installed app. See the trademark notices.
