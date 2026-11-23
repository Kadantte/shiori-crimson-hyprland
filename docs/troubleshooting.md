# Troubleshooting (beta)

## Launcher opens on the wrong screen

Check the launcher entry point and associated Hyprland/GTK placement rules. The ASUS top-bar launcher and LG launcher both passed manual tests on Asura on 2026-11-23; a separate HUD code path was flagged as LG hard-pinned. Confirm which code is used before proposing edits.

## HUD slow or unresponsive

Check whether synchronous `playerctl`/MPRIS calls are blocking the UI when a media service is stalled. Existing normal-condition command latencies were low, but this is not proof of worst-case behavior. Avoid killing processes or injecting load during read-only diagnosis.

## Dock stale or high resource usage

Eight 3-second polling modules were observed. Inspect actual implementations, subprocess cost and redraw pattern before changing polling frequencies or replacing them with event-driven signals.

## Recovery

Do not delete live configuration or reload Hyprland just to troubleshoot. Use independent TTY access and known-good backups. See [installation design](installation.md).
