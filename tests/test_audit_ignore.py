"""Tests for the externalized, self-verifying audit suppression mechanism and
the list-context fix to the implicit-string-concatenation detector in
``scripts/audit_sdk.py``.
"""

import json
import sys
from pathlib import Path

import pytest

# scripts/ is not a package; put it on the path so we can import the audit tool.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import audit_sdk  # noqa: E402


# --------------------------------------------------------------------------- #
# load_ignores
# --------------------------------------------------------------------------- #
class TestLoadIgnores:
    def test_missing_file_returns_empty(self, tmp_path):
        assert audit_sdk.load_ignores(tmp_path / "nope.json") == []

    def test_none_path_returns_empty(self):
        assert audit_sdk.load_ignores(None) == []

    def test_malformed_json_returns_empty(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("{not valid json", encoding="utf-8")
        assert audit_sdk.load_ignores(p) == []

    def test_valid_file_parsed(self, tmp_path):
        p = tmp_path / "ignore.json"
        p.write_text(
            json.dumps(
                {"ignores": [{"type": "extra_method", "key": "A.b", "reason": "x"}]}
            ),
            encoding="utf-8",
        )
        ignores = audit_sdk.load_ignores(p)
        assert len(ignores) == 1
        assert ignores[0]["key"] == "A.b"

    def test_non_dict_entries_filtered_out(self, tmp_path):
        p = tmp_path / "ignore.json"
        p.write_text(
            json.dumps({"ignores": [{"type": "extra_method", "key": "A.b"}, "garbage"]}),
            encoding="utf-8",
        )
        assert audit_sdk.load_ignores(p) == [{"type": "extra_method", "key": "A.b"}]

    def test_missing_ignores_key_returns_empty(self, tmp_path):
        p = tmp_path / "ignore.json"
        p.write_text(json.dumps({"something_else": []}), encoding="utf-8")
        assert audit_sdk.load_ignores(p) == []


# --------------------------------------------------------------------------- #
# partition_findings — atomic findings
# --------------------------------------------------------------------------- #
class TestPartitionAtomic:
    def test_unmatched_finding_stays_active(self):
        findings = [{"type": "extra_method", "key": "A.b"}]
        active, suppressed, stale = audit_sdk.partition_findings(findings, [])
        assert active == findings
        assert suppressed == []
        assert stale == []

    def test_matched_finding_is_suppressed(self):
        findings = [{"type": "extra_method", "key": "A.b"}]
        ignores = [{"type": "extra_method", "key": "A.b", "reason": "alias"}]
        active, suppressed, stale = audit_sdk.partition_findings(findings, ignores)
        assert active == []
        assert len(suppressed) == 1
        assert suppressed[0]["ignore"]["reason"] == "alias"
        assert stale == []

    def test_type_mismatch_does_not_match(self):
        findings = [{"type": "extra_method", "key": "A.b"}]
        ignores = [{"type": "code_issue", "key": "A.b"}]
        active, suppressed, stale = audit_sdk.partition_findings(findings, ignores)
        assert active == findings
        assert suppressed == []
        assert len(stale) == 1  # the ignore matched nothing

    def test_key_mismatch_does_not_match(self):
        findings = [{"type": "extra_method", "key": "A.b"}]
        ignores = [{"type": "extra_method", "key": "A.c"}]
        active, _, stale = audit_sdk.partition_findings(findings, ignores)
        assert active == findings
        assert len(stale) == 1


# --------------------------------------------------------------------------- #
# partition_findings — enum value verification
# --------------------------------------------------------------------------- #
class TestPartitionEnum:
    def _enum(self, direction, values):
        return {
            "type": "enum_staleness",
            "key": "Foo.state -> State",
            "direction": direction,
            "values": set(values),
            "sdk_enum": "State",
            "spec_key": "Foo.state",
        }

    def test_wildcard_suppresses_all(self):
        findings = [self._enum("missing", {"1", "2", "3"})]
        ignores = [
            {
                "type": "enum_staleness",
                "key": "Foo.state -> State",
                "direction": "missing",
                "values": "*",
            }
        ]
        active, suppressed, stale = audit_sdk.partition_findings(findings, ignores)
        assert active == []
        assert len(suppressed) == 1
        assert stale == []

    def test_listed_values_suppressed_exactly(self):
        findings = [self._enum("extra", {"removed"})]
        ignores = [
            {
                "type": "enum_staleness",
                "key": "Foo.state -> State",
                "direction": "extra",
                "values": ["removed"],
            }
        ]
        active, suppressed, stale = audit_sdk.partition_findings(findings, ignores)
        assert active == []
        assert len(suppressed) == 1
        assert suppressed[0]["values"] == {"removed"}
        assert stale == []

    def test_new_value_stays_active_while_known_value_suppressed(self):
        # Ignore covers "removed"; a newly-appeared "archived" must NOT be hidden.
        findings = [self._enum("extra", {"removed", "archived"})]
        ignores = [
            {
                "type": "enum_staleness",
                "key": "Foo.state -> State",
                "direction": "extra",
                "values": ["removed"],
            }
        ]
        active, suppressed, stale = audit_sdk.partition_findings(findings, ignores)
        assert len(active) == 1
        assert active[0]["values"] == {"archived"}
        assert len(suppressed) == 1
        assert suppressed[0]["values"] == {"removed"}
        assert stale == []  # the ignore did suppress "removed", so it is not stale

    def test_direction_mismatch_is_not_suppressed(self):
        findings = [self._enum("extra", {"removed"})]
        ignores = [
            {
                "type": "enum_staleness",
                "key": "Foo.state -> State",
                "direction": "missing",
                "values": "*",
            }
        ]
        active, suppressed, stale = audit_sdk.partition_findings(findings, ignores)
        assert len(active) == 1
        assert suppressed == []
        assert len(stale) == 1

    def test_value_case_insensitive(self):
        findings = [self._enum("extra", {"removed"})]
        ignores = [
            {
                "type": "enum_staleness",
                "key": "Foo.state -> State",
                "direction": "extra",
                "values": ["REMOVED"],
            }
        ]
        active, suppressed, _ = audit_sdk.partition_findings(findings, ignores)
        assert active == []
        assert len(suppressed) == 1


# --------------------------------------------------------------------------- #
# partition_findings — stale tracking
# --------------------------------------------------------------------------- #
class TestStaleTracking:
    def test_used_entry_not_stale_unused_entry_stale(self):
        findings = [{"type": "extra_method", "key": "A.b"}]
        ignores = [
            {"type": "extra_method", "key": "A.b", "reason": "used"},
            {"type": "extra_method", "key": "X.y", "reason": "stale"},
        ]
        active, suppressed, stale = audit_sdk.partition_findings(findings, ignores)
        assert active == []
        assert len(suppressed) == 1
        assert len(stale) == 1
        assert stale[0]["reason"] == "stale"

    def test_partial_enum_ignore_is_not_stale(self):
        finding = {
            "type": "enum_staleness",
            "key": "Foo.state -> State",
            "direction": "extra",
            "values": {"removed", "new"},
            "sdk_enum": "State",
            "spec_key": "Foo.state",
        }
        ignores = [
            {
                "type": "enum_staleness",
                "key": "Foo.state -> State",
                "direction": "extra",
                "values": ["removed"],
            }
        ]
        _, _, stale = audit_sdk.partition_findings([finding], ignores)
        assert stale == []


# --------------------------------------------------------------------------- #
# compute_enum_findings
# --------------------------------------------------------------------------- #
class TestComputeEnumFindings:
    def test_missing_value_detected(self):
        spec = {
            "components": {
                "schemas": {"Foo": {"properties": {"color": {"enum": ["red", "green", "blue"]}}}}
            }
        }
        findings = audit_sdk.compute_enum_findings(spec, {"Color": [["red", "green"]]})
        assert len(findings) == 1
        f = findings[0]
        assert f["direction"] == "missing"
        assert f["values"] == {"blue"}
        assert f["key"] == "Foo.color -> Color"

    def test_extra_value_detected(self):
        spec = {
            "components": {
                "schemas": {"Foo": {"properties": {"color": {"enum": ["red", "green"]}}}}
            }
        }
        findings = audit_sdk.compute_enum_findings(
            spec, {"Color": [["red", "green", "purple"]]}
        )
        assert len(findings) == 1
        assert findings[0]["direction"] == "extra"
        assert findings[0]["values"] == {"purple"}

    def test_in_sync_yields_no_findings(self):
        spec = {
            "components": {
                "schemas": {"Foo": {"properties": {"color": {"enum": ["red", "green"]}}}}
            }
        }
        assert audit_sdk.compute_enum_findings(spec, {"Color": [["red", "green"]]}) == []

    def test_duplicate_sdk_enum_name_picks_best_overlap(self):
        # Two SDK classes share the name "Includes" (Listing vs ListingInventory).
        # The comparison must pick the candidate that actually overlaps the spec
        # enum, not whichever was inserted last.
        spec = {
            "components": {
                "schemas": {"Foo": {"properties": {"includes": {"enum": ["a", "b", "c"]}}}}
            }
        }
        sdk_enums = {"Includes": [["listing"], ["a", "b", "c", "d"]]}
        findings = audit_sdk.compute_enum_findings(spec, sdk_enums)
        # Should match the ["a","b","c","d"] candidate: only "d" is extra.
        assert len(findings) == 1
        assert findings[0]["direction"] == "extra"
        assert findings[0]["values"] == {"d"}


# --------------------------------------------------------------------------- #
# compute_param_findings — query/path parameter drift
# --------------------------------------------------------------------------- #
class TestComputeParamFindings:
    def _implemented(self, spec_params, sdk_params, annotations=None):
        return {
            "getX": {
                "spec": {"parameters": [{"name": n} for n in spec_params]},
                "sdk": {
                    "params": list(sdk_params),
                    "param_annotations": annotations or {},
                    "file": "X.py",
                    "line": 10,
                },
                "sdk_method": "get_x",
            }
        }

    def test_extra_sdk_param_detected(self):
        findings = audit_sdk.compute_param_findings(
            self._implemented(["limit"], ["limit", "legacy"]), {}
        )
        assert len(findings) == 1
        assert findings[0]["type"] == "param_drift"
        assert findings[0]["key"] == "getX"
        assert findings[0]["direction"] == "extra"
        assert findings[0]["values"] == {"legacy"}
        assert findings[0]["location"] == "X.py:10"

    def test_missing_sdk_param_detected(self):
        findings = audit_sdk.compute_param_findings(
            self._implemented(["limit", "offset"], ["limit"]), {}
        )
        assert len(findings) == 1
        assert findings[0]["direction"] == "missing"
        assert findings[0]["values"] == {"offset"}

    def test_in_sync_yields_no_findings(self):
        assert (
            audit_sdk.compute_param_findings(
                self._implemented(["limit"], ["limit"]), {}
            )
            == []
        )

    def test_both_directions_yield_separate_findings(self):
        findings = audit_sdk.compute_param_findings(
            self._implemented(["limit"], ["legacy"]), {}
        )
        assert {f["direction"] for f in findings} == {"missing", "extra"}

    def test_model_payload_param_excluded(self):
        # A request-model argument is not a query param and must not be flagged.
        findings = audit_sdk.compute_param_findings(
            self._implemented(
                ["limit"], ["limit", "listing"], {"listing": "UpdateListingRequest"}
            ),
            {"UpdateListingRequest": {"init_params": []}},
        )
        assert findings == []

    def test_path_params_excluded(self):
        findings = audit_sdk.compute_param_findings(
            self._implemented(["limit"], ["limit", "shop_id"]), {}
        )
        assert findings == []


# --------------------------------------------------------------------------- #
# partition_findings — param_drift value verification
# --------------------------------------------------------------------------- #
class TestPartitionParamDrift:
    def _drift(self, values, direction="extra"):
        return {
            "type": "param_drift",
            "key": "getListing",
            "direction": direction,
            "values": set(values),
            "sdk_method": "get_listing",
            "location": "Listing.py:66",
        }

    def _ignore(self, values, direction="extra"):
        return {
            "type": "param_drift",
            "key": "getListing",
            "direction": direction,
            "values": values,
            "reason": "kept for backward compatibility",
        }

    def test_listed_param_suppressed(self):
        active, suppressed, stale = audit_sdk.partition_findings(
            [self._drift({"legacy"})], [self._ignore(["legacy"])]
        )
        assert active == []
        assert len(suppressed) == 1
        assert suppressed[0]["values"] == {"legacy"}
        assert stale == []

    def test_new_param_stays_active_while_known_param_suppressed(self):
        # The whole point: a newly drifted param on an already-suppressed
        # operation must still surface.
        active, suppressed, stale = audit_sdk.partition_findings(
            [self._drift({"legacy", "brand_new"})], [self._ignore(["legacy"])]
        )
        assert len(active) == 1
        assert active[0]["values"] == {"brand_new"}
        assert suppressed[0]["values"] == {"legacy"}
        assert stale == []

    def test_direction_mismatch_is_not_suppressed(self):
        active, suppressed, stale = audit_sdk.partition_findings(
            [self._drift({"legacy"}, "extra")],
            [self._ignore(["legacy"], "missing")],
        )
        assert len(active) == 1
        assert suppressed == []
        assert len(stale) == 1

    def test_resolved_drift_makes_ignore_stale(self):
        # Once the kwarg is actually removed, the entry suppresses nothing.
        active, suppressed, stale = audit_sdk.partition_findings(
            [], [self._ignore(["legacy"])]
        )
        assert active == [] and suppressed == []
        assert len(stale) == 1

    def test_omitted_values_suppresses_nothing(self):
        # A valued ignore with NO `values` key must NOT behave as a wildcard —
        # otherwise it would silently hide unreviewed drift. It suppresses
        # nothing (finding stays fully active) and self-reports as stale.
        ig = {
            "type": "param_drift",
            "key": "getListing",
            "direction": "extra",
            "reason": "no values key",
        }
        active, suppressed, stale = audit_sdk.partition_findings(
            [self._drift({"legacy", "unreviewed"})], [ig]
        )
        assert len(active) == 1
        assert active[0]["values"] == {"legacy", "unreviewed"}
        assert suppressed == []
        assert len(stale) == 1

    def test_explicit_wildcard_still_suppresses_all(self):
        # `"*"` written explicitly is still honoured (distinct from omission).
        active, suppressed, stale = audit_sdk.partition_findings(
            [self._drift({"legacy", "other"})], [self._ignore("*")]
        )
        assert active == []
        assert len(suppressed) == 1
        assert stale == []


# --------------------------------------------------------------------------- #
# get_spec_enums — parameter-level enum extraction
# --------------------------------------------------------------------------- #
class TestGetSpecEnums:
    def test_component_schema_enums_extracted(self):
        spec = {
            "components": {
                "schemas": {"Foo": {"properties": {"color": {"enum": ["red", "green"]}}}}
            }
        }
        assert audit_sdk.get_spec_enums(spec) == {"Foo.color": ["red", "green"]}

    def test_scalar_parameter_enum_extracted(self):
        spec = {
            "paths": {
                "/x": {
                    "get": {
                        "operationId": "getX",
                        "parameters": [
                            {"name": "state", "schema": {"enum": ["active", "draft"]}}
                        ],
                    }
                }
            }
        }
        assert audit_sdk.get_spec_enums(spec) == {"getX.state": ["active", "draft"]}

    def test_array_parameter_items_enum_extracted(self):
        # The `includes` filter is an array param: values live under
        # schema.items.enum, which was previously ignored entirely.
        spec = {
            "paths": {
                "/x": {
                    "get": {
                        "operationId": "getX",
                        "parameters": [
                            {
                                "name": "includes",
                                "schema": {
                                    "type": "array",
                                    "items": {"enum": ["Shop", "User"]},
                                },
                            }
                        ],
                    }
                }
            }
        }
        assert audit_sdk.get_spec_enums(spec) == {"getX.includes": ["Shop", "User"]}

    def test_parameter_without_enum_ignored(self):
        spec = {
            "paths": {
                "/x": {
                    "get": {
                        "operationId": "getX",
                        "parameters": [
                            {"name": "limit", "schema": {"type": "integer"}}
                        ],
                    }
                }
            }
        }
        assert audit_sdk.get_spec_enums(spec) == {}


# --------------------------------------------------------------------------- #
# scan_enum_values — duplicate class names across files
# --------------------------------------------------------------------------- #
class TestScanEnumValues:
    def test_same_name_across_files_kept_separately(self, tmp_path):
        (tmp_path / "A.py").write_text(
            "from enum import Enum\n\nclass Includes(Enum):\n    SHOP = 'Shop'\n",
            encoding="utf-8",
        )
        (tmp_path / "B.py").write_text(
            "from enum import Enum\n\nclass Includes(Enum):\n    LISTING = 'Listing'\n",
            encoding="utf-8",
        )
        result = audit_sdk.scan_enum_values(tmp_path)
        assert "Includes" in result
        # Both definitions retained, neither clobbered.
        assert sorted(result["Includes"], key=lambda v: v[0]) == [["Listing"], ["Shop"]]


# --------------------------------------------------------------------------- #
# scan_string_concat_issues — list-context detection
# --------------------------------------------------------------------------- #
class TestStringConcatDetector:
    def _write(self, tmp_path, name, code):
        (tmp_path / name).write_text(code, encoding="utf-8")

    def test_missing_comma_in_list_is_flagged(self, tmp_path):
        self._write(tmp_path, "buggy.py", 'nullable = ["a", "b" "c"]\n')
        issues = audit_sdk.scan_string_concat_issues(tmp_path)
        assert len(issues) == 1
        assert issues[0]["file"] == "buggy.py"

    def test_multiline_list_missing_comma_is_flagged(self, tmp_path):
        self._write(
            tmp_path,
            "buggy2.py",
            'mandatory = [\n    "first"\n    "second",\n    "third",\n]\n',
        )
        issues = audit_sdk.scan_string_concat_issues(tmp_path)
        assert len(issues) == 1

    def test_parenthesised_assignment_not_flagged(self, tmp_path):
        self._write(
            tmp_path,
            "intentional.py",
            'MSG = (\n    "long part one "\n    "long part two"\n)\n',
        )
        assert audit_sdk.scan_string_concat_issues(tmp_path) == []

    def test_function_call_args_not_flagged(self, tmp_path):
        self._write(
            tmp_path,
            "warn.py",
            'import warnings\n'
            'def f():\n'
            '    warnings.warn("alpha " "beta", DeprecationWarning)\n',
        )
        assert audit_sdk.scan_string_concat_issues(tmp_path) == []

    def test_proper_list_with_commas_not_flagged(self, tmp_path):
        self._write(tmp_path, "clean.py", 'items = ["a", "b", "c"]\n')
        assert audit_sdk.scan_string_concat_issues(tmp_path) == []

    def test_concat_in_nested_list_inside_call_is_flagged(self, tmp_path):
        self._write(tmp_path, "nested.py", 'foo(["x" "y"])\n')
        issues = audit_sdk.scan_string_concat_issues(tmp_path)
        assert len(issues) == 1

    def test_dunder_files_skipped(self, tmp_path):
        self._write(tmp_path, "__init__.py", 'x = ["a" "b"]\n')
        assert audit_sdk.scan_string_concat_issues(tmp_path) == []


# --------------------------------------------------------------------------- #
# Integration: the shipped ignore file silences exactly the known findings
# --------------------------------------------------------------------------- #
class TestShippedIgnoreFile:
    def test_shipped_ignore_file_is_valid_and_nonempty(self):
        path = SCRIPTS_DIR.parent / "specs" / "audit-ignore.json"
        ignores = audit_sdk.load_ignores(path)
        assert len(ignores) >= 1
        for ig in ignores:
            assert "type" in ig and "key" in ig and "reason" in ig
            if ig["type"] in audit_sdk._VALUED_FINDING_TYPES:
                assert "direction" in ig and "values" in ig

    def test_no_duplicate_match_keys(self):
        # partition_findings applies only the FIRST ignore matching a given
        # (type, key, direction), so a duplicate would silently suppress just
        # part of a finding and then report itself as stale.
        path = SCRIPTS_DIR.parent / "specs" / "audit-ignore.json"
        seen = set()
        for ig in audit_sdk.load_ignores(path):
            match_key = (ig["type"], ig["key"], ig.get("direction"))
            assert match_key not in seen, f"duplicate ignore entry: {match_key}"
            seen.add(match_key)

    def test_no_wildcard_param_drift_ignores(self):
        # "*" on a param_drift entry would hide unreviewed parameter drift on
        # that operation, defeating the self-verifying property.
        path = SCRIPTS_DIR.parent / "specs" / "audit-ignore.json"
        for ig in audit_sdk.load_ignores(path):
            if ig["type"] == "param_drift":
                assert ig["values"] != "*", f"{ig['key']} uses a wildcard"

    def test_shipped_legacy_param_ignores_are_value_scoped(self):
        # The 8 listing-endpoint `legacy` suppressions must name the value
        # explicitly, never "*", so future drift on those operations surfaces.
        path = SCRIPTS_DIR.parent / "specs" / "audit-ignore.json"
        entries = [
            ig
            for ig in audit_sdk.load_ignores(path)
            if ig["type"] == "param_drift"
        ]
        assert len(entries) == 8
        for ig in entries:
            assert ig["direction"] == "extra"
            assert ig["values"] == ["legacy"]
