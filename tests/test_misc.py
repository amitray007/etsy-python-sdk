import pytest

from etsy_python.v3.resources.Miscellaneous import MiscellaneousResource
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestMiscellaneous:
    def test_ping(self, etsy_client):
        resource = MiscellaneousResource(session=etsy_client)
        response = resource.ping()
        assert isinstance(response, Response)
        assert response.code == 200

    def test_token_scopes(self, etsy_client, api_key):
        from etsy_python.v3.models.Miscellaneous import GetTokenScopes

        resource = MiscellaneousResource(session=etsy_client)
        scopes_request = GetTokenScopes(token=etsy_client.access_token)
        response = resource.token_scopes(scopes_request)
        assert isinstance(response, Response)
        assert response.code == 200
