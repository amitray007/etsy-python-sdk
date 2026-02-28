#!/usr/bin/env python3
"""
Diff two Etsy OAS specs and produce a structured markdown report.

Usage:
    python scripts/diff_spec.py
    python scripts/diff_spec.py --baseline specs/baseline.json --latest specs/latest.json

Output: Markdown report to stdout and specs/diff-report.md
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_operations(spec: dict) -> Dict[str, dict]:
    """Extract all operations keyed by operationId."""
    operations = {}
    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method in ("get", "post", "put", "delete", "patch"):
                op_id = details.get("operationId", f"{method}:{path}")
                operations[op_id] = {
                    "path": path,
                    "method": method.upper(),
                    "parameters": details.get("parameters", []),
                    "requestBody": details.get("requestBody"),
                    "responses": details.get("responses", {}),
                    "deprecated": details.get("deprecated", False),
                    "tags": details.get("tags", []),
                    "summary": details.get("summary", ""),
                }
    return operations


def get_schemas(spec: dict) -> Dict[str, dict]:
    """Extract all schemas from components."""
    return spec.get("components", {}).get("schemas", {})


def diff_parameters(
    old_params: List[dict], new_params: List[dict]
) -> Dict[str, List[str]]:
    """Diff parameter lists, returning added/removed/changed."""
    old_by_name = {p["name"]: p for p in old_params}
    new_by_name = {p["name"]: p for p in new_params}
    old_names = set(old_by_name.keys())
    new_names = set(new_by_name.keys())

    result = {
        "added": sorted(new_names - old_names),
        "removed": sorted(old_names - new_names),
        "changed": [],
    }

    for name in old_names & new_names:
        old_p = old_by_name[name]
        new_p = new_by_name[name]
        changes = []
        if old_p.get("required") != new_p.get("required"):
            changes.append(
                f"required: {old_p.get('required', False)} -> {new_p.get('required', False)}"
            )
        old_schema = old_p.get("schema", {})
        new_schema = new_p.get("schema", {})
        if old_schema.get("type") != new_schema.get("type"):
            changes.append(
                f"type: {old_schema.get('type')} -> {new_schema.get('type')}"
            )
        if old_schema.get("enum") != new_schema.get("enum"):
            changes.append("enum values changed")
        if changes:
            result["changed"].append(f"{name} ({', '.join(changes)})")

    return result


def diff_schema_properties(
    old_schema: dict, new_schema: dict
) -> Dict[str, List[str]]:
    """Diff schema properties."""
    old_props = set(old_schema.get("properties", {}).keys())
    new_props = set(new_schema.get("properties", {}).keys())

    result = {
        "added": sorted(new_props - old_props),
        "removed": sorted(old_props - new_props),
        "changed": [],
    }

    for prop in old_props & new_props:
        old_p = old_schema["properties"][prop]
        new_p = new_schema["properties"][prop]
        changes = []
        if old_p.get("type") != new_p.get("type"):
            changes.append(
                f"type: {old_p.get('type')} -> {new_p.get('type')}"
            )
        if old_p.get("enum") != new_p.get("enum"):
            old_enum = set(old_p.get("enum", []))
            new_enum = set(new_p.get("enum", []))
            added = new_enum - old_enum
            removed = old_enum - new_enum
            if added:
                changes.append(f"enum added: {sorted(added)}")
            if removed:
                changes.append(f"enum removed: {sorted(removed)}")
        if changes:
            result["changed"].append(f"{prop} ({', '.join(changes)})")

    return result


def extract_request_body_schema(op: dict, spec: dict) -> dict:
    """Extract the schema from a requestBody, resolving $ref if needed."""
    rb = op.get("requestBody")
    if not rb:
        return {}
    content = rb.get("content", {})
    json_content = content.get("application/json", content.get("application/x-www-form-urlencoded", {}))
    schema = json_content.get("schema", {})
    return resolve_ref(schema, spec)


def resolve_ref(obj: Any, spec: dict) -> Any:
    """Resolve a $ref pointer in the spec."""
    if isinstance(obj, dict) and "$ref" in obj:
        ref_path = obj["$ref"].lstrip("#/").split("/")
        resolved = spec
        for part in ref_path:
            resolved = resolved.get(part, {})
        return resolved
    return obj


def generate_report(baseline: dict, latest: dict) -> str:
    """Generate the full diff report as markdown."""
    lines = ["# Etsy OAS Spec Diff Report\n"]

    old_ops = get_operations(baseline)
    new_ops = get_operations(latest)
    old_op_ids = set(old_ops.keys())
    new_op_ids = set(new_ops.keys())

    # New Endpoints
    added_ops = sorted(new_op_ids - old_op_ids)
    lines.append("## New Endpoints\n")
    if added_ops:
        for op_id in added_ops:
            op = new_ops[op_id]
            lines.append(
                f"- **{op_id}** `{op['method']} {op['path']}`"
            )
            if op["summary"]:
                lines.append(f"  {op['summary']}")
    else:
        lines.append("No new endpoints.\n")

    # Removed Endpoints
    removed_ops = sorted(old_op_ids - new_op_ids)
    lines.append("\n## Removed Endpoints\n")
    if removed_ops:
        for op_id in removed_ops:
            op = old_ops[op_id]
            lines.append(
                f"- **{op_id}** `{op['method']} {op['path']}`"
            )
    else:
        lines.append("No removed endpoints.\n")

    # Changed Endpoints
    common_ops = sorted(old_op_ids & new_op_ids)
    lines.append("\n## Changed Endpoints\n")
    any_changes = False
    for op_id in common_ops:
        old_op = old_ops[op_id]
        new_op = new_ops[op_id]
        changes = []

        # Parameter changes
        param_diff = diff_parameters(
            old_op["parameters"], new_op["parameters"]
        )
        if any(param_diff.values()):
            if param_diff["added"]:
                changes.append(
                    f"  - Parameters added: {', '.join(param_diff['added'])}"
                )
            if param_diff["removed"]:
                changes.append(
                    f"  - Parameters removed: {', '.join(param_diff['removed'])}"
                )
            if param_diff["changed"]:
                changes.append(
                    f"  - Parameters changed: {', '.join(param_diff['changed'])}"
                )

        # Request body changes
        old_rb = extract_request_body_schema(old_op, baseline)
        new_rb = extract_request_body_schema(new_op, latest)
        if old_rb != new_rb:
            rb_diff = diff_schema_properties(old_rb, new_rb)
            if any(rb_diff.values()):
                if rb_diff["added"]:
                    changes.append(
                        f"  - Request body fields added: {', '.join(rb_diff['added'])}"
                    )
                if rb_diff["removed"]:
                    changes.append(
                        f"  - Request body fields removed: {', '.join(rb_diff['removed'])}"
                    )
                if rb_diff["changed"]:
                    changes.append(
                        f"  - Request body fields changed: {', '.join(rb_diff['changed'])}"
                    )

        # Deprecation changes
        if not old_op["deprecated"] and new_op["deprecated"]:
            changes.append("  - **Newly deprecated**")

        if changes:
            any_changes = True
            lines.append(
                f"### {op_id} (`{new_op['method']} {new_op['path']}`)\n"
            )
            lines.extend(changes)
            lines.append("")

    if not any_changes:
        lines.append("No changed endpoints.\n")

    # Schema Changes
    old_schemas = get_schemas(baseline)
    new_schemas = get_schemas(latest)
    old_schema_names = set(old_schemas.keys())
    new_schema_names = set(new_schemas.keys())

    lines.append("\n## Schema Changes\n")
    schema_changes = False

    added_schemas = sorted(new_schema_names - old_schema_names)
    if added_schemas:
        schema_changes = True
        lines.append("### New Schemas\n")
        for name in added_schemas:
            props = list(new_schemas[name].get("properties", {}).keys())
            lines.append(f"- **{name}**: {', '.join(props[:10])}")
            if len(props) > 10:
                lines.append(f"  ...and {len(props) - 10} more")
        lines.append("")

    removed_schemas = sorted(old_schema_names - new_schema_names)
    if removed_schemas:
        schema_changes = True
        lines.append("### Removed Schemas\n")
        for name in removed_schemas:
            lines.append(f"- **{name}**")
        lines.append("")

    for name in sorted(old_schema_names & new_schema_names):
        prop_diff = diff_schema_properties(old_schemas[name], new_schemas[name])
        if any(prop_diff.values()):
            schema_changes = True
            lines.append(f"### {name}\n")
            if prop_diff["added"]:
                lines.append(
                    f"- Properties added: {', '.join(prop_diff['added'])}"
                )
            if prop_diff["removed"]:
                lines.append(
                    f"- Properties removed: {', '.join(prop_diff['removed'])}"
                )
            if prop_diff["changed"]:
                lines.append(
                    f"- Properties changed: {', '.join(prop_diff['changed'])}"
                )
            lines.append("")

    if not schema_changes:
        lines.append("No schema changes.\n")

    # Deprecations summary
    lines.append("\n## Deprecations\n")
    deprecations = []
    for op_id in new_op_ids:
        if new_ops[op_id]["deprecated"] and (
            op_id not in old_ops or not old_ops[op_id].get("deprecated", False)
        ):
            deprecations.append(op_id)
    if deprecations:
        for op_id in sorted(deprecations):
            op = new_ops[op_id]
            lines.append(f"- **{op_id}** `{op['method']} {op['path']}`")
    else:
        lines.append("No new deprecations.\n")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff two Etsy OAS specs")
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="Path to baseline spec (default: specs/baseline.json)",
    )
    parser.add_argument(
        "--latest",
        type=Path,
        default=None,
        help="Path to latest spec (default: specs/latest.json)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    baseline_path = args.baseline or project_root / "specs" / "baseline.json"
    latest_path = args.latest or project_root / "specs" / "latest.json"

    if not baseline_path.exists():
        print(f"Error: Baseline spec not found at {baseline_path}")
        print("Run `python scripts/fetch_spec.py` first, then copy latest to baseline.")
        return 1

    if not latest_path.exists():
        print(f"Error: Latest spec not found at {latest_path}")
        print("Run `python scripts/fetch_spec.py` first.")
        return 1

    try:
        baseline = load_json(baseline_path)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse {baseline_path}: {e}")
        return 1

    try:
        latest = load_json(latest_path)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse {latest_path}: {e}")
        return 1

    report = generate_report(baseline, latest)
    print(report)

    report_path = project_root / "specs" / "diff-report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
