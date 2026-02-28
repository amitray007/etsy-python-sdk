from unittest.mock import MagicMock

from etsy_python.v3.models.Shop import UpdateShopRequest
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Shop import ShopResource
from etsy_python.v3.resources.enums.Request import Method

from tests.conftest import MOCK_SHOP_ID, MOCK_USER_ID
from tests.fixtures.responses import make_collection, make_shop


class TestGetShop:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop())
        resource = ShopResource(session=mock_session)

        result = resource.get_shop(MOCK_SHOP_ID)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}"
        )


class TestUpdateShop:
    def test_calls_put_with_payload(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop())
        resource = ShopResource(session=mock_session)
        payload = MagicMock(spec=UpdateShopRequest)

        result = resource.update_shop(MOCK_SHOP_ID, payload)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}", method=Method.PUT, payload=payload
        )


class TestGetShopByOwnerUserId:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop())
        resource = ShopResource(session=mock_session)

        result = resource.get_shop_by_owner_user_id(int(MOCK_USER_ID))

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/users/{MOCK_USER_ID}/shops"
        )


class TestFindShops:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_shop)
        )
        resource = ShopResource(session=mock_session)

        result = resource.find_shops("TestShop")

        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == "/shops"
        assert call_args[1]["shop_name"] == "TestShop"

    def test_custom_pagination(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_shop)
        )
        resource = ShopResource(session=mock_session)

        resource.find_shops("TestShop", limit=10, offset=5)

        call_kwargs = mock_session.make_request.call_args[1]
        assert call_kwargs["limit"] == 10
        assert call_kwargs["offset"] == 5
