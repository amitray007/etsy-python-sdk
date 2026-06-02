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
        findings = audit_sdk.compute_enum_findings(spec, {"Color": ["red", "green"]})
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
            spec, {"Color": ["red", "green", "purple"]}
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
        assert audit_sdk.compute_enum_findings(spec, {"Color": ["red", "green"]}) == []


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
            if ig["type"] == "enum_staleness":
                assert "direction" in ig and "values" in ig
