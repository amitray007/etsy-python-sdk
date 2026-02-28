from unittest.mock import MagicMock

from etsy_python.v3.models.ShippingProfile import (
    CreateShopShippingProfileDestinationRequest,
    CreateShopShippingProfileRequest,
    CreateShopShippingProfileUpgradeRequest,
    UpdateShopShippingProfileDestinationRequest,
    UpdateShopShippingProfileRequest,
    UpdateShopShippingProfileUpgradeRequest,
)
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.ShippingProfile import ShippingProfileResource
from etsy_python.v3.resources.enums.Request import Method

from tests.conftest import (
    MOCK_SHIPPING_PROFILE_DESTINATION_ID,
    MOCK_SHIPPING_PROFILE_ID,
    MOCK_SHIPPING_PROFILE_UPGRADE_ID,
    MOCK_SHOP_ID,
)
from tests.fixtures.responses import (
    make_collection,
    make_shipping_carrier,
    make_shipping_profile,
    make_shipping_profile_destination,
    make_shipping_profile_upgrade,
)

SP = MOCK_SHIPPING_PROFILE_ID
SPD = MOCK_SHIPPING_PROFILE_DESTINATION_ID
SPU = MOCK_SHIPPING_PROFILE_UPGRADE_ID


class TestGetShippingCarriers:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_shipping_carrier)
        )
        resource = ShippingProfileResource(session=mock_session)

        result = resource.get_shipping_carriers("US")

        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == "/shipping-carriers"
        assert call_args[1]["origin_country_iso"] == "US"


class TestCreateShopShippingProfile:
    def test_calls_post(self, mock_session):
        mock_session.make_request.return_value = Response(
            201, make_shipping_profile()
        )
        resource = ShippingProfileResource(session=mock_session)
        payload = MagicMock(spec=CreateShopShippingProfileRequest)

        result = resource.create_shop_shipping_profile(MOCK_SHOP_ID, payload)

        assert result.code == 201
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles",
            method=Method.POST,
            payload=payload,
        )


class TestGetShopShippingProfiles:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_shipping_profile)
        )
        resource = ShippingProfileResource(session=mock_session)

        result = resource.get_shop_shipping_profiles(MOCK_SHOP_ID)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles"
        )


class TestDeleteShopShippingProfile:
    def test_calls_delete(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = ShippingProfileResource(session=mock_session)

        result = resource.delete_shop_shipping_profile(MOCK_SHOP_ID, SP)

        assert result.code == 204
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}",
            method=Method.DELETE,
        )


class TestGetShopShippingProfile:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shipping_profile()
        )
        resource = ShippingProfileResource(session=mock_session)

        result = resource.get_shop_shipping_profile(MOCK_SHOP_ID, SP)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}"
        )


class TestUpdateShopShippingProfile:
    def test_calls_put(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shipping_profile()
        )
        resource = ShippingProfileResource(session=mock_session)
        payload = MagicMock(spec=UpdateShopShippingProfileRequest)

        result = resource.update_shop_shipping_profile(MOCK_SHOP_ID, SP, payload)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}",
            method=Method.PUT,
            payload=payload,
        )


class TestCreateShopShippingProfileDestination:
    def test_calls_post(self, mock_session):
        mock_session.make_request.return_value = Response(
            201, make_shipping_profile_destination()
        )
        resource = ShippingProfileResource(session=mock_session)
        payload = MagicMock(spec=CreateShopShippingProfileDestinationRequest)

        result = resource.create_shop_shipping_profile_destination(
            MOCK_SHOP_ID, SP, payload
        )

        assert result.code == 201
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}/destinations",
            method=Method.POST,
            payload=payload,
        )


class TestGetShopShippingProfileDestinations:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_shipping_profile_destination)
        )
        resource = ShippingProfileResource(session=mock_session)

        result = resource.get_shop_shipping_profile_destination_by_shipping_profile(
            MOCK_SHOP_ID, SP
        )

        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert (
            call_args[0][0]
            == f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}/destinations"
        )
        assert call_args[1]["limit"] == 25
        assert call_args[1]["offset"] == 0


class TestDeleteShopShippingProfileDestination:
    def test_calls_delete(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = ShippingProfileResource(session=mock_session)

        result = resource.delete_shop_shipping_profile_destination(
            MOCK_SHOP_ID, SP, SPD
        )

        assert result.code == 204
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}/destinations/{SPD}",
            method=Method.DELETE,
        )


class TestUpdateShopShippingProfileDestination:
    def test_calls_put(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shipping_profile_destination()
        )
        resource = ShippingProfileResource(session=mock_session)
        payload = MagicMock(spec=UpdateShopShippingProfileDestinationRequest)

        result = resource.update_shop_shipping_profile_destination(
            MOCK_SHOP_ID, SP, SPD, payload
        )

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}/destinations/{SPD}",
            method=Method.PUT,
            payload=payload,
        )


class TestCreateShopShippingProfileUpgrade:
    def test_calls_post(self, mock_session):
        mock_session.make_request.return_value = Response(
            201, make_shipping_profile_upgrade()
        )
        resource = ShippingProfileResource(session=mock_session)
        payload = MagicMock(spec=CreateShopShippingProfileUpgradeRequest)

        result = resource.create_shop_shipping_profile_upgrade(
            MOCK_SHOP_ID, SP, payload
        )

        assert result.code == 201
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}/upgrades",
            method=Method.POST,
            payload=payload,
        )


class TestGetShopShippingProfileUpgrades:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_shipping_profile_upgrade)
        )
        resource = ShippingProfileResource(session=mock_session)

        result = resource.get_shop_shipping_profile_upgrades(MOCK_SHOP_ID, SP)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}/upgrades"
        )


class TestDeleteShopShippingProfileUpgrade:
    def test_calls_delete(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = ShippingProfileResource(session=mock_session)

        result = resource.delete_shop_shipping_profile_upgrade(
            MOCK_SHOP_ID, SP, SPU
        )

        assert result.code == 204
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}/upgrades/{SPU}",
            method=Method.DELETE,
        )


class TestUpdateShopShippingProfileUpgrade:
    def test_calls_put(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shipping_profile_upgrade()
        )
        resource = ShippingProfileResource(session=mock_session)
        payload = MagicMock(spec=UpdateShopShippingProfileUpgradeRequest)

        result = resource.update_shop_shipping_profile_upgrade(
            MOCK_SHOP_ID, SP, SPU, payload
        )

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/shipping-profiles/{SP}/upgrades/{SPU}",
            method=Method.PUT,
            payload=payload,
        )
