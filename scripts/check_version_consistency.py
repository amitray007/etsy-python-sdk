#!/usr/bin/env python3
"""
Check that version is consistent across all files.
Used as a pre-commit hook and in CI.
"""

import re
import sys
from pathlib import Path


def get_version_from_file(file_path, pattern):
    """Extract version from a file using regex pattern."""
    if not file_path.exists():
        return None
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return None


def main():
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Files to check and their version patterns
    version_files = {
        'etsy_python/_version.py': r'__version__\s*=\s*["\']([^"\']+)["\']',
        '.bumpversion.cfg': r'current_version\s*=\s*([^\n]+)',
    }
    
    versions = {}
    errors = []
    
    # Extract versions from all files
    for file_path, pattern in version_files.items():
        full_path = project_root / file_path
        version = get_version_from_file(full_path, pattern)
        if version:
            versions[file_path] = version.strip()
        else:
            errors.append(f"Could not find version in {file_path}")
    
    # Check if all versions match
    if versions:
        unique_versions = set(versions.values())
        if len(unique_versions) > 1:
            errors.append("Version mismatch detected:")
            for file_path, version in versions.items():
                errors.append(f"  {file_path}: {version}")
        else:
            print(f"[OK] All versions consistent: {list(unique_versions)[0]}")
    
    # Report errors
    if errors:
        print("[ERROR] Version consistency check failed:")
        for error in errors:
            print(f"  {error}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())