from dataclasses import dataclass
from typing import Union, Dict, Any

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.ProcessingProfile import (
    CreateShopReadinessStateDefinitionRequest,
    UpdateShopReadinessStateDefinitionRequest,
)
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method


@dataclass
class ProcessingProfileResource:
    session: EtsyClient

    def create_shop_readiness_state_definition(
        self,
        shop_id: int,
        readiness_state_definition: CreateShopReadinessStateDefinitionRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/readiness-state-definitions"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=readiness_state_definition
        )

    def get_shop_readiness_state_definitions(
        self, shop_id: int, limit: int = 25, offset: int = 0
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/readiness-state-definitions"
        query_params: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self.session.make_request(endpoint, query_params=query_params)

    def get_shop_readiness_state_definition(
        self, shop_id: int, readiness_state_definition_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/readiness-state-definitions/{readiness_state_definition_id}"
        return self.session.make_request(endpoint)

    def update_shop_readiness_state_definition(
        self,
        shop_id: int,
        readiness_state_definition_id: int,
        readiness_state_definition: UpdateShopReadinessStateDefinitionRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/readiness-state-definitions/{readiness_state_definition_id}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=readiness_state_definition
        )

    def delete_shop_readiness_state_definition(
        self, shop_id: int, readiness_state_definition_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/readiness-state-definitions/{readiness_state_definition_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)
