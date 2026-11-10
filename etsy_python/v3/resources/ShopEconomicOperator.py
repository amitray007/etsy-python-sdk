from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.ShopEconomicOperator import (
    CreateShopEconomicOperatorRequest,
    UpdateShopEconomicOperatorRequest,
)
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method


@dataclass
class ShopEconomicOperatorResource:
    """GPSR manufacturer and EU responsible person records of a shop.

    Etsy has no delete endpoint for economic operators; correct a record with
    ``update_shop_economic_operator`` instead.
    """

    session: EtsyClient

    def create_shop_economic_operator(
        self,
        shop_id: int,
        economic_operator_request: CreateShopEconomicOperatorRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/economic-operators"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=economic_operator_request
        )

    def get_shop_economic_operators(
        self, shop_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/economic-operators"
        return self.session.make_request(endpoint)

    def get_shop_economic_operator(
        self, shop_id: int, economic_operator_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/economic-operators/{economic_operator_id}"
        return self.session.make_request(endpoint)

    def update_shop_economic_operator(
        self,
        shop_id: int,
        economic_operator_id: int,
        economic_operator_request: UpdateShopEconomicOperatorRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/economic-operators/{economic_operator_id}"
        return self.session.make_request(
            endpoint, method=Method.PATCH, payload=economic_operator_request
        )
