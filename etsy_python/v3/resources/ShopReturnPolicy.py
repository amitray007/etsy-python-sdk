from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.ShopReturnPolicy import (
    ConsolidateShopReturnPoliciesRequest,
    CreateShopReturnPolicyRequest,
    UpdateShopReturnPolicyRequest,
)
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method


@dataclass
class ShopReturnPolicyResource:
    session: EtsyClient

    def consolidate_shop_return_policies(
        self, shop_id: int, shop_return_request: ConsolidateShopReturnPoliciesRequest
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/policies/return/consolidate"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=shop_return_request
        )

    def create_shop_return_policy(
        self, shop_id: int, shop_return_request: CreateShopReturnPolicyRequest
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/policies/return"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=shop_return_request
        )

    def get_shop_return_policies(
        self, shop_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/policies/return"
        return self.session.make_request(endpoint)

    def delete_shop_return_policy(
        self, shop_id: int, return_policy_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/policies/return/{return_policy_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def get_shop_return_policy(
        self, shop_id: int, return_policy_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/policies/return/{return_policy_id}"
        return self.session.make_request(endpoint)

    def update_shop_return_policy(
        self,
        shop_id: int,
        return_policy_id: int,
        shop_return_request: UpdateShopReturnPolicyRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/policies/return/{return_policy_id}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=shop_return_request
        )
