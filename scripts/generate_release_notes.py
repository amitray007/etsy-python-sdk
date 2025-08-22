#!/usr/bin/env python3
"""
Generate detailed release notes for GitHub releases.
This script creates release notes with PR links, contributor mentions,
and categorized changes similar to GitHub's automatic release notes.
"""

import subprocess
import re
import sys
import argparse
from typing import List, Dict, Optional


def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Execute a command and return the result."""
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def get_previous_tag() -> Optional[str]:
    """Get the most recent tag before HEAD."""
    result = run_command(
        ["git", "describe", "--tags", "--abbrev=0", "HEAD^"], check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def get_commits_since_tag(tag: Optional[str]) -> List[Dict[str, str]]:
    """Get all commits since the given tag."""
    commits = []

    if tag:
        cmd = [
            "git",
            "log",
            f"{tag}..HEAD",
            "--pretty=format:%H|%s|%an|%ae",
            "--no-merges",
        ]
    else:
        cmd = ["git", "log", "--pretty=format:%H|%s|%an|%ae", "--no-merges"]

    result = run_command(cmd)

    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split("|")
            if len(parts) >= 4:
                commits.append(
                    {
                        "hash": parts[0],
                        "message": parts[1],
                        "author": parts[2],
                        "email": parts[3],
                    }
                )

    return commits


def extract_pr_number(message: str) -> Optional[str]:
    """Extract PR number from commit message."""
    # Look for #123 or (#123) patterns
    match = re.search(r"#(\d+)", message)
    if match:
        return match.group(1)

    # Look for "pull/123" pattern
    match = re.search(r"pull/(\d+)", message)
    if match:
        return match.group(1)

    return None


def get_github_username(email: str) -> str:
    """Extract GitHub username from email or git config."""
    # Common patterns
    if "@users.noreply.github.com" in email:
        # GitHub no-reply email format: username@users.noreply.github.com
        return email.split("@")[0].split("+")[-1]
    elif "[bot]" in email or "bot@" in email:
        # Bot accounts
        return email.split("@")[0].replace("[bot]", "-bot")
    else:
        # Try to get from git log
        result = run_command(
            ["git", "log", "--pretty=format:%ae|%an", "-1", "--author", email],
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            parts = result.stdout.strip().split("|")
            if len(parts) >= 2:
                # Use the name as username (simplified)
                return parts[1].replace(" ", "").lower()

        # Default: use email prefix
        return email.split("@")[0]


def format_commit_line(commit: Dict[str, str], repo: str) -> str:
    """Format a single commit line with PR link and author mention."""
    message = commit["message"]
    username = get_github_username(commit["email"])

    # Extract PR number
    pr_num = extract_pr_number(commit["message"])

    if pr_num:
        return f"* {message} by @{username} in {repo}/pull/{pr_num}"
    else:
        return f"* {message} by @{username}"


def generate_release_notes(
    version: str, repo: str = "https://github.com/amitray007/etsy-python-sdk"
) -> str:
    """Generate complete release notes for a version."""
    prev_tag = get_previous_tag()
    commits = get_commits_since_tag(prev_tag)

    notes = ""

    # Add What's Changed section
    notes += "## What's Changed\n"

    # Add all commits as a simple list
    if commits:
        for commit in commits:
            formatted_line = format_commit_line(commit, repo)
            notes += formatted_line + "\n"
    else:
        notes += "* No changes in this release\n"

    # Add full changelog link
    notes += "\n"
    if prev_tag:
        notes += f"**Full Changelog**: {repo}/compare/{prev_tag}...v{version}"
    else:
        notes += f"**Full Changelog**: {repo}/commits/v{version}"

    return notes


def main():
    parser = argparse.ArgumentParser(description="Generate release notes for a version")
    parser.add_argument("version", help="Version number for the release")
    parser.add_argument(
        "--repo",
        default="https://github.com/amitray007/etsy-python-sdk",
        help="Repository URL",
    )
    parser.add_argument("--output", help="Output file (default: print to stdout)")

    args = parser.parse_args()

    # Generate release notes
    notes = generate_release_notes(args.version, args.repo)

    # Output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(notes)
        print(f"Release notes written to {args.output}")
    else:
        # For Windows compatibility, encode to UTF-8 when printing
        import sys
        import codecs

        if sys.platform == "win32":
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        print(notes)

    return 0


if __name__ == "__main__":
    sys.exit(main())
