#!/usr/bin/env python3
"""
Check for new Etsy Open API releases on GitHub.

Fetches releases from https://github.com/etsy/open-api/releases and compares
against the last checked release stored in specs/last-release-check.json.

Usage:
    python scripts/check_releases.py              # Check for new releases
    python scripts/check_releases.py --update      # Mark latest release as checked
    python scripts/check_releases.py --update TAG  # Mark specific release as checked

Exit codes:
    0 - New releases found (report saved to specs/release-notes.md)
    1 - Up to date (no new releases)
    2 - Error (network, file I/O, etc.)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

GITHUB_RELEASES_URL = "https://api.github.com/repos/etsy/open-api/releases"

DEFAULT_STATE = {
    "last_checked_release": "3.0.0-general-release-2025-01-06",
    "last_checked_date": "2025-01-06T19:29:43Z",
}


def load_state(state_path: Path) -> dict:
    """Read the last-release-check state file, or return defaults if missing."""
    if state_path.exists():
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return dict(DEFAULT_STATE)


def save_state(state_path: Path, state: dict) -> None:
    """Write state as formatted JSON."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")


def fetch_releases() -> list[dict]:
    """Fetch releases from the GitHub API."""
    response = requests.get(
        GITHUB_RELEASES_URL,
        params={"per_page": 50},
        headers={"Accept": "application/vnd.github+json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def parse_date(date_str: str) -> datetime:
    """Parse a GitHub API date string into a UTC datetime."""
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )


def filter_new_releases(releases: list[dict], last_checked_date: str) -> list[dict]:
    """Filter releases published after the last checked date, sorted oldest-first."""
    cutoff = parse_date(last_checked_date)
    new = [
        r
        for r in releases
        if r.get("published_at") and parse_date(r["published_at"]) > cutoff
    ]
    new.sort(key=lambda r: parse_date(r["published_at"]))
    return new


def generate_report(releases: list[dict]) -> str:
    """Produce a markdown report of new releases."""
    lines = ["# Etsy Open API — New Releases", ""]
    lines.append(f"Found **{len(releases)}** new release(s).\n")

    for release in releases:
        name = release.get("name") or release.get("tag_name", "Unknown")
        tag = release.get("tag_name", "")
        url = release.get("html_url", "")
        published = release.get("published_at", "")
        body = release.get("body", "").strip()

        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"- **Tag**: `{tag}`")
        lines.append(f"- **Published**: {published}")
        lines.append(f"- **URL**: {url}")
        lines.append("")
        if body:
            lines.append(body)
        else:
            lines.append("_No release notes provided._")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def cmd_check(state_path: Path, report_path: Path) -> int:
    """Check for new releases. Returns exit code."""
    state = load_state(state_path)
    last_checked_date = state["last_checked_date"]
    last_checked_release = state["last_checked_release"]

    print(f"Last checked release: {last_checked_release}")
    print(f"Last checked date:    {last_checked_date}")
    print()

    print(f"Fetching releases from {GITHUB_RELEASES_URL}...")
    try:
        releases = fetch_releases()
    except requests.RequestException as e:
        print(f"Error fetching releases: {e}")
        return 2

    print(f"Fetched {len(releases)} releases total.")

    new_releases = filter_new_releases(releases, last_checked_date)

    if not new_releases:
        print("Up to date. No new releases since last check.")
        return 1

    print(f"Found {len(new_releases)} new release(s):")
    for r in new_releases:
        name = r.get("name") or r.get("tag_name", "Unknown")
        print(f"  - {name} ({r.get('published_at', '')})")
    print()

    report = generate_report(new_releases)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved to {report_path}")

    return 0


def cmd_update(state_path: Path, tag: str | None) -> int:
    """Mark a release as checked. Returns exit code."""
    print(f"Fetching releases from {GITHUB_RELEASES_URL}...")
    try:
        releases = fetch_releases()
    except requests.RequestException as e:
        print(f"Error fetching releases: {e}")
        return 2

    if not releases:
        print("No releases found.")
        return 2

    if tag:
        target = next((r for r in releases if r.get("tag_name") == tag), None)
        if not target:
            print(f"Release with tag '{tag}' not found.")
            print("Available tags:")
            for r in releases[:10]:
                print(f"  - {r.get('tag_name')}")
            return 2
    else:
        # Find the most recent release by published_at
        target = max(
            [r for r in releases if r.get("published_at")],
            key=lambda r: parse_date(r["published_at"]),
        )

    tag_name = target.get("tag_name", "")
    published = target.get("published_at", "")
    name = target.get("name") or tag_name

    state = {
        "last_checked_release": tag_name,
        "last_checked_date": published,
    }
    save_state(state_path, state)

    print(f"Updated state to: {name}")
    print(f"  Tag:       {tag_name}")
    print(f"  Published: {published}")
    print(f"  Saved to:  {state_path}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check for new Etsy Open API releases on GitHub."
    )
    parser.add_argument(
        "--update",
        nargs="?",
        const="__latest__",
        metavar="TAG",
        help="Mark a release as checked (latest by default, or specify a tag)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    state_path = project_root / "specs" / "last-release-check.json"
    report_path = project_root / "specs" / "release-notes.md"

    if args.update is not None:
        tag = None if args.update == "__latest__" else args.update
        return cmd_update(state_path, tag)
    else:
        return cmd_check(state_path, report_path)


if __name__ == "__main__":
    sys.exit(main())
