from dataclasses import dataclass
from typing import Union, Dict, Any

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method


@dataclass
class UserAddressResource:
    session: EtsyClient

    def delete_user_address(
        self, user_address_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/user/addresses/{user_address_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def get_user_address(
        self, user_address_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/user/addresses/{user_address_id}"
        return self.session.make_request(endpoint)

    def get_user_addresses(
        self, limit: int = 25, offset: int = 0
    ) -> Union[Response, RequestException]:
        endpoint = "/user/addresses"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self.session.make_request(endpoint, **kwargs)
