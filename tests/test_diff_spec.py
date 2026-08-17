"""Tests for the security-scheme (OAuth scope) diffing in ``scripts/diff_spec.py``.

Scopes live under ``components.securitySchemes``, outside both ``paths`` and
``components.schemas``. Before this section existed, a spec revision that removed
OAuth scopes produced a report reading "no changes" in every section, which is how
the 2026-08-17 removal of 8 Etsy scopes was mislabeled as cosmetic.
"""

import sys
from pathlib import Path

# scripts/ is not a package; put it on the path so we can import the diff tool.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import diff_spec  # noqa: E402


def make_spec(scopes=None):
    """Minimal spec carrying only an oauth2 authorizationCode scope map."""
    spec = {"paths": {}, "components": {"schemas": {}}}
    if scopes is not None:
        spec["components"]["securitySchemes"] = {
            "oauth2": {
                "type": "oauth2",
                "flows": {"authorizationCode": {"scopes": dict(scopes)}},
            }
        }
    return spec


# --------------------------------------------------------------------------- #
# get_oauth_scopes
# --------------------------------------------------------------------------- #
class TestGetOAuthScopes:
    def test_extracts_scopes(self):
        spec = make_spec({"listings_r": "read listings", "shops_w": "write shops"})
        assert diff_spec.get_oauth_scopes(spec) == {
            "listings_r": "read listings",
            "shops_w": "write shops",
        }

    def test_missing_security_schemes_returns_empty(self):
        assert diff_spec.get_oauth_scopes(make_spec()) == {}

    def test_empty_spec_returns_empty(self):
        assert diff_spec.get_oauth_scopes({}) == {}

    def test_merges_multiple_flows(self):
        spec = {
            "components": {
                "securitySchemes": {
                    "oauth2": {
                        "flows": {
                            "authorizationCode": {"scopes": {"a_r": "a"}},
                            "clientCredentials": {"scopes": {"b_r": "b"}},
                        }
                    }
                }
            }
        }
        assert diff_spec.get_oauth_scopes(spec) == {"a_r": "a", "b_r": "b"}

    def test_malformed_shapes_do_not_raise(self):
        spec = {
            "components": {
                "securitySchemes": {
                    "bad_scheme": "not-a-dict",
                    "no_flows": {"type": "http"},
                    "bad_flows": {"flows": "not-a-dict"},
                    "bad_flow": {"flows": {"authorizationCode": "not-a-dict"}},
                    "bad_scopes": {"flows": {"authorizationCode": {"scopes": []}}},
                    "good": {"flows": {"authorizationCode": {"scopes": {"ok_r": "y"}}}},
                }
            }
        }
        assert diff_spec.get_oauth_scopes(spec) == {"ok_r": "y"}

    def test_non_string_description_coerced_to_empty(self):
        spec = make_spec({"weird_r": None})
        assert diff_spec.get_oauth_scopes(spec) == {"weird_r": ""}


# --------------------------------------------------------------------------- #
# generate_report -- Security Scheme Changes section
# --------------------------------------------------------------------------- #
class TestSecuritySchemeSection:
    def test_section_always_present(self):
        report = diff_spec.generate_report(make_spec({}), make_spec({}))
        assert "## Security Scheme Changes" in report

    def test_no_changes_reported_when_identical(self):
        scopes = {"listings_r": "read listings"}
        report = diff_spec.generate_report(make_spec(scopes), make_spec(scopes))
        assert "No security scheme changes." in report

    def test_removed_scope_reported(self):
        report = diff_spec.generate_report(
            make_spec({"listings_r": "read listings", "cart_r": "read shopping carts"}),
            make_spec({"listings_r": "read listings"}),
        )
        assert "### Removed OAuth Scopes" in report
        assert "**cart_r**: read shopping carts" in report
        assert "No security scheme changes." not in report

    def test_added_scope_reported(self):
        report = diff_spec.generate_report(
            make_spec({"listings_r": "read listings"}),
            make_spec({"listings_r": "read listings", "new_r": "brand new"}),
        )
        assert "### New OAuth Scopes" in report
        assert "**new_r**: brand new" in report

    def test_changed_description_reported(self):
        report = diff_spec.generate_report(
            make_spec({"listings_r": "old text"}),
            make_spec({"listings_r": "new text"}),
        )
        assert "### Changed OAuth Scope Descriptions" in report
        assert "`old text` -> `new text`" in report

    def test_regression_scope_removal_is_not_silent(self):
        """The exact 2026-08-17 case: only scopes changed, nothing else."""
        removed = {
            "billing_r": "see all billing statement data",
            "cart_r": "read shopping carts",
            "cart_w": "add/remove from shopping carts",
            "favorites_r": "see private favorites",
            "favorites_w": "add/remove favorites",
            "feedback_r": "see purchase info in feedback",
            "recommend_r": "see recommended listings",
            "recommend_w": "accept/reject recommended listings",
        }
        kept = {"listings_r": "read listings"}
        report = diff_spec.generate_report(
            make_spec({**kept, **removed}), make_spec(kept)
        )

        # Every other section correctly reports nothing...
        assert "No new endpoints." in report
        assert "No removed endpoints." in report
        assert "No changed endpoints." in report
        assert "No schema changes." in report
        assert "No new deprecations." in report

        # ...so this section is the only thing standing between a real change
        # and a report that reads as entirely cosmetic.
        assert "No security scheme changes." not in report
        for name in removed:
            assert f"**{name}**" in report
