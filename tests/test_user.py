import pytest

from etsy_python.v3.resources.User import UserResource
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestUser:
    def test_get_me(self, etsy_client):
        resource = UserResource(session=etsy_client)
        response = resource.get_me()
        assert isinstance(response, Response)
        assert response.code == 200
        assert "user_id" in response.message

    def test_get_user(self, etsy_client):
        resource = UserResource(session=etsy_client)
        user_id = int(etsy_client.user_id)
        response = resource.get_user(user_id)
        assert isinstance(response, Response)
        assert response.code == 200
