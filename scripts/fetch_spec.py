#!/usr/bin/env python3
"""
Fetch the latest Etsy OpenAPI spec and compare against baseline.

Usage:
    python scripts/fetch_spec.py

Exit codes:
    0 - Spec fetched and differs from baseline (changes detected)
    1 - Spec fetched but identical to baseline (no changes)
    2 - Error (network, file I/O, etc.)
"""

import json
import sys
from pathlib import Path

import requests

ETSY_OAS_URL = "https://www.etsy.com/openapi/generated/oas/3.0.0.json"


def fetch_spec() -> dict:
    """Download the current Etsy OAS spec."""
    response = requests.get(ETSY_OAS_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    """Save dict as formatted JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> int:
    project_root = Path(__file__).parent.parent
    specs_dir = project_root / "specs"
    baseline_path = specs_dir / "baseline.json"
    latest_path = specs_dir / "latest.json"

    print(f"Fetching Etsy OAS spec from {ETSY_OAS_URL}...")
    try:
        spec = fetch_spec()
    except requests.RequestException as e:
        print(f"Error fetching spec: {e}")
        return 2

    save_json(latest_path, spec)
    print(f"Saved to {latest_path}")

    if not baseline_path.exists():
        print("No baseline.json found. This is likely the first run.")
        print(f"Copy {latest_path} to {baseline_path} to set the baseline:")
        print(f"  cp specs/latest.json specs/baseline.json")
        return 0

    try:
        baseline = load_json(baseline_path)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse {baseline_path}: {e}")
        return 2

    if baseline == spec:
        print("No changes detected. Spec matches baseline.")
        return 1
    else:
        print("Changes detected! Spec differs from baseline.")
        print("Run `python scripts/diff_spec.py` to see what changed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
