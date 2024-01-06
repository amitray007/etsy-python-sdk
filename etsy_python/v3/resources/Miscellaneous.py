from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Miscellaneous import GetTokenScopes
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method


@dataclass()
class MiscellaneousResource:
    session: EtsyClient

    def ping(self) -> Union[Response, RequestException]:
        endpoint = "/openapi-ping"
        return self.session.make_request(endpoint)

    def token_scopes(self, token: GetTokenScopes):
        endpoint = "/scopes"
        return self.session.make_request(endpoint, method=Method.POST, payload=token)
