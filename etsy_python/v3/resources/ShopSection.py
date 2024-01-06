from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Shop import CreateShopSectionRequest, UpdateShopSectionRequest
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method


@dataclass
class ShopSectionResource:
    session: EtsyClient

    def create_shop_section(
        self, shop_id: int, shop_section_request: CreateShopSectionRequest
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/sections"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=shop_section_request
        )

    def get_shop_sections(self, shop_id: int) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/sections"
        return self.session.make_request(endpoint)

    def delete_shop_section(
        self, shop_id: int, shop_section_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/sections/{shop_section_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def get_shop_section(
        self, shop_id: int, shop_section_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/sections/{shop_section_id}"
        return self.session.make_request(endpoint)

    def update_shop_section(
        self,
        shop_id: int,
        shop_section_id: int,
        shop_section_request: UpdateShopSectionRequest,
    ):
        endpoint = f"/shops/{shop_id}/sections/{shop_section_id}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=shop_section_request
        )
