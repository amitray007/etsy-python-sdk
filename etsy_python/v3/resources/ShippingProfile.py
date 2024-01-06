from dataclasses import dataclass
from typing import Union, Dict, Any

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.ShippingProfile import (
    CreateShopShippingProfileDestinationRequest,
    CreateShopShippingProfileRequest,
    CreateShopShippingProfileUpgradeRequest,
    UpdateShopShippingProfileDestinationRequest,
    UpdateShopShippingProfileRequest,
    UpdateShopShippingProfileUpgradeRequest,
)
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method


@dataclass
class ShippingProfileResource:
    session: EtsyClient

    def get_shipping_carriers(
        self, origin_country_iso: str
    ) -> Union[Response, RequestException]:
        endpoint = "/shipping-carriers"
        kwargs: Dict[str, Any] = {"origin_country_iso": origin_country_iso}
        return self.session.make_request(endpoint, **kwargs)

    def create_shop_shipping_profile(
        self, shop_id: int, shipping_profile: CreateShopShippingProfileRequest
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=shipping_profile
        )

    def get_shop_shipping_profiles(
        self, shop_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles"
        return self.session.make_request(endpoint)

    def delete_shop_shipping_profile(
        self, shop_id: int, shipping_profile_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def get_shop_shipping_profile(
        self, shop_id: int, shipping_profile_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}"
        return self.session.make_request(endpoint)

    def update_shop_shipping_profile(
        self,
        shop_id: int,
        shipping_profile_id: int,
        shipping_profile: UpdateShopShippingProfileRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=shipping_profile
        )

    def create_shop_shipping_profile_destination(
        self,
        shop_id: int,
        shipping_profile_id: int,
        shipping_profile_destination: CreateShopShippingProfileDestinationRequest,
    ) -> Union[Response, RequestException]:
        endpoint = (
            f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/destinations"
        )
        return self.session.make_request(
            endpoint, method=Method.POST, payload=shipping_profile_destination
        )

    def get_shop_shipping_profile_destination_by_shipping_profile(
        self, shop_id: int, shipping_profile_id: int, limit: int = 25, offset: int = 0
    ) -> Union[Response, RequestException]:
        endpoint = (
            f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/destinations"
        )
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self.session.make_request(endpoint, **kwargs)

    def delete_shop_shipping_profile_destination(
        self,
        shop_id: int,
        shipping_profile_id: int,
        shipping_profile_destination_id: int,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/destinations/{shipping_profile_destination_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def update_shop_shipping_profile_destination(
        self,
        shop_id: int,
        shipping_profile_id: int,
        shipping_profile_destination_id: int,
        shipping_profile_destination: UpdateShopShippingProfileDestinationRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/destinations/{shipping_profile_destination_id}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=shipping_profile_destination
        )

    def create_shop_shipping_profile_upgrade(
        self,
        shop_id: int,
        shipping_profile_id: int,
        shipping_profile_upgrade: CreateShopShippingProfileUpgradeRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/upgrades"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=shipping_profile_upgrade
        )

    def get_shop_shipping_profile_upgrades(
        self, shop_id: int, shipping_profile_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/upgrades"
        return self.session.make_request(endpoint)

    def delete_shop_shipping_profile_upgrade(
        self,
        shop_id: int,
        shipping_profile_id: int,
        upgrade_id: int,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/upgrades/{upgrade_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def update_shop_shipping_profile_upgrade(
        self,
        shop_id: int,
        shipping_profile_id: int,
        upgrade_id: int,
        shipping_profile_upgrade: UpdateShopShippingProfileUpgradeRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shipping-profiles/{shipping_profile_id}/upgrades/{upgrade_id}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=shipping_profile_upgrade
        )
