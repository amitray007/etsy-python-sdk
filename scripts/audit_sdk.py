#!/usr/bin/env python3
"""
Audit SDK coverage against the Etsy OAS spec.

Auto-infers mappings from OAS operationIds to SDK resource methods by:
1. Converting operationId (camelCase) to snake_case
2. Scanning resource files for matching method names
3. Comparing parameters and enums

Usage:
    python scripts/audit_sdk.py
    python scripts/audit_sdk.py --spec specs/baseline.json

Output: Markdown report to stdout and specs/audit-report.md
"""

import ast
import json
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def camel_to_snake(name: str) -> str:
    """Convert camelCase/PascalCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def get_operations(spec: dict) -> Dict[str, dict]:
    """Extract all operations from the OAS spec."""
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
                    "tags": details.get("tags", []),
                    "deprecated": details.get("deprecated", False),
                }
    return operations


def resolve_ref(obj, spec: dict):
    """Resolve a $ref pointer."""
    if isinstance(obj, dict) and "$ref" in obj:
        ref_path = obj["$ref"].lstrip("#/").split("/")
        resolved = spec
        for part in ref_path:
            resolved = resolved.get(part, {})
        return resolved
    return obj


def get_request_body_fields(op: dict, spec: dict) -> Set[str]:
    """Get field names from a request body schema."""
    rb = op.get("requestBody")
    if not rb:
        return set()
    content = rb.get("content", {})
    json_content = content.get(
        "application/json",
        content.get("application/x-www-form-urlencoded", {}),
    )
    schema = json_content.get("schema", {})
    schema = resolve_ref(schema, spec)
    return set(schema.get("properties", {}).keys())


def get_spec_enums(spec: dict) -> Dict[str, List[str]]:
    """Extract all enum definitions from schemas."""
    enums = {}
    for name, schema in spec.get("components", {}).get("schemas", {}).items():
        for prop_name, prop in schema.get("properties", {}).items():
            prop = resolve_ref(prop, spec)
            if "enum" in prop:
                key = f"{name}.{prop_name}"
                enums[key] = prop["enum"]
    return enums


def scan_resource_methods(resources_dir: Path) -> Dict[str, Dict[str, dict]]:
    """Scan all resource .py files and extract method names and their parameters."""
    resources = {}
    for py_file in sorted(resources_dir.glob("*.py")):
        if py_file.name.startswith("__") or py_file.name in (
            "Session.py",
            "Response.py",
        ):
            continue

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        file_methods = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name.startswith("_"):
                            continue
                        params = []
                        for arg in item.args.args:
                            if arg.arg != "self":
                                params.append(arg.arg)
                        file_methods[item.name] = {
                            "params": params,
                            "class": node.name,
                            "file": py_file.name,
                            "line": item.lineno,
                        }

        if file_methods:
            resources[py_file.stem] = file_methods

    return resources


def scan_enum_values(enums_dir: Path) -> Dict[str, List[str]]:
    """Scan enum .py files and extract enum class names and their values."""
    sdk_enums = {}
    for py_file in sorted(enums_dir.glob("*.py")):
        if py_file.name.startswith("__"):
            continue

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                values = []
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if isinstance(item.value, ast.Constant):
                                    values.append(item.value.value)
                if values:
                    sdk_enums[node.name] = values

    return sdk_enums


def scan_model_fields(models_dir: Path) -> Dict[str, Set[str]]:
    """Scan model .py files and extract class init parameter names."""
    models = {}
    for py_file in sorted(models_dir.glob("*.py")):
        if py_file.name.startswith("__"):
            continue

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if (
                        isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and item.name == "__init__"
                    ):
                        params = set()
                        for arg in item.args.args:
                            if arg.arg != "self":
                                params.add(arg.arg)
                        if params:
                            models[node.name] = params

    return models


def build_method_index(
    resources: Dict[str, Dict[str, dict]]
) -> Dict[str, dict]:
    """Build a flat index of all SDK methods by snake_case name."""
    index = {}
    for resource_name, methods in resources.items():
        for method_name, info in methods.items():
            index[method_name] = {**info, "resource": resource_name}
    return index


def generate_report(
    spec: dict,
    resources_dir: Path,
    enums_dir: Path,
    models_dir: Path,
) -> str:
    """Generate the audit report."""
    lines = ["# Etsy SDK Audit Report\n"]

    operations = get_operations(spec)
    resources = scan_resource_methods(resources_dir)
    method_index = build_method_index(resources)
    sdk_enums = scan_enum_values(enums_dir)
    sdk_models = scan_model_fields(models_dir)

    # Map operations to SDK methods
    mapped = {}
    unmapped = []
    for op_id, op_info in sorted(operations.items()):
        snake_name = camel_to_snake(op_id)
        if snake_name in method_index:
            mapped[op_id] = {
                "spec": op_info,
                "sdk": method_index[snake_name],
                "sdk_method": snake_name,
            }
        else:
            unmapped.append((op_id, op_info))

    # Find SDK methods with no OAS match
    all_spec_snake = {camel_to_snake(op_id) for op_id in operations}
    extra_methods = []
    for method_name, info in method_index.items():
        if method_name not in all_spec_snake:
            extra_methods.append((method_name, info))

    # Coverage summary
    total_ops = len(operations)
    mapped_count = len(mapped)
    lines.append("## Coverage Summary\n")
    lines.append(f"- Total OAS operations: {total_ops}")
    lines.append(f"- Mapped to SDK methods: {mapped_count}")
    lines.append(f"- Missing from SDK: {len(unmapped)}")
    lines.append(f"- Extra SDK methods (no OAS match): {len(extra_methods)}")
    pct = (mapped_count / total_ops * 100) if total_ops > 0 else 0
    lines.append(f"- Coverage: {pct:.1f}%\n")

    # Missing endpoints
    lines.append("## Missing Endpoints\n")
    lines.append("OAS operations with no matching SDK method.\n")
    if unmapped:
        for op_id, op_info in unmapped:
            snake = camel_to_snake(op_id)
            dep = " (DEPRECATED)" if op_info["deprecated"] else ""
            lines.append(
                f"- **{op_id}** -> `{snake}`{dep}"
            )
            lines.append(
                f"  `{op_info['method']} {op_info['path']}`"
            )
            lines.append(f"  Tags: {', '.join(op_info['tags'])}")
    else:
        lines.append("All OAS operations are covered!\n")

    # Extra SDK methods
    lines.append("\n## Extra SDK Methods\n")
    lines.append("SDK methods with no matching OAS operation (possibly removed or renamed).\n")
    if extra_methods:
        for method_name, info in sorted(extra_methods):
            lines.append(
                f"- **{method_name}** in `{info['file']}:{info['line']}` ({info['class']})"
            )
    else:
        lines.append("No extra methods found.\n")

    # Parameter drift
    lines.append("\n## Parameter Drift\n")
    lines.append("Mismatches between OAS params and SDK method signatures.\n")
    any_drift = False
    for op_id, mapping in sorted(mapped.items()):
        op = mapping["spec"]
        sdk = mapping["sdk"]

        # Collect OAS parameter names (path + query)
        spec_params = {p["name"] for p in op["parameters"]}

        # Collect OAS request body field names
        spec_body_fields = get_request_body_fields(op, spec)

        # SDK method params (excluding path params that are method args)
        sdk_params = set(sdk["params"])

        # Combine spec params for comparison
        all_spec_params = spec_params | spec_body_fields

        # Find mismatches (ignore common SDK-only params like 'self', model objects)
        spec_only = all_spec_params - sdk_params
        sdk_only = sdk_params - all_spec_params

        # Filter out params that are likely model class references
        sdk_only = {
            p
            for p in sdk_only
            if not any(
                p.endswith(suffix)
                for suffix in ("_request", "_listing", "_policy", "_profile")
            )
            and p
            not in (
                "shop_id",
                "listing_id",
                "receipt_id",
                "listing",
                "request",
                "payload",
            )
        }

        if spec_only or sdk_only:
            any_drift = True
            lines.append(
                f"### {op_id} (`{mapping['sdk_method']}` in {sdk['file']}:{sdk['line']})\n"
            )
            if spec_only:
                lines.append(f"- In spec but not SDK: {', '.join(sorted(spec_only))}")
            if sdk_only:
                lines.append(f"- In SDK but not spec: {', '.join(sorted(sdk_only))}")
            lines.append("")

    if not any_drift:
        lines.append("No parameter drift detected.\n")

    # Enum staleness
    lines.append("\n## Enum Staleness\n")
    lines.append("OAS enum values not reflected in SDK enum classes.\n")
    spec_enums = get_spec_enums(spec)
    any_enum_issues = False

    # Build a lookup of SDK enum values for fuzzy matching
    sdk_enum_values_map = {}
    for enum_name, values in sdk_enums.items():
        for v in values:
            sdk_enum_values_map.setdefault(str(v).lower(), []).append(enum_name)

    for spec_key, spec_values in sorted(spec_enums.items()):
        # Try to find matching SDK enum by checking if spec values overlap
        best_match = None
        best_overlap = 0
        for sdk_name, sdk_values in sdk_enums.items():
            sdk_value_set = {str(v).lower() for v in sdk_values}
            spec_value_set = {str(v).lower() for v in spec_values}
            overlap = len(sdk_value_set & spec_value_set)
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = sdk_name

        if best_match and best_overlap > 0:
            sdk_value_set = {str(v).lower() for v in sdk_enums[best_match]}
            spec_value_set = {str(v).lower() for v in spec_values}
            missing = spec_value_set - sdk_value_set
            extra = sdk_value_set - spec_value_set
            if missing or extra:
                any_enum_issues = True
                lines.append(f"### {spec_key} -> SDK `{best_match}`\n")
                if missing:
                    lines.append(f"- Missing from SDK: {', '.join(sorted(missing))}")
                if extra:
                    lines.append(f"- Extra in SDK: {', '.join(sorted(extra))}")
                lines.append("")

    if not any_enum_issues:
        lines.append("All enum values are in sync.\n")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SDK coverage against OAS spec")
    parser.add_argument(
        "--spec",
        type=Path,
        default=None,
        help="Path to OAS spec (default: specs/baseline.json)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    spec_path = args.spec or project_root / "specs" / "baseline.json"
    resources_dir = project_root / "etsy_python" / "v3" / "resources"
    enums_dir = project_root / "etsy_python" / "v3" / "enums"
    models_dir = project_root / "etsy_python" / "v3" / "models"

    if not spec_path.exists():
        print(f"Error: Spec not found at {spec_path}")
        print("Run `python scripts/fetch_spec.py` first.")
        return 1

    spec = load_json(spec_path)
    report = generate_report(spec, resources_dir, enums_dir, models_dir)
    print(report)

    report_path = project_root / "specs" / "audit-report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
