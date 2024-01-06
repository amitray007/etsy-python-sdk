from dataclasses import dataclass
from typing import Union, Dict, Any

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Shop import UpdateShopRequest
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method


@dataclass
class ShopResource:
    session: EtsyClient

    def get_shop(self, shop_id: int) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}"
        return self.session.make_request(endpoint)

    def update_shop(
        self, shop_id: int, shop_request: UpdateShopRequest
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=shop_request
        )

    def get_shop_by_owner_user_id(
        self, user_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/users/{user_id}/shops"
        return self.session.make_request(endpoint)

    def find_shops(
        self, shop_name: str, limit: int = 25, offset: int = 0
    ) -> Union[Response, RequestException]:
        endpoint = "/shops"
        kwargs: Dict[str, Any] = {
            "shop_name": shop_name,
            "limit": limit,
            "offset": offset,
        }
        return self.session.make_request(endpoint, **kwargs)
