from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient


@dataclass
class UserResource:
    session: EtsyClient

    def get_user(self, user_id: int) -> Union[Response, RequestException]:
        endpoint = f"/users/{user_id}"
        return self.session.make_request(endpoint)

    def get_me(self) -> Union[Response, RequestException]:
        endpoint = "/users/me"
        return self.session.make_request(endpoint)
