import pytest

from etsy_python.v3.models.ShopReturnPolicy import (
    ConsolidateShopReturnPoliciesRequest,
    CreateShopReturnPolicyRequest,
    UpdateShopReturnPolicyRequest,
)


class TestConsolidateShopReturnPoliciesRequest:
    def test_stores_required_ids(self):
        req = ConsolidateShopReturnPoliciesRequest(
            source_return_policy_id=111, destination_return_policy_id=222
        )
        assert req.source_return_policy_id == 111
        assert req.destination_return_policy_id == 222


class TestCreateShopReturnPolicyRequest:
    def test_stores_required_fields(self):
        req = CreateShopReturnPolicyRequest(
            accepts_returns=True, accepts_exchanges=False, return_deadline=30
        )
        assert req.accepts_returns is True
        assert req.accepts_exchanges is False
        assert req.return_deadline == 30

    def test_return_deadline_optional(self):
        req = CreateShopReturnPolicyRequest(
            accepts_returns=True, accepts_exchanges=True
        )
        assert req.return_deadline is None

    def test_bool_false_preserved_not_nulled(self):
        # Booleans must serialize even when False — guard against the
        # nullable/None coercion described in CLAUDE.md.
        req = CreateShopReturnPolicyRequest(
            accepts_returns=False, accepts_exchanges=False
        )
        result = req.get_dict()
        assert result["accepts_returns"] is False
        assert result["accepts_exchanges"] is False


class TestUpdateShopReturnPolicyRequest:
    def test_stores_required_fields(self):
        req = UpdateShopReturnPolicyRequest(
            accepts_returns=True, accepts_exchanges=True, return_deadline=14
        )
        assert req.accepts_returns is True
        assert req.accepts_exchanges is True
        assert req.return_deadline == 14

    def test_return_deadline_optional(self):
        req = UpdateShopReturnPolicyRequest(
            accepts_returns=False, accepts_exchanges=True
        )
        assert req.return_deadline is None
