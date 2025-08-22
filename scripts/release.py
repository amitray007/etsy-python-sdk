#!/usr/bin/env python3
"""
Manual release script for local development and testing.
This script helps developers create releases locally before pushing to GitHub.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
    return result


def check_git_status():
    """Check if git working directory is clean."""
    result = run_command(['git', 'status', '--porcelain'])
    if result.stdout.strip():
        print("Error: Working directory is not clean. Please commit or stash changes.")
        print(result.stdout)
        return False
    return True


def check_branch():
    """Check if on master branch."""
    result = run_command(['git', 'branch', '--show-current'])
    branch = result.stdout.strip()
    if branch != 'master':
        print(f"Warning: Not on master branch (current: {branch})")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    return True


def bump_version(bump_type):
    """Bump version using the bump_version.py script."""
    script_path = Path(__file__).parent / 'bump_version.py'
    result = run_command(['python', str(script_path), '--type', bump_type])
    
    # Get the new version
    from etsy_python._version import __version__
    return __version__


def build_package():
    """Build the package distribution."""
    print("\n📦 Building package...")
    run_command(['python', '-m', 'pip', 'install', '--upgrade', 'build'])
    run_command(['python', '-m', 'build'])
    print("✓ Package built successfully")


def run_tests():
    """Run any available tests."""
    print("\n🧪 Running tests...")
    # Since there's no test framework set up, we'll just do basic imports
    try:
        import etsy_python
        from etsy_python._version import __version__
        print(f"✓ Package imports successfully (version {__version__})")
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    return True


def create_git_tag(version, message=None):
    """Create a git tag for the release."""
    tag_name = f"v{version}"
    if message is None:
        message = f"Release version {version}"
    
    print(f"\n🏷️  Creating tag {tag_name}...")
    run_command(['git', 'tag', '-a', tag_name, '-m', message])
    print(f"✓ Tag {tag_name} created")
    return tag_name


def commit_version_bump(version):
    """Commit the version bump changes."""
    print(f"\n💾 Committing version bump to {version}...")
    run_command(['git', 'add', 'etsy_python/_version.py', '.bumpversion.cfg'])
    run_command(['git', 'commit', '-m', f'chore: bump version to {version}'])
    print("✓ Changes committed")


def push_to_remote(push_tags=True):
    """Push commits and tags to remote."""
    print("\n🚀 Pushing to remote...")
    run_command(['git', 'push', 'origin', 'master'])
    if push_tags:
        run_command(['git', 'push', 'origin', '--tags'])
    print("✓ Pushed to remote")


def main():
    parser = argparse.ArgumentParser(
        description='Create a new release for etsy-python package'
    )
    parser.add_argument(
        'bump_type',
        choices=['patch', 'minor', 'major'],
        help='Type of version bump'
    )
    parser.add_argument(
        '--no-push',
        action='store_true',
        help="Don't push to remote (local release only)"
    )
    parser.add_argument(
        '--no-tag',
        action='store_true',
        help="Don't create git tag"
    )
    parser.add_argument(
        '--no-build',
        action='store_true',
        help="Don't build the package"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help="Force release even with uncommitted changes"
    )
    
    args = parser.parse_args()
    
    print("🎯 Etsy Python SDK Release Tool")
    print("=" * 40)
    
    # Pre-release checks
    if not args.force:
        if not check_git_status():
            return 1
        if not check_branch():
            return 1
    
    # Bump version
    print(f"\n📈 Bumping version ({args.bump_type})...")
    new_version = bump_version(args.bump_type)
    print(f"✓ Version bumped to {new_version}")
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Tests failed, but continuing...")
    
    # Commit changes
    commit_version_bump(new_version)
    
    # Create tag
    if not args.no_tag:
        create_git_tag(new_version)
    
    # Build package
    if not args.no_build:
        build_package()
    
    # Push to remote
    if not args.no_push:
        push_to_remote(push_tags=not args.no_tag)
    else:
        print("\n⚠️  Skipping push to remote (--no-push flag set)")
        print("To push manually, run:")
        print("  git push origin master --tags")
    
    print(f"\n✅ Release {new_version} completed successfully!")
    print("\nNext steps:")
    if args.no_push:
        print("  1. Push changes: git push origin master --tags")
        print("  2. GitHub Actions will automatically publish to PyPI")
    else:
        print("  1. GitHub Actions will automatically publish to PyPI")
        print("  2. Check the Actions tab on GitHub for progress")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())