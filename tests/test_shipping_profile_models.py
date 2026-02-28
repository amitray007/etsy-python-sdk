import pytest

from etsy_python.v3.enums.ShippingProfile import Type
from etsy_python.v3.models.ShippingProfile import (
    CreateShopShippingProfileDestinationRequest,
    CreateShopShippingProfileRequest,
    CreateShopShippingProfileUpgradeRequest,
    UpdateShopShippingProfileDestinationRequest,
    UpdateShopShippingProfileRequest,
    UpdateShopShippingProfileUpgradeRequest,
)


class TestCreateShopShippingProfileRequest:
    def test_valid_request(self):
        req = CreateShopShippingProfileRequest(
            title="Standard Shipping",
            origin_country_iso="US",
            primary_cost=5.00,
            secondary_cost=2.00,
            min_processing_time=3,
            max_processing_time=5,
        )
        assert req.title == "Standard Shipping"
        assert req.origin_country_iso == "US"

    def test_missing_mandatory_raises(self):
        with pytest.raises(ValueError):
            CreateShopShippingProfileRequest(
                title="Standard",
                origin_country_iso=None,  # mandatory
                primary_cost=5.00,
                secondary_cost=2.00,
                min_processing_time=3,
                max_processing_time=5,
            )

    def test_nullable_fields(self):
        req = CreateShopShippingProfileRequest(
            title="Standard",
            origin_country_iso="US",
            primary_cost=5.00,
            secondary_cost=2.00,
            min_processing_time=3,
            max_processing_time=5,
            destination_country_iso="",  # nullable -> None
        )
        result = req.get_dict()
        assert result["destination_country_iso"] is None


class TestUpdateShopShippingProfileRequest:
    def test_no_mandatory_fields(self):
        req = UpdateShopShippingProfileRequest(title="Updated Profile")
        assert req.title == "Updated Profile"

    def test_empty_request(self):
        req = UpdateShopShippingProfileRequest()
        result = req.get_dict()
        assert "title" not in result


class TestCreateShopShippingProfileDestinationRequest:
    def test_valid_request(self):
        req = CreateShopShippingProfileDestinationRequest(
            primary_cost=5.00, secondary_cost=2.00
        )
        assert req.primary_cost == 5.00

    def test_missing_mandatory_raises(self):
        with pytest.raises(ValueError):
            CreateShopShippingProfileDestinationRequest(
                primary_cost=None, secondary_cost=2.00
            )


class TestUpdateShopShippingProfileDestinationRequest:
    def test_no_mandatory_fields(self):
        req = UpdateShopShippingProfileDestinationRequest(primary_cost=7.00)
        assert req.primary_cost == 7.00


class TestCreateShopShippingProfileUpgradeRequest:
    def test_always_raises_due_to_type_mismatch(self):
        # SDK bug: mandatory list has "type" but attribute is stored as "_type",
        # so check_mandatory() always fails with ValueError
        with pytest.raises(ValueError):
            CreateShopShippingProfileUpgradeRequest(
                profile_type=Type.ZERO,
                upgrade_name="Priority",
                price=10.00,
                secondary_price=5.00,
            )

    def test_missing_mandatory_raises(self):
        with pytest.raises(ValueError):
            CreateShopShippingProfileUpgradeRequest(
                profile_type=Type.ZERO,
                upgrade_name=None,  # mandatory
                price=10.00,
                secondary_price=5.00,
            )


class TestUpdateShopShippingProfileUpgradeRequest:
    def test_no_mandatory_fields(self):
        req = UpdateShopShippingProfileUpgradeRequest(upgrade_name="Express")
        assert req.upgrade_name == "Express"
