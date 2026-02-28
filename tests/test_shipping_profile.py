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
