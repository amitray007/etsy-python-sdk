#!/usr/bin/env python3
"""
Audit SDK coverage against the Etsy OAS spec.

Auto-infers mappings from OAS operationIds to SDK resource methods by:
1. Converting operationId (camelCase) to snake_case
2. Scanning resource files for matching method names
3. Comparing parameters, request body fields, and enums

Usage:
    python scripts/audit_sdk.py
    python scripts/audit_sdk.py --spec specs/baseline.json

Output: Markdown report to stdout and specs/audit-report.md
"""

import ast
import io
import json
import re
import sys
import argparse
import tokenize
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def camel_to_snake(name: str) -> str:
    """Convert camelCase/PascalCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


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
        content.get(
            "application/x-www-form-urlencoded",
            content.get("multipart/form-data", {}),
        ),
    )
    schema = json_content.get("schema", {})
    schema = resolve_ref(schema, spec)
    return set(schema.get("properties", {}).keys())


def get_request_body_schema(op: dict, spec: dict) -> Optional[dict]:
    """Get full request body schema with required fields and property details."""
    rb = op.get("requestBody")
    if not rb:
        return None
    content = rb.get("content", {})
    json_content = content.get(
        "application/json",
        content.get(
            "application/x-www-form-urlencoded",
            content.get("multipart/form-data", {}),
        ),
    )
    schema = json_content.get("schema", {})
    schema = resolve_ref(schema, spec)
    if not schema.get("properties"):
        return None
    properties = {}
    for name, prop in schema.get("properties", {}).items():
        prop = resolve_ref(prop, spec)
        properties[name] = {
            "type": prop.get("type", "unknown"),
            "enum": prop.get("enum"),
            "deprecated": prop.get("deprecated", False),
            "description": prop.get("description", ""),
        }
    return {
        "required": schema.get("required", []),
        "properties": properties,
    }


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
    """Scan all resource .py files and extract method names, parameters, and annotations."""
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
                        param_annotations = {}
                        for arg in item.args.args:
                            if arg.arg != "self":
                                params.append(arg.arg)
                                if arg.annotation and isinstance(arg.annotation, ast.Name):
                                    param_annotations[arg.arg] = arg.annotation.id

                        # Detect NotImplementedError stubs
                        is_not_implemented = False
                        if len(item.body) == 1:
                            stmt = item.body[0]
                            if isinstance(stmt, ast.Raise) and stmt.exc is not None:
                                exc = stmt.exc
                                if (
                                    isinstance(exc, ast.Name)
                                    and exc.id == "NotImplementedError"
                                ) or (
                                    isinstance(exc, ast.Call)
                                    and isinstance(exc.func, ast.Name)
                                    and exc.func.id == "NotImplementedError"
                                ):
                                    is_not_implemented = True

                        file_methods[item.name] = {
                            "params": params,
                            "param_annotations": param_annotations,
                            "class": node.name,
                            "file": py_file.name,
                            "line": item.lineno,
                            "not_implemented": is_not_implemented,
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


def scan_model_fields(models_dir: Path) -> Dict[str, dict]:
    """Scan model .py files and extract class init params, nullable, and mandatory lists."""
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
                init_params = set()
                nullable_fields: List[str] = []
                mandatory_fields: List[str] = []

                for item in node.body:
                    # Extract __init__ params
                    if (
                        isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and item.name == "__init__"
                    ):
                        for arg in item.args.args:
                            if arg.arg != "self":
                                init_params.add(arg.arg)

                    # Extract class-level nullable/mandatory lists (plain assign)
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and isinstance(
                                item.value, ast.List
                            ):
                                values = [
                                    e.value
                                    for e in item.value.elts
                                    if isinstance(e, ast.Constant)
                                ]
                                if target.id == "nullable":
                                    nullable_fields = values
                                elif target.id == "mandatory":
                                    mandatory_fields = values

                    # Extract class-level nullable/mandatory lists (annotated assign)
                    if isinstance(item, ast.AnnAssign):
                        if (
                            isinstance(item.target, ast.Name)
                            and item.value
                            and isinstance(item.value, ast.List)
                        ):
                            values = [
                                e.value
                                for e in item.value.elts
                                if isinstance(e, ast.Constant)
                            ]
                            if item.target.id == "nullable":
                                nullable_fields = values
                            elif item.target.id == "mandatory":
                                mandatory_fields = values

                if init_params:
                    models[node.name] = {
                        "init_params": init_params,
                        "nullable": nullable_fields,
                        "mandatory": mandatory_fields,
                        "file": py_file.name,
                        "line": node.lineno,
                    }

    return models


def scan_init_exports(init_path: Path) -> Set[str]:
    """Parse resources/__init__.py to find all imported names."""
    if not init_path.exists():
        return set()
    try:
        tree = ast.parse(init_path.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    exported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                exported.add(alias.name if alias.asname is None else alias.asname)
    return exported


def scan_string_concat_issues(directory: Path) -> List[dict]:
    """Detect implicit string concatenation in list literals inside .py files.

    Two adjacent STRING tokens without a comma between them indicate
    accidental concatenation like: "foo" "bar" -> "foobar".
    """
    issues = []
    for py_file in sorted(directory.glob("*.py")):
        if py_file.name.startswith("__"):
            continue
        try:
            code = py_file.read_text(encoding="utf-8")
            tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
        except (tokenize.TokenError, SyntaxError):
            continue

        prev_tok = None
        for tok in tokens:
            if tok.type == tokenize.STRING:
                if prev_tok is not None and prev_tok.type == tokenize.STRING:
                    issues.append(
                        {
                            "file": py_file.name,
                            "line": prev_tok.start[0],
                            "strings": f"{prev_tok.string} {tok.string}",
                        }
                    )
                prev_tok = tok
            elif tok.type in (
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.COMMENT,
                tokenize.INDENT,
                tokenize.DEDENT,
            ):
                pass  # whitespace-like tokens, keep prev
            else:
                prev_tok = None
    return issues


def detect_description_deprecations(spec: dict) -> List[dict]:
    """Find fields with deprecation notices in their descriptions."""
    deprecations = []
    dep_pattern = re.compile(r"\[DEPRECATED\]|deprecated", re.IGNORECASE)

    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue
            op_id = details.get("operationId", f"{method}:{path}")

            # Check parameters
            for p in details.get("parameters", []):
                desc = p.get("description", "")
                if dep_pattern.search(desc):
                    deprecations.append(
                        {
                            "operation": op_id,
                            "location": "parameter",
                            "field": p["name"],
                            "description_snippet": desc[:120],
                        }
                    )

            # Check request body fields
            rb = details.get("requestBody")
            if rb:
                content = rb.get("content", {})
                for ct, ct_d in content.items():
                    schema = ct_d.get("schema", {})
                    schema = resolve_ref(schema, spec)
                    for pname, pdef in schema.get("properties", {}).items():
                        pdef = resolve_ref(pdef, spec)
                        desc = pdef.get("description", "")
                        if dep_pattern.search(desc):
                            deprecations.append(
                                {
                                    "operation": op_id,
                                    "location": "body",
                                    "field": pname,
                                    "description_snippet": desc[:120],
                                }
                            )
    return deprecations


def build_method_index(
    resources: Dict[str, Dict[str, dict]],
) -> Dict[str, dict]:
    """Build a flat index of all SDK methods by snake_case name."""
    index = {}
    for resource_name, methods in resources.items():
        for method_name, info in methods.items():
            index[method_name] = {**info, "resource": resource_name}
    return index


# Known SDK field name -> spec field name mappings (used in todict via _type -> type)
TYPE_FIELD_ALIASES = {
    "listing_type": "type",
    "profile_type": "type",
}

# Common path parameter names that are always in the URL, not query params
PATH_PARAM_NAMES = {
    "shop_id",
    "listing_id",
    "receipt_id",
    "return_policy_id",
    "property_id",
    "shipping_profile_id",
    "listing_image_id",
    "listing_file_id",
    "video_id",
    "shop_section_id",
    "user_id",
    "policy_id",
    "payment_id",
    "transaction_id",
    "production_partner_id",
    "destination_id",
    "upgrade_id",
    "review_id",
    "address_id",
    "taxonomy_id",
    "holiday_id",
}


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

    # Separate stubs from implemented
    not_impl_methods = {
        op_id: m for op_id, m in mapped.items() if m["sdk"].get("not_implemented")
    }
    implemented = {
        op_id: m for op_id, m in mapped.items() if not m["sdk"].get("not_implemented")
    }

    # --- Coverage Summary ---
    total_ops = len(operations)
    mapped_count = len(mapped)
    not_impl_count = len(not_impl_methods)
    impl_count = mapped_count - not_impl_count

    # Scan for code issues
    concat_issues = scan_string_concat_issues(models_dir)
    concat_issues.extend(scan_string_concat_issues(resources_dir))

    # Scan for missing exports
    init_exports = scan_init_exports(resources_dir / "__init__.py")
    all_resource_classes = set()
    for resource_name, methods in resources.items():
        for method_name, info in methods.items():
            cls = info["class"]
            if cls.endswith("Resource"):
                all_resource_classes.add((cls, info["file"]))
    missing_exports = [
        (cls, f) for cls, f in sorted(all_resource_classes) if cls not in init_exports
    ]

    # Deprecation notices
    deprecations = detect_description_deprecations(spec)

    lines.append("## Coverage Summary\n")
    lines.append(f"- Total OAS operations: {total_ops}")
    lines.append(f"- Mapped to SDK methods: {mapped_count} ({impl_count} implemented, {not_impl_count} stubs)")
    lines.append(f"- Missing from SDK: {len(unmapped)}")
    lines.append(f"- Extra SDK methods (no OAS match): {len(extra_methods)}")
    lines.append(f"- Code issues found: {len(concat_issues)}")
    lines.append(f"- Missing exports: {len(missing_exports)}")
    pct = (impl_count / total_ops * 100) if total_ops > 0 else 0
    lines.append(f"- Effective coverage: {pct:.1f}%\n")

    # --- Missing Endpoints ---
    lines.append("## Missing Endpoints\n")
    lines.append("OAS operations with no matching SDK method.\n")
    if unmapped:
        for op_id, op_info in unmapped:
            snake = camel_to_snake(op_id)
            dep = " (DEPRECATED)" if op_info["deprecated"] else ""
            lines.append(f"- **{op_id}** -> `{snake}`{dep}")
            lines.append(f"  `{op_info['method']} {op_info['path']}`")
            lines.append(f"  Tags: {', '.join(op_info['tags'])}")

            # Show request body schema for implementers
            body_schema = get_request_body_schema(op_info, spec)
            if body_schema:
                required = body_schema["required"]
                req_str = ", ".join(required) if required else "none"
                lines.append(f"  Request body (required: {req_str}):")
                for fname, finfo in sorted(body_schema["properties"].items()):
                    type_str = finfo["type"]
                    if finfo.get("enum"):
                        type_str += f", enum: {', '.join(str(v) for v in finfo['enum'])}"
                    lines.append(f"    - `{fname}`: {type_str}")
    else:
        lines.append("All OAS operations are covered!\n")

    # --- Not Implemented Stubs ---
    lines.append("\n## Not Implemented Stubs\n")
    lines.append("SDK methods that exist but raise NotImplementedError.\n")
    if not_impl_methods:
        for op_id, m in sorted(not_impl_methods.items()):
            sdk = m["sdk"]
            spec_info = m["spec"]
            lines.append(
                f"- **{m['sdk_method']}** in `{sdk['file']}:{sdk['line']}` ({sdk['class']})"
            )
            lines.append(
                f"  Spec: `{spec_info['method']} {spec_info['path']}`"
            )
    else:
        lines.append("No stubs found.\n")

    # --- Extra SDK Methods ---
    lines.append("\n## Extra SDK Methods\n")
    lines.append("SDK methods with no matching OAS operation (possibly removed or renamed).\n")
    if extra_methods:
        for method_name, info in sorted(extra_methods):
            lines.append(
                f"- **{method_name}** in `{info['file']}:{info['line']}` ({info['class']})"
            )
    else:
        lines.append("No extra methods found.\n")

    # --- Missing Exports ---
    lines.append("\n## Missing Exports\n")
    lines.append("Resource classes found in files but not imported in `resources/__init__.py`.\n")
    if missing_exports:
        for cls, filename in missing_exports:
            lines.append(f"- **{cls}** in `{filename}`")
    else:
        lines.append("All resource classes are exported.\n")

    # --- Query/Path Parameter Drift ---
    lines.append("\n## Query/Path Parameter Drift\n")
    lines.append("Mismatches between OAS path/query params and SDK method signatures.\n")
    any_query_drift = False
    for op_id, mapping in sorted(implemented.items()):
        op = mapping["spec"]
        sdk = mapping["sdk"]

        spec_params = {p["name"] for p in op["parameters"]}
        sdk_params = set(sdk["params"])
        param_annotations = sdk.get("param_annotations", {})

        # Exclude model-object params from method signature comparison
        model_param_names = set()
        for pname, ptype in param_annotations.items():
            if ptype in sdk_models:
                model_param_names.add(pname)

        non_model_sdk_params = sdk_params - model_param_names
        spec_only = spec_params - non_model_sdk_params
        sdk_only = non_model_sdk_params - spec_params - PATH_PARAM_NAMES

        if spec_only or sdk_only:
            any_query_drift = True
            lines.append(
                f"### {op_id} (`{mapping['sdk_method']}` in {sdk['file']}:{sdk['line']})\n"
            )
            if spec_only:
                lines.append(f"- In spec but not SDK: {', '.join(sorted(spec_only))}")
            if sdk_only:
                lines.append(f"- In SDK but not spec: {', '.join(sorted(sdk_only))}")
            lines.append("")

    if not any_query_drift:
        lines.append("No query/path parameter drift detected.\n")

    # --- Request Body Drift ---
    lines.append("\n## Request Body Drift\n")
    lines.append("Mismatches between OAS request body fields and SDK model class fields.\n")
    any_body_drift = False
    for op_id, mapping in sorted(implemented.items()):
        op = mapping["spec"]
        sdk = mapping["sdk"]

        spec_body_fields = get_request_body_fields(op, spec)
        if not spec_body_fields:
            continue

        # Skip multipart/form-data endpoints (FileRequest subclasses have different patterns)
        rb = op.get("requestBody", {})
        content = rb.get("content", {}) if rb else {}
        if "multipart/form-data" in content and "application/json" not in content:
            continue

        param_annotations = sdk.get("param_annotations", {})

        # Find the model class used by this method
        model_class_name = None
        for pname, ptype in param_annotations.items():
            if ptype in sdk_models:
                model_class_name = ptype
                break

        if model_class_name:
            model_info = sdk_models[model_class_name]
            model_fields = model_info["init_params"]
            # Normalize known aliases (_type -> type mapping in todict)
            normalized_model_fields = set()
            for f in model_fields:
                if f in TYPE_FIELD_ALIASES:
                    normalized_model_fields.add(TYPE_FIELD_ALIASES[f])
                else:
                    normalized_model_fields.add(f)

            body_spec_only = spec_body_fields - normalized_model_fields
            body_sdk_only = normalized_model_fields - spec_body_fields

            if body_spec_only or body_sdk_only:
                any_body_drift = True
                lines.append(
                    f"### {op_id} (model `{model_class_name}` in models/{model_info['file']}:{model_info['line']})\n"
                )
                if body_spec_only:
                    lines.append(
                        f"- In spec but not model: {', '.join(sorted(body_spec_only))}"
                    )
                if body_sdk_only:
                    lines.append(
                        f"- In model but not spec: {', '.join(sorted(body_sdk_only))}"
                    )
                lines.append("")
        else:
            # Method has body fields but no model object - compare against method params
            sdk_params = set(sdk["params"])
            body_spec_only = spec_body_fields - sdk_params
            body_sdk_only = sdk_params - spec_body_fields - {
                p["name"] for p in op["parameters"]
            } - PATH_PARAM_NAMES

            if body_spec_only or body_sdk_only:
                any_body_drift = True
                lines.append(
                    f"### {op_id} (`{mapping['sdk_method']}` in {sdk['file']}:{sdk['line']}, no model class)\n"
                )
                if body_spec_only:
                    lines.append(
                        f"- In spec but not SDK: {', '.join(sorted(body_spec_only))}"
                    )
                if body_sdk_only:
                    lines.append(
                        f"- In SDK but not spec: {', '.join(sorted(body_sdk_only))}"
                    )
                lines.append("")

    if not any_body_drift:
        lines.append("No request body drift detected.\n")

    # --- Enum Staleness ---
    lines.append("\n## Enum Staleness\n")
    lines.append("OAS enum values not reflected in SDK enum classes.\n")
    spec_enums = get_spec_enums(spec)
    any_enum_issues = False

    for spec_key, spec_values in sorted(spec_enums.items()):
        # Extract property name from spec key (Schema.property_name)
        prop_name = spec_key.split(".")[-1] if "." in spec_key else spec_key
        expected_enum_name = snake_to_pascal(prop_name)

        # Try name-based match first
        best_match = None
        if expected_enum_name in sdk_enums:
            best_match = expected_enum_name
        else:
            # Fall back to overlap matching with threshold
            best_overlap = 0
            for sdk_name, sdk_values in sdk_enums.items():
                sdk_value_set = {str(v).lower() for v in sdk_values}
                spec_value_set = {str(v).lower() for v in spec_values}
                overlap = len(sdk_value_set & spec_value_set)
                smaller_set = min(len(sdk_value_set), len(spec_value_set))
                min_required = max(2, smaller_set // 2)
                if overlap >= min_required and overlap > best_overlap:
                    best_overlap = overlap
                    best_match = sdk_name

        if best_match:
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

    # --- Deprecation Notices ---
    lines.append("\n## Deprecation Notices\n")
    lines.append("Fields with deprecation indicators in their spec descriptions.\n")
    if deprecations:
        # Group by operation
        by_op: Dict[str, List[dict]] = {}
        for d in deprecations:
            by_op.setdefault(d["operation"], []).append(d)
        for op_id, items in sorted(by_op.items()):
            lines.append(f"### {op_id}\n")
            for item in items:
                lines.append(
                    f"- {item['location']} `{item['field']}`: {item['description_snippet']}"
                )
            lines.append("")
    else:
        lines.append("No deprecation notices found.\n")

    # --- Code Issues ---
    lines.append("\n## Code Issues\n")
    lines.append("Potential bugs detected by static analysis.\n")
    if concat_issues:
        lines.append("### Implicit String Concatenation\n")
        lines.append(
            "Adjacent string literals without a comma — these silently concatenate into a single string.\n"
        )
        for issue in concat_issues:
            lines.append(f"- `{issue['file']}:{issue['line']}`: {issue['strings']}")
    else:
        lines.append("No code issues found.\n")

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
