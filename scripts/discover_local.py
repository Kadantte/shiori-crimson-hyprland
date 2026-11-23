#!/usr/bin/env python3
"""List candidate Hyprland and Waybar file names without opening file content."""
from __future__ import annotations
import os
from pathlib import Path

HOME = Path.home()
CANDIDATES = [HOME / ".config/hypr", HOME / ".config/waybar"]


def main() -> None:
    print("Shiori Crimson read-only local source discovery")
    print("No files are copied, changed, read for content or uploaded.")
    for directory in CANDIDATES:
        print(f"\nCandidate directory: {directory}")
        if directory.is_symlink():
            print("  SKIPPED: directory is a symbolic link")
            continue
        if not directory.is_dir():
            print("  Not present")
            continue
        count = 0
        for root, subdirs, filenames in os.walk(directory, followlinks=False):
            subdirs[:] = [d for d in sorted(subdirs) if not (Path(root) / d).is_symlink()]
            for name in sorted(filenames):
                path = Path(root) / name
                if path.is_symlink():
                    print("  SKIPPED symlink:", path.relative_to(directory))
                    continue
                if not path.is_file():
                    continue
                print("  ", path.relative_to(directory))
                count += 1
                if count >= 500:
                    print("  Stopped after 500 files")
                    break
            if count >= 500:
                break
        print("  Visible candidate files:", count)
    print("\nOther HUD/dock sources require manual discovery; no full-home scan is performed.")


if __name__ == "__main__":
    main()
