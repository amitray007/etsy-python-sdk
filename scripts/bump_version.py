#!/usr/bin/env python3
"""
Automatic version bumping script for etsy-python package.
Supports patch, minor, and major version bumps.
"""

import re
import sys
import argparse
from pathlib import Path


def read_version(version_file):
    """Read current version from _version.py file."""
    with open(version_file, 'r') as f:
        content = f.read()
    
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError(f"Could not find version in {version_file}")
    
    return match.group(1)


def parse_version(version_str):
    """Parse version string into major, minor, patch components."""
    parts = version_str.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version_str}")
    
    try:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2])
    except ValueError:
        raise ValueError(f"Version parts must be integers: {version_str}")
    
    return major, minor, patch


def bump_version(version_str, bump_type='patch'):
    """Bump version based on type (patch, minor, major)."""
    major, minor, patch = parse_version(version_str)
    
    if bump_type == 'patch':
        patch += 1
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"


def write_version(version_file, new_version):
    """Write new version to _version.py file."""
    content = f'''"""Version information for etsy-python package."""

__version__ = "{new_version}"'''
    
    with open(version_file, 'w') as f:
        f.write(content)


def get_latest_commit_message():
    """Get the latest commit message to determine bump type."""
    import subprocess
    
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%B'],  # Get full commit message
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def determine_bump_type(commit_message):
    """
    Determine version bump type from commit message.
    
    Conventions:
    - Contains 'BREAKING CHANGE' or starts with 'breaking:' -> major
    - Starts with 'feat:' or contains 'feature' -> minor
    - Default -> patch
    """
    message_lower = commit_message.lower()
    
    # Check for breaking changes
    if 'breaking change' in message_lower or message_lower.startswith('breaking:'):
        return 'major'
    
    # Check for new features
    if message_lower.startswith('feat:') or 'feature' in message_lower:
        return 'minor'
    
    # Default to patch
    return 'patch'


def main():
    parser = argparse.ArgumentParser(description='Bump version for etsy-python package')
    parser.add_argument(
        '--type',
        choices=['patch', 'minor', 'major', 'auto'],
        default='auto',
        help='Type of version bump (default: auto - determined from commit message)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    version_file = project_root / 'etsy_python' / '_version.py'
    
    if not version_file.exists():
        print(f"Error: Version file not found at {version_file}")
        sys.exit(1)
    
    # Read current version
    current_version = read_version(version_file)
    print(f"Current version: {current_version}")
    
    # Determine bump type
    if args.type == 'auto':
        commit_message = get_latest_commit_message()
        if commit_message:
            bump_type = determine_bump_type(commit_message)
            print(f"Latest commit: {commit_message}")
            print(f"Auto-detected bump type: {bump_type}")
        else:
            bump_type = 'patch'
            print("Could not get commit message, defaulting to patch bump")
    else:
        bump_type = args.type
    
    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print(f"New version: {new_version}")
    
    if not args.dry_run:
        # Write new version
        write_version(version_file, new_version)
        print(f"Version updated to {new_version}")
        
        # Output new version for GitHub Actions
        print(f"::set-output name=version::{new_version}")
    else:
        print("Dry run - no changes made")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())