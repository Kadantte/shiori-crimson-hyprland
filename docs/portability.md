# Portability and manual configuration rendering

The upstream source was a machine-specific dual-monitor configuration. **The copied `configs/` files contain template markers (`{{...}}`) and are not valid live configurations until rendered.** Do not copy them verbatim into `~/.config`.

Render only to a *new preview directory* outside `~/.config`:

```bash
python3 scripts/render_config_templates.py \
  --main-output DP-6 --portrait-output DP-5 \
  --main-wallpaper "$HOME/Pictures/Wallpapers/landscape.png" \
  --portrait-wallpaper "$HOME/Pictures/Wallpapers/portrait.png" \
  --output "$HOME/Downloads/shiori-config-preview"
# Validates inputs; no writes unless --write is specified
```

Only after inspecting the proposed output, add `--write` to create that previously non-existent preview folder. It refuses to overwrite an existing preview and refuses `~/.config` as a destination.

**Manually review the rendered preview** before considering any installation: monitor resolution, scale, physical arrangement, refresh rate, `kb_layout = fr`, workspaces, multimedia shortcuts, audio output, installed tools, application launcher, existing desktop setup, and the power-menu monitor identity (currently LG-specific). The hardcoded GPU name display and `Asura` labels are not generalized. New users need their own configuration choices.

No `sudo`, package installation, Hyprland reload, live file replacement, automatic backup, or deployment is performed. The snapshot's `restore.sh` is *historical deployment logic*, not a safe universal uninstaller; do not use it on another host. A future installer must use explicit per-file consent, preflight, backup verification, dry-run and rollback tests before release.
