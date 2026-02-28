from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from etsy_python.v3.common.Env import environment
from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.FileRequest import FileRequest
from etsy_python.v3.models.Request import Request
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.RateLimit import RateLimit
from etsy_python.v3.resources.enums.Request import Method

from tests.conftest import MOCK_ACCESS_TOKEN, MOCK_KEYSTRING, MOCK_REFRESH_TOKEN


def _make_mock_response(status_code=200, json_data=None, headers=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.json.return_value = json_data or {}
    return resp


class TestInit:
    def test_user_id_extracted(self, real_etsy_client):
        assert real_etsy_client.user_id == "12345678"

    def test_keystring_stored(self, real_etsy_client):
        assert real_etsy_client.keystring == MOCK_KEYSTRING

    def test_access_token_stored(self, real_etsy_client):
        assert real_etsy_client.access_token == MOCK_ACCESS_TOKEN

    def test_refresh_token_stored(self, real_etsy_client):
        assert real_etsy_client.refresh_token == MOCK_REFRESH_TOKEN


class TestEnsureUtc:
    def test_naive_datetime_gets_utc(self):
        naive = datetime(2025, 1, 1, 12, 0, 0)
        result = EtsyClient.ensure_utc(naive)
        assert result.tzinfo == timezone.utc

    def test_utc_datetime_unchanged(self):
        utc = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = EtsyClient.ensure_utc(utc)
        assert result == utc

    def test_non_utc_timezone_converted(self):
        est = timezone(timedelta(hours=-5))
        est_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=est)
        result = EtsyClient.ensure_utc(est_time)
        assert result.tzinfo == timezone.utc
        assert result.hour == 17  # 12 EST = 17 UTC


class TestMakeRequestGet:
    def test_get_request(self, real_etsy_client):
        mock_resp = _make_mock_response(200, {"shop_id": 123})
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        result = real_etsy_client.make_request("/shops/123")
        assert isinstance(result, Response)
        assert result.code == 200
        assert result.message == {"shop_id": 123}

        called_url = real_etsy_client._mock_http_session.get.call_args[0][0]
        assert called_url == f"{environment.request_url}/shops/123"

    def test_get_with_kwargs(self, real_etsy_client):
        mock_resp = _make_mock_response(200, {"results": []})
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        real_etsy_client.make_request("/shops/123/listings", limit=25, offset=0)

        called_url = real_etsy_client._mock_http_session.get.call_args[0][0]
        assert "limit=25" in called_url
        assert "offset=0" in called_url


class TestMakeRequestPost:
    def test_post_json_request(self, real_etsy_client):
        mock_resp = _make_mock_response(201, {"listing_id": 456})
        real_etsy_client._mock_http_session.post.return_value = mock_resp

        payload = MagicMock(spec=Request)
        payload.get_dict.return_value = {"title": "Test Listing"}

        result = real_etsy_client.make_request(
            "/shops/123/listings", method=Method.POST, payload=payload
        )
        assert isinstance(result, Response)
        assert result.code == 201

        real_etsy_client._mock_http_session.post.assert_called_once()
        call_kwargs = real_etsy_client._mock_http_session.post.call_args
        assert call_kwargs[1]["json"] == {"title": "Test Listing"}

    def test_post_file_request(self, real_etsy_client):
        mock_resp = _make_mock_response(201, {"listing_image_id": 789})
        real_etsy_client._mock_http_session.post.return_value = mock_resp

        payload = MagicMock(spec=FileRequest)
        payload.file = {"image": b"fake-image-data"}
        payload.data = {"rank": 1}

        result = real_etsy_client.make_request(
            "/shops/123/listings/456/images", method=Method.POST, payload=payload
        )
        assert isinstance(result, Response)
        assert result.code == 201

        call_kwargs = real_etsy_client._mock_http_session.post.call_args
        assert call_kwargs[1]["files"] == {"image": b"fake-image-data"}
        assert call_kwargs[1]["data"] == {"rank": 1}


class TestMakeRequestPut:
    def test_put_request(self, real_etsy_client):
        mock_resp = _make_mock_response(200, {"shop_id": 123})
        real_etsy_client._mock_http_session.put.return_value = mock_resp

        payload = MagicMock(spec=Request)
        payload.get_dict.return_value = {"title": "Updated Shop"}

        result = real_etsy_client.make_request(
            "/shops/123", method=Method.PUT, payload=payload
        )
        assert isinstance(result, Response)
        assert result.code == 200

        call_kwargs = real_etsy_client._mock_http_session.put.call_args
        assert call_kwargs[1]["json"] == {"title": "Updated Shop"}


class TestMakeRequestPatch:
    def test_patch_request(self, real_etsy_client):
        mock_resp = _make_mock_response(200, {"listing_id": 456})
        real_etsy_client._mock_http_session.patch.return_value = mock_resp

        payload = MagicMock(spec=Request)
        payload.get_dict.return_value = {"title": "Patched Listing"}

        result = real_etsy_client.make_request(
            "/shops/123/listings/456", method=Method.PATCH, payload=payload
        )
        assert isinstance(result, Response)
        assert result.code == 200

        call_kwargs = real_etsy_client._mock_http_session.patch.call_args
        assert call_kwargs[1]["json"] == {"title": "Patched Listing"}


class TestMakeRequestDelete:
    def test_delete_request(self, real_etsy_client):
        mock_resp = _make_mock_response(204, None)
        real_etsy_client._mock_http_session.delete.return_value = mock_resp

        result = real_etsy_client.make_request("/listings/456", method=Method.DELETE)
        assert isinstance(result, Response)
        assert result.code == 204
        assert result.message == "OK"


class TestMakeRequestErrors:
    @pytest.mark.parametrize("status_code", [400, 401, 403, 404, 409, 500, 503])
    def test_error_codes_raise_request_exception(self, real_etsy_client, status_code):
        mock_resp = _make_mock_response(
            status_code, {"error": "Something went wrong"}
        )
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        with pytest.raises(RequestException) as exc_info:
            real_etsy_client.make_request("/shops/123")
        assert exc_info.value.code == status_code

    def test_error_with_description(self, real_etsy_client):
        mock_resp = _make_mock_response(
            400,
            {"error": "Bad Request", "error_description": "Missing required field"},
        )
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        with pytest.raises(RequestException) as exc_info:
            real_etsy_client.make_request("/shops/123")
        assert exc_info.value.error == "Bad Request"
        assert exc_info.value.error_description == "Missing required field"

    def test_post_without_payload_raises_value_error(self, real_etsy_client):
        with pytest.raises(ValueError, match="Improper payload"):
            real_etsy_client.make_request("/shops/123/listings", method=Method.POST)

    def test_put_without_payload_raises_value_error(self, real_etsy_client):
        with pytest.raises(ValueError, match="Improper payload"):
            real_etsy_client.make_request("/shops/123", method=Method.PUT)

    def test_patch_without_payload_raises_value_error(self, real_etsy_client):
        with pytest.raises(ValueError, match="Improper payload"):
            real_etsy_client.make_request(
                "/shops/123/listings/456", method=Method.PATCH
            )


class TestRateLimits:
    def test_rate_limits_extracted(self, real_etsy_client):
        headers = {
            "X-Limit-Per-Day": "10000",
            "X-Remaining-This-Second": "5",
            "X-Remaining-Today": "9500",
        }
        mock_resp = _make_mock_response(200, {"shop_id": 123}, headers)
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        result = real_etsy_client.make_request("/shops/123")
        assert result.rate_limits is not None
        assert isinstance(result.rate_limits, RateLimit)
        assert result.rate_limits.limit_per_day == "10000"
        assert result.rate_limits.remaining_this_second == "5"
        assert result.rate_limits.remaining_today == "9500"

    def test_no_rate_limit_headers(self, real_etsy_client):
        mock_resp = _make_mock_response(200, {"shop_id": 123})
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        result = real_etsy_client.make_request("/shops/123")
        assert result.rate_limits is None

    def test_rate_limits_on_error(self, real_etsy_client):
        headers = {
            "X-Limit-Per-Day": "10000",
            "X-Remaining-This-Second": "0",
            "X-Remaining-Today": "0",
        }
        mock_resp = _make_mock_response(
            403, {"error": "Rate limited"}, headers
        )
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        with pytest.raises(RequestException) as exc_info:
            real_etsy_client.make_request("/shops/123")
        assert exc_info.value.rate_limits is not None


class TestTokenRefresh:
    def test_expired_token_triggers_refresh(self, real_etsy_client):
        real_etsy_client.expiry = datetime.now(tz=timezone.utc) - timedelta(hours=1)

        refresh_resp = _make_mock_response(
            200,
            {
                "access_token": "new-access-token",
                "refresh_token": "new-refresh-token",
                "expires_in": 3600,
            },
        )
        real_etsy_client._mock_http_session.post.return_value = refresh_resp

        get_resp = _make_mock_response(200, {"shop_id": 123})
        real_etsy_client._mock_http_session.get.return_value = get_resp

        result = real_etsy_client.make_request("/shops/123")
        assert isinstance(result, Response)
        assert real_etsy_client.access_token == "new-access-token"
        assert real_etsy_client.refresh_token == "new-refresh-token"

    def test_sync_refresh_callback_called(self):
        sync_callback = MagicMock()

        with patch("etsy_python.v3.resources.Session.Session") as mock_cls:
            mock_http = MagicMock()
            mock_cls.return_value = mock_http
            mock_http.headers = {}

            client = EtsyClient(
                keystring=MOCK_KEYSTRING,
                access_token=MOCK_ACCESS_TOKEN,
                refresh_token=MOCK_REFRESH_TOKEN,
                expiry=datetime.now(tz=timezone.utc) - timedelta(hours=1),
                sync_refresh=sync_callback,
            )

            refresh_resp = _make_mock_response(
                200,
                {
                    "access_token": "new-token",
                    "refresh_token": "new-refresh",
                    "expires_in": 3600,
                },
            )
            mock_http.post.return_value = refresh_resp

            get_resp = _make_mock_response(200, {"ok": True})
            mock_http.get.return_value = get_resp

            client.make_request("/test")
            sync_callback.assert_called_once()
            args = sync_callback.call_args[0]
            assert args[0] == "new-token"
            assert args[1] == "new-refresh"

    def test_refresh_failure_raises(self, real_etsy_client):
        real_etsy_client.expiry = datetime.now(tz=timezone.utc) - timedelta(hours=1)

        refresh_resp = _make_mock_response(
            200,
            {"error": "invalid_grant"},
        )
        real_etsy_client._mock_http_session.post.return_value = refresh_resp

        with pytest.raises(RequestException) as exc_info:
            real_etsy_client.make_request("/shops/123")
        assert exc_info.value.code == 401


class TestNoContentResponse:
    def test_204_returns_ok_message(self, real_etsy_client):
        mock_resp = _make_mock_response(204)
        real_etsy_client._mock_http_session.delete.return_value = mock_resp

        result = real_etsy_client.make_request("/listings/123", method=Method.DELETE)
        assert result.code == 204
        assert result.message == "OK"
