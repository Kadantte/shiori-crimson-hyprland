#!/usr/bin/env python3
"""Prepublication safety checks. No network calls, no writes; NOT a full security audit."""
from __future__ import annotations
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_TYPES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".bmp", ".ico", ".avif", ".heic"}
SECRET_PATTERNS = {
    "private key block": re.compile(r"-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----"),
    "GitHub classic token": re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    "GitHub fine-grained token": re.compile(r"github_pat_[A-Za-z0-9_]{60,}"),
    "AWS access key id": re.compile(r"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    "Slack token": re.compile(r"xox[baprs]-[0-9A-Za-z-]{20,}"),
    "possible hard-coded home path": re.compile(r"/home/[A-Za-z0-9_.-]+/"),
}
SENSITIVE_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "token.json", "known_hosts", "config.json.bak"}
SENSITIVE_ENDINGS = {".pem", ".p12", ".pfx", ".key", ".kdbx", ".sqlite", ".sqlite3", ".db"}
SKIP_DIRS = {".git", "__pycache__", ".venv", "build", "dist", ".pytest_cache", "_import-staging"}
MAX_SCAN_BYTES = 2_000_000


def collect_files(root: Path):
    for item in sorted(root.rglob("*")):
        relative = item.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if item.is_symlink() or item.is_file():
            yield item


def check(root: Path) -> list[str]:
    problems: list[str] = []
    registry = root / "assets" / "ASSET-REGISTER.csv"
    approved: set[str] = set()
    if registry.is_file():
        with registry.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rel = (row.get("path") or "").strip()
                if not rel:
                    problems.append("asset register contains a blank path")
                    continue
                if rel in approved:
                    problems.append(f"duplicate asset register path: {rel}")
                if (row.get("public_distribution_approved") or "").strip().lower() != "yes":
                    problems.append(f"asset without public-distribution approval: {rel}")
                if not (row.get("owner_or_licensor") or "").strip() or not (row.get("permission_basis") or "").strip():
                    problems.append(f"asset missing provenance or permission basis: {rel}")
                approved.add(rel)
    else:
        problems.append("missing assets/ASSET-REGISTER.csv")

    third_party = root / "assets" / "THIRD-PARTY-REGISTER.csv"
    third_records: dict[str, dict[str, str]] = {}
    if third_party.is_file():
        with third_party.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                path = (row.get("path") or "").strip()
                if not path:
                    problems.append("third-party register contains blank path")
                    continue
                if path in third_records:
                    problems.append(f"duplicate third-party register path: {path}")
                third_records[path] = row
    else:
        problems.append("missing assets/THIRD-PARTY-REGISTER.csv")

    present_images: set[str] = set()
    for item in collect_files(root):
        relative = item.relative_to(root).as_posix()
        if item.is_symlink():
            problems.append(f"symlink found: {relative} (manual review required)")
            continue
        if item.name in SENSITIVE_NAMES or item.suffix.lower() in SENSITIVE_ENDINGS:
            problems.append(f"sensitive file name: {relative}")
        if item.suffix.lower() in ASSET_TYPES:
            present_images.add(relative)
            if not relative.startswith("assets/"):
                problems.append(f"image outside registered assets/: {relative}")
            if relative not in approved:
                problems.append(f"image not registered with public-distribution approval: {relative}")
            brand_filename = item.stem.lower() in {"chrome", "discord", "docker"}
            if relative.startswith("assets/third-party/") or brand_filename:
                row = third_records.get(relative)
                if row is None:
                    problems.append(f"third-party image lacks separate rights record: {relative}")
                elif ((row.get("review_status") or "").strip().lower() != "approved"
                      or not (row.get("redistribution_basis") or "").strip()
                      or not (row.get("official_terms_url") or "").strip()
                      or not (row.get("source_url") or "").strip()):
                    problems.append(f"third-party image not cleared for redistribution: {relative}")
            continue
        if item.stat().st_size > MAX_SCAN_BYTES:
            problems.append(f"large file requires manual review: {relative}")
            continue
        try:
            content = item.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"binary or non-UTF8 file requires manual review: {relative}")
            continue
        for title, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                problems.append(f"{title} pattern in: {relative}")
    for path in sorted(approved - present_images):
        problems.append(f"asset register lists missing file: {path}")
    return problems


def main() -> int:
    errors = check(ROOT)
    print("Shiori Crimson prepublication check (heuristic, read-only)")
    if errors:
        for error in errors:
            print("ERROR:", error)
        print("FAIL: do not publish until manually reviewed and corrected.")
        return 1
    print("PASS: no flagged files or unapproved registered images detected.")
    print("NOTE: no ownership or license clearance is proven by this script.")
    print("NOTE: static scanning does not validate runtime safety, provenance or copyright.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
