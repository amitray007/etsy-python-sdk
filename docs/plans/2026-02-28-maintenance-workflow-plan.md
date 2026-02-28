# Maintenance Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build on-demand tooling (scripts + Claude Code skills) to detect Etsy API changes, audit SDK coverage, and run live integration tests.

**Architecture:** Three Python scripts (`fetch_spec.py`, `diff_spec.py`, `audit_sdk.py`) provide the core logic. A pytest test suite covers live API integration. Three Claude Code skills (`/maintain:check`, `/maintain:audit`, `/maintain:test`) orchestrate these tools conversationally. A `specs/` directory stores baseline and latest OAS specs.

**Tech Stack:** Python 3.8+, requests (already a dependency), pytest, python-dotenv

**Design doc:** `docs/plans/2026-02-28-maintenance-workflow-design.md`

---

### Task 1: Project scaffolding and dev dependencies

**Files:**
- Create: `specs/.gitkeep`
- Create: `requirements-dev.txt`
- Modify: `.gitignore`

**Step 1: Create `requirements-dev.txt`**

```python
# requirements-dev.txt
pytest>=7.0
python-dotenv>=1.0
```

**Step 2: Add specs ignores to `.gitignore`**

Append to `.gitignore`:
```
# Maintenance workflow - ephemeral files
specs/latest.json
specs/diff-report.md
specs/audit-report.md
```

**Step 3: Create the specs directory with a `.gitkeep`**

```bash
mkdir -p specs
touch specs/.gitkeep
```

**Step 4: Install dev dependencies**

```bash
pip install -r requirements-dev.txt
```

**Step 5: Commit**

```bash
git add requirements-dev.txt .gitignore specs/.gitkeep
git commit -m "chore: add dev dependencies and specs directory for maintenance workflow"
```

---

### Task 2: `scripts/fetch_spec.py` — Download latest OAS spec

**Files:**
- Create: `scripts/fetch_spec.py`

**Step 1: Write the script**

```python
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

    baseline = load_json(baseline_path)
    if baseline == spec:
        print("No changes detected. Spec matches baseline.")
        return 1
    else:
        print("Changes detected! Spec differs from baseline.")
        print("Run `python scripts/diff_spec.py` to see what changed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 2: Test it manually**

```bash
python scripts/fetch_spec.py
```

Expected: Prints "Fetching...", saves `specs/latest.json`, reports "No baseline.json found."

**Step 3: Set baseline from latest**

```bash
cp specs/latest.json specs/baseline.json
```

**Step 4: Verify no-diff detection**

```bash
python scripts/fetch_spec.py
echo $?
```

Expected: "No changes detected. Spec matches baseline." Exit code 1.

**Step 5: Commit**

```bash
git add scripts/fetch_spec.py specs/baseline.json
git commit -m "feat: add fetch_spec.py and initial baseline OAS spec"
```

---

### Task 3: `scripts/diff_spec.py` — Structured spec diffing

**Files:**
- Create: `scripts/diff_spec.py`

**Step 1: Write the script**

This is the most complex script. It compares two OAS specs and produces a categorized markdown report.

```python
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

    baseline = load_json(baseline_path)
    latest = load_json(latest_path)

    report = generate_report(baseline, latest)
    print(report)

    report_path = project_root / "specs" / "diff-report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 2: Test with identical specs (no diff)**

```bash
python scripts/diff_spec.py
```

Expected: All sections show "No ... endpoints/changes." since baseline == latest.

**Step 3: Commit**

```bash
git add scripts/diff_spec.py
git commit -m "feat: add diff_spec.py for structured OAS spec diffing"
```

---

### Task 4: `scripts/audit_sdk.py` — SDK coverage audit

**Files:**
- Create: `scripts/audit_sdk.py`

**Step 1: Write the script**

This script auto-maps OAS operations to SDK resource methods by converting operationId to snake_case, then scans Python files for matches.

```python
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
```

**Step 2: Test the audit**

```bash
python scripts/audit_sdk.py
```

Expected: Produces a coverage report showing mapped/unmapped operations, any parameter drift, and enum issues.

**Step 3: Commit**

```bash
git add scripts/audit_sdk.py
git commit -m "feat: add audit_sdk.py for SDK coverage auditing against OAS spec"
```

---

### Task 5: Integration test infrastructure

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/pytest.ini` (or add `pytest` section to `setup.cfg`)
- Create: `.env.example`

**Step 1: Create `.env.example`**

```
# Copy to .env and fill in your values
ETSY_API_KEY=your_api_key_here
ETSY_ACCESS_TOKEN=your_access_token_here
ETSY_REFRESH_TOKEN=your_refresh_token_here
ETSY_SHOP_ID=your_shop_id_here
ETSY_TOKEN_EXPIRY=2026-12-31T00:00:00Z
```

**Step 2: Create `pytest.ini`**

```ini
[pytest]
testpaths = tests
markers =
    readonly: Tests that only read data (safe to run anytime)
    write: Tests that create/modify/delete data on the test shop
```

**Step 3: Create `tests/conftest.py`**

```python
import os
from datetime import datetime, timezone

import pytest

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from etsy_python.v3.resources.Session import EtsyClient


def _get_env(name: str) -> str:
    """Get a required environment variable."""
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"Missing required env var: {name}")
    return value


@pytest.fixture(scope="session")
def api_key() -> str:
    return _get_env("ETSY_API_KEY")


@pytest.fixture(scope="session")
def shop_id() -> int:
    return int(_get_env("ETSY_SHOP_ID"))


@pytest.fixture(scope="session")
def etsy_client(api_key) -> EtsyClient:
    """Create an EtsyClient for the test session."""
    access_token = _get_env("ETSY_ACCESS_TOKEN")
    refresh_token = _get_env("ETSY_REFRESH_TOKEN")
    expiry_str = _get_env("ETSY_TOKEN_EXPIRY")

    try:
        expiry = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
    except ValueError:
        expiry = datetime.now(tz=timezone.utc)

    return EtsyClient(
        keystring=api_key,
        access_token=access_token,
        refresh_token=refresh_token,
        expiry=expiry,
    )
```

**Step 4: Verify pytest discovers the infrastructure**

```bash
pytest --co -q
```

Expected: Shows "no tests ran" (no test files yet), but no import/config errors.

**Step 5: Commit**

```bash
git add tests/conftest.py pytest.ini .env.example
git commit -m "feat: add integration test infrastructure with pytest and env config"
```

---

### Task 6: Integration tests — read-only endpoints

**Files:**
- Create: `tests/test_misc.py`
- Create: `tests/test_user.py`
- Create: `tests/test_taxonomy.py`
- Create: `tests/test_shop.py`

**Step 1: Write `tests/test_misc.py`**

```python
import pytest

from etsy_python.v3.resources.Miscellaneous import MiscellaneousResource
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestMiscellaneous:
    def test_ping(self, etsy_client):
        resource = MiscellaneousResource(session=etsy_client)
        response = resource.ping()
        assert isinstance(response, Response)
        assert response.code == 200

    def test_token_scopes(self, etsy_client, api_key):
        from etsy_python.v3.models.Miscellaneous import GetTokenScopes

        resource = MiscellaneousResource(session=etsy_client)
        scopes_request = GetTokenScopes(token=etsy_client.access_token)
        response = resource.token_scopes(scopes_request)
        assert isinstance(response, Response)
        assert response.code == 200
```

**Step 2: Write `tests/test_user.py`**

```python
import pytest

from etsy_python.v3.resources.User import UserResource
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestUser:
    def test_get_me(self, etsy_client):
        resource = UserResource(session=etsy_client)
        response = resource.get_me()
        assert isinstance(response, Response)
        assert response.code == 200
        assert "user_id" in response.message

    def test_get_user(self, etsy_client):
        resource = UserResource(session=etsy_client)
        user_id = int(etsy_client.user_id)
        response = resource.get_user(user_id)
        assert isinstance(response, Response)
        assert response.code == 200
```

**Step 3: Write `tests/test_taxonomy.py`**

```python
import pytest

from etsy_python.v3.resources.Taxonomy import (
    BuyerTaxonomyResource,
    SellerTaxonomyResource,
)
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestBuyerTaxonomy:
    def test_get_buyer_taxonomy_nodes(self, etsy_client):
        resource = BuyerTaxonomyResource(session=etsy_client)
        response = resource.get_buyer_taxonomy_nodes()
        assert isinstance(response, Response)
        assert response.code == 200
        assert "results" in response.message

    def test_get_properties_by_buyer_taxonomy_id(self, etsy_client):
        resource = BuyerTaxonomyResource(session=etsy_client)
        # Taxonomy ID 1 is a root node that should always exist
        response = resource.get_properties_by_buyer_taxonomy_id(taxonomy_id=1)
        assert isinstance(response, Response)
        assert response.code == 200


@pytest.mark.readonly
class TestSellerTaxonomy:
    def test_get_seller_taxonomy_nodes(self, etsy_client):
        resource = SellerTaxonomyResource(session=etsy_client)
        response = resource.get_seller_taxonomy_nodes()
        assert isinstance(response, Response)
        assert response.code == 200
        assert "results" in response.message
```

**Step 4: Write `tests/test_shop.py`**

```python
import pytest

from etsy_python.v3.resources.Shop import ShopResource
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestShop:
    def test_get_shop(self, etsy_client, shop_id):
        resource = ShopResource(session=etsy_client)
        response = resource.get_shop(shop_id)
        assert isinstance(response, Response)
        assert response.code == 200
        assert "shop_id" in response.message

    def test_get_shop_by_owner_user_id(self, etsy_client):
        resource = ShopResource(session=etsy_client)
        user_id = int(etsy_client.user_id)
        response = resource.get_shop_by_owner_user_id(user_id)
        assert isinstance(response, Response)
        assert response.code == 200
```

**Step 5: Run the read-only tests**

```bash
pytest tests/ -m readonly -v
```

Expected: All pass (assuming valid credentials in `.env`).

**Step 6: Commit**

```bash
git add tests/test_misc.py tests/test_user.py tests/test_taxonomy.py tests/test_shop.py
git commit -m "feat: add read-only integration tests for misc, user, taxonomy, shop"
```

---

### Task 7: Integration tests — listing CRUD

**Files:**
- Create: `tests/test_listing.py`

**Step 1: Write `tests/test_listing.py`**

```python
import pytest

from etsy_python.v3.enums.Listing import (
    WhoMade,
    WhenMade,
    State,
    Includes,
)
from etsy_python.v3.models.Listing import (
    CreateDraftListingRequest,
    UpdateListingRequest,
)
from etsy_python.v3.resources.Listing import ListingResource
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestListingRead:
    def test_find_all_listings_active(self, etsy_client):
        resource = ListingResource(session=etsy_client)
        response = resource.find_all_listings_active(limit=5)
        assert isinstance(response, Response)
        assert response.code == 200

    def test_get_listings_by_shop(self, etsy_client, shop_id):
        resource = ListingResource(session=etsy_client)
        response = resource.get_listings_by_shop(shop_id, limit=5)
        assert isinstance(response, Response)
        assert response.code == 200


@pytest.mark.write
class TestListingCRUD:
    """Full lifecycle test: create -> read -> update -> delete."""

    @pytest.fixture
    def listing_resource(self, etsy_client):
        return ListingResource(session=etsy_client)

    @pytest.fixture
    def taxonomy_id(self, etsy_client):
        """Get a valid taxonomy ID from the API."""
        from etsy_python.v3.resources.Taxonomy import SellerTaxonomyResource

        resource = SellerTaxonomyResource(session=etsy_client)
        response = resource.get_seller_taxonomy_nodes()
        nodes = response.message.get("results", [])
        # Pick first leaf node or first node
        for node in nodes:
            if node.get("children_ids") == []:
                return node["id"]
        return nodes[0]["id"] if nodes else 1

    def test_listing_lifecycle(self, listing_resource, shop_id, taxonomy_id):
        # CREATE
        create_request = CreateDraftListingRequest(
            quantity=1,
            title="SDK Integration Test Listing - DO NOT BUY",
            description="Automated test listing created by etsy-python-sdk integration tests. This will be deleted.",
            price=9.99,
            who_made=WhoMade.I_DID,
            when_made=WhenMade.TWENTY_TWENTIES,
            taxonomy_id=taxonomy_id,
        )
        create_response = listing_resource.create_draft_listing(
            shop_id, create_request
        )
        assert isinstance(create_response, Response)
        assert create_response.code == 201
        listing_id = create_response.message["listing_id"]

        try:
            # READ
            get_response = listing_resource.get_listing(listing_id)
            assert isinstance(get_response, Response)
            assert get_response.code == 200
            assert get_response.message["title"] == "SDK Integration Test Listing - DO NOT BUY"

            # UPDATE
            update_request = UpdateListingRequest(
                title="SDK Integration Test Listing UPDATED",
            )
            update_response = listing_resource.update_listing(
                shop_id, listing_id, update_request
            )
            assert isinstance(update_response, Response)
            assert update_response.code == 200
            assert update_response.message["title"] == "SDK Integration Test Listing UPDATED"

        finally:
            # DELETE (always cleanup)
            delete_response = listing_resource.delete_listing(listing_id)
            assert isinstance(delete_response, Response)
```

**Step 2: Run write tests**

```bash
pytest tests/test_listing.py -m write -v
```

Expected: Creates a draft listing, reads/updates it, then deletes it.

**Step 3: Commit**

```bash
git add tests/test_listing.py
git commit -m "feat: add listing CRUD integration tests"
```

---

### Task 8: Integration tests — shipping and receipt

**Files:**
- Create: `tests/test_shipping_profile.py`
- Create: `tests/test_receipt.py`

**Step 1: Write `tests/test_shipping_profile.py`**

```python
import pytest

from etsy_python.v3.resources.ShippingProfile import ShippingProfileResource
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestShippingProfileRead:
    def test_get_shop_shipping_profiles(self, etsy_client, shop_id):
        resource = ShippingProfileResource(session=etsy_client)
        response = resource.get_shop_shipping_profiles(shop_id)
        assert isinstance(response, Response)
        assert response.code == 200

    def test_get_shipping_carriers(self, etsy_client):
        resource = ShippingProfileResource(session=etsy_client)
        response = resource.get_shipping_carriers(origin_country_iso="US")
        assert isinstance(response, Response)
        assert response.code == 200


@pytest.mark.readonly
class TestReceiptRead:
    def test_get_shop_receipts(self, etsy_client, shop_id):
        from etsy_python.v3.resources.Receipt import ReceiptResource

        resource = ReceiptResource(session=etsy_client)
        response = resource.get_shop_receipts(shop_id)
        assert isinstance(response, Response)
        assert response.code == 200
```

**Step 2: Write `tests/test_receipt.py`**

```python
import pytest

from etsy_python.v3.resources.Receipt import ReceiptResource
from etsy_python.v3.resources.ReceiptTransactions import ReceiptTransactionsResource
from etsy_python.v3.resources.Payment import PaymentResource
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestReceipt:
    def test_get_shop_receipts(self, etsy_client, shop_id):
        resource = ReceiptResource(session=etsy_client)
        response = resource.get_shop_receipts(shop_id)
        assert isinstance(response, Response)
        assert response.code == 200

    def test_get_shop_receipt_transactions_by_shop(self, etsy_client, shop_id):
        resource = ReceiptTransactionsResource(session=etsy_client)
        response = resource.get_shop_receipt_transaction_by_shop(shop_id)
        assert isinstance(response, Response)
        assert response.code == 200


@pytest.mark.readonly
class TestPayment:
    def test_get_payments(self, etsy_client, shop_id):
        resource = PaymentResource(session=etsy_client)
        response = resource.get_payments(shop_id)
        assert isinstance(response, Response)
        assert response.code == 200
```

**Step 3: Run all tests**

```bash
pytest tests/ -v
```

**Step 4: Commit**

```bash
git add tests/test_shipping_profile.py tests/test_receipt.py
git commit -m "feat: add shipping profile and receipt integration tests"
```

---

### Task 9: Claude Code skills

**Files:**
- Create: `.claude/skills/maintain/check.md`
- Create: `.claude/skills/maintain/audit.md`
- Create: `.claude/skills/maintain/test.md`

**Step 1: Create `.claude/skills/maintain/check.md`**

```markdown
---
name: check
description: Fetch the latest Etsy OAS spec and diff it against the baseline to detect API changes
---

# Check for Etsy API Changes

## Steps

1. Run the fetch script to download the latest spec:
   ```bash
   python scripts/fetch_spec.py
   ```

2. If changes were detected (exit code 0), run the diff script:
   ```bash
   python scripts/diff_spec.py
   ```

3. Read the diff report at `specs/diff-report.md` and present a summary to the user.

4. Highlight:
   - **Breaking changes** (removed endpoints, removed parameters, type changes)
   - **New endpoints** that may need SDK support
   - **Deprecations** that should be noted
   - **Enum changes** that may require updating SDK enums

5. If no changes detected, report that the SDK is up to date with the spec.

6. Suggest next steps:
   - Run `/maintain:audit` to check how these changes affect SDK coverage
   - Check https://github.com/etsy/open-api/releases for human-readable changelogs
```

**Step 2: Create `.claude/skills/maintain/audit.md`**

```markdown
---
name: audit
description: Audit SDK coverage against the Etsy OAS spec to find gaps, drift, and stale enums
---

# Audit SDK Coverage

## Steps

1. Run the audit script:
   ```bash
   python scripts/audit_sdk.py
   ```

2. Read the audit report at `specs/audit-report.md` and present findings to the user.

3. For each category of findings, provide actionable guidance:

   **Missing Endpoints:**
   - Show the OAS operation details (method, path, parameters)
   - Identify which resource file should contain the new method
   - Offer to implement the missing method following existing patterns

   **Extra SDK Methods:**
   - Check if the method was removed from the spec or renamed
   - Suggest deprecation or removal

   **Parameter Drift:**
   - Show what the spec expects vs what the SDK has
   - Identify the specific file and line to modify
   - Offer to update the method signature or model class

   **Enum Staleness:**
   - Show missing/extra enum values
   - Identify the enum file to update
   - Offer to add missing values

4. Suggest next steps:
   - Implement the changes identified
   - Run `/maintain:test` to validate changes work against the live API
   - After all changes are applied, update the baseline:
     ```bash
     cp specs/latest.json specs/baseline.json
     ```
```

**Step 3: Create `.claude/skills/maintain/test.md`**

```markdown
---
name: test
description: Run integration tests against the live Etsy API to validate SDK functionality
---

# Run Integration Tests

## Prerequisites

Ensure `.env` file exists with valid credentials (see `.env.example`).

## Steps

1. Ask the user what scope of tests to run:
   - **All tests**: `pytest tests/ -v`
   - **Read-only only**: `pytest tests/ -m readonly -v`
   - **Write tests only**: `pytest tests/ -m write -v`
   - **Specific resource**: `pytest tests/test_<resource>.py -v`

2. Run the selected tests.

3. For any failures:
   - Read the test file and the corresponding resource/model code
   - Determine if the failure is due to:
     - SDK bug (fix the SDK code)
     - API change (update SDK to match new API behavior)
     - Test environment issue (credentials, permissions, test data)
   - Offer to fix the issue

4. Report a summary:
   - Total tests run / passed / failed / skipped
   - Rate limit info if available
   - Any patterns in failures (e.g., all receipt tests failing = auth scope issue)
```

**Step 4: Commit**

```bash
git add .claude/skills/maintain/check.md .claude/skills/maintain/audit.md .claude/skills/maintain/test.md
git commit -m "feat: add Claude Code skills for /maintain:check, /maintain:audit, /maintain:test"
```

---

### Task 10: Final validation and documentation

**Files:**
- Modify: `CLAUDE.md` (add maintenance workflow section)

**Step 1: Run the full workflow once to validate**

```bash
python scripts/fetch_spec.py
python scripts/diff_spec.py
python scripts/audit_sdk.py
pytest tests/ -m readonly -v
```

**Step 2: Add maintenance workflow section to CLAUDE.md**

Add after the "## Commands" section:

```markdown
### Maintenance Workflow
```bash
# Check for Etsy API changes
python scripts/fetch_spec.py          # Fetch latest OAS spec
python scripts/diff_spec.py           # Diff against baseline

# Audit SDK coverage
python scripts/audit_sdk.py           # Compare spec vs SDK code

# Run integration tests
pytest tests/ -v                      # All tests
pytest tests/ -m readonly -v          # Read-only tests only
pytest tests/ -m write -v             # Write tests only

# After applying changes, update baseline
cp specs/latest.json specs/baseline.json

# Claude Code skills (interactive)
# /maintain:check   - Fetch + diff spec
# /maintain:audit   - Audit SDK coverage
# /maintain:test    - Run integration tests
```
```

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add maintenance workflow section to CLAUDE.md"
```

---

## Execution Order and Dependencies

```
Task 1 (scaffolding)
  -> Task 2 (fetch_spec.py) -- needs specs/ dir
    -> Task 3 (diff_spec.py) -- needs baseline.json from task 2
    -> Task 4 (audit_sdk.py) -- needs baseline.json from task 2
  -> Task 5 (test infrastructure) -- needs requirements-dev.txt
    -> Task 6 (read-only tests)
    -> Task 7 (listing CRUD tests)
    -> Task 8 (shipping/receipt tests)
  -> Task 9 (Claude Code skills) -- independent, can run in parallel
Task 10 (final validation) -- depends on all above
```

Tasks 3, 4, and 9 can run in parallel after Task 2 completes.
Tasks 6, 7, and 8 can run in parallel after Task 5 completes.
