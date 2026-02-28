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
