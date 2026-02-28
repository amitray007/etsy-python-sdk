from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.User import UserResource

from tests.conftest import MOCK_USER_ID
from tests.fixtures.responses import make_user


class TestGetUser:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_user())
        resource = UserResource(session=mock_session)

        result = resource.get_user(int(MOCK_USER_ID))

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/users/{MOCK_USER_ID}"
        )


class TestGetMe:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_user())
        resource = UserResource(session=mock_session)

        result = resource.get_me()

        assert result.code == 200
        mock_session.make_request.assert_called_once_with("/users/me")
