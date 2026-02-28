#!/usr/bin/env python3
"""
Read the audit report and produce a condensed markdown summary for PR comments.

Usage:
    python scripts/format_pr_comment.py > comment.md
    python scripts/format_pr_comment.py --report specs/audit-report.md
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List


def parse_coverage_summary(lines: List[str]) -> dict:
    """Extract numeric values from the Coverage Summary section."""
    summary = {}
    in_section = False
    for line in lines:
        if line.startswith("## Coverage Summary"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("- "):
            match = re.match(r"- (.+?):\s*(.+)", line)
            if match:
                summary[match.group(1).strip()] = match.group(2).strip()
    return summary


def extract_section(lines: List[str], header: str) -> List[str]:
    """Extract lines belonging to a section (from header to next ## header)."""
    section = []
    in_section = False
    for line in lines:
        if line.strip() == header:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            section.append(line)
    return section


def count_items(section_lines: List[str]) -> int:
    """Count bullet items in a section."""
    return sum(1 for line in section_lines if line.startswith("- **"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Path to audit report (default: specs/audit-report.md)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    report_path = args.report or project_root / "specs" / "audit-report.md"

    if not report_path.exists():
        print(f"Error: Report not found at {report_path}", file=sys.stderr)
        return 1

    content = report_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    summary = parse_coverage_summary(lines)
    coverage_pct = summary.get("Coverage", "N/A")
    total_ops = summary.get("Total OAS operations", "?")
    mapped = summary.get("Mapped to SDK methods", "?")
    missing_count = summary.get("Missing from SDK", "?")
    extra_count = summary.get("Extra SDK methods (no OAS match)", "?")

    missing_lines = extract_section(lines, "## Missing Endpoints")
    query_drift_lines = extract_section(lines, "## Query/Path Parameter Drift")
    body_drift_lines = extract_section(lines, "## Request Body Drift")
    enum_lines = extract_section(lines, "## Enum Staleness")

    drift_count = (
        sum(1 for l in query_drift_lines if l.startswith("### "))
        + sum(1 for l in body_drift_lines if l.startswith("### "))
    )
    enum_count = sum(1 for l in enum_lines if l.startswith("### "))

    # Build condensed comment
    out = []
    out.append("<!-- sdk-coverage-report -->")
    out.append("## SDK Coverage Report")
    out.append("")

    # Coverage bar
    try:
        pct = float(coverage_pct.rstrip("%"))
        filled = int(pct / 5)
        bar = "#" * filled + "-" * (20 - filled)
        out.append(f"**Coverage: {coverage_pct}** `[{bar}]` ({mapped}/{total_ops} operations)")
    except ValueError:
        out.append(f"**Coverage: {coverage_pct}** ({mapped}/{total_ops} operations)")

    out.append("")

    # Summary table
    out.append("| Metric | Count |")
    out.append("|--------|-------|")
    out.append(f"| Mapped operations | {mapped} |")
    out.append(f"| Missing endpoints | {missing_count} |")
    out.append(f"| Extra SDK methods | {extra_count} |")
    out.append(f"| Parameter drift | {drift_count} |")
    out.append(f"| Stale enums | {enum_count} |")
    out.append("")

    # Missing endpoints (compact)
    missing_items = [l for l in missing_lines if l.startswith("- **")]
    if missing_items:
        out.append("<details>")
        out.append(f"<summary><strong>Missing Endpoints ({len(missing_items)})</strong></summary>")
        out.append("")
        for item in missing_items:
            out.append(item)
        out.append("")
        out.append("</details>")
        out.append("")

    # Parameter drift (compact — just list affected operations)
    drift_ops = (
        [l.lstrip("# ").split(" (")[0] for l in query_drift_lines if l.startswith("### ")]
        + [l.lstrip("# ").split(" (")[0] for l in body_drift_lines if l.startswith("### ")]
    )
    if drift_ops:
        out.append("<details>")
        out.append(f"<summary><strong>Parameter Drift ({len(drift_ops)} operations)</strong></summary>")
        out.append("")
        for op in drift_ops:
            out.append(f"- `{op}`")
        out.append("")
        out.append("</details>")
        out.append("")

    # Enum staleness (compact)
    enum_items = [l.lstrip("# ").split("\n")[0] for l in enum_lines if l.startswith("### ")]
    if enum_items:
        out.append("<details>")
        out.append(f"<summary><strong>Stale Enums ({len(enum_items)})</strong></summary>")
        out.append("")
        for item in enum_items:
            out.append(f"- `{item}`")
        out.append("")
        out.append("</details>")
        out.append("")

    out.append("---")
    out.append("*Auto-generated by SDK Coverage Check*")

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
