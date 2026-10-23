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

    def test_get_with_query_params(self, real_etsy_client):
        mock_resp = _make_mock_response(200, {"results": []})
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        real_etsy_client.make_request(
            "/shops/123/listings", query_params={"limit": 25, "offset": 0}
        )

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
    @pytest.mark.parametrize(
        "status_code", [400, 401, 402, 403, 404, 405, 409, 422, 429, 500, 502, 503, 504]
    )
    def test_error_codes_raise_request_exception(self, real_etsy_client, status_code):
        mock_resp = _make_mock_response(
            status_code, {"error": "Something went wrong"}
        )
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        with pytest.raises(RequestException) as exc_info:
            real_etsy_client.make_request("/shops/123")
        assert exc_info.value.code == status_code

    @pytest.mark.parametrize("status_code", [200, 201, 302, 399])
    def test_non_error_codes_return_response(self, real_etsy_client, status_code):
        mock_resp = _make_mock_response(status_code, {"ok": True})
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        result = real_etsy_client.make_request("/shops/123")
        assert isinstance(result, Response)
        assert result.code == status_code

    def test_non_json_error_body_raises_request_exception(self, real_etsy_client):
        mock_resp = _make_mock_response(405)
        mock_resp.json.side_effect = ValueError("not JSON")
        mock_resp.text = "<html>Method Not Allowed</html>"
        real_etsy_client._mock_http_session.delete.return_value = mock_resp

        with pytest.raises(RequestException) as exc_info:
            real_etsy_client.make_request("/user/addresses/1", method=Method.DELETE)
        assert exc_info.value.code == 405
        assert exc_info.value.error == "<html>Method Not Allowed</html>"

    def test_empty_error_body_uses_reason_phrase(self, real_etsy_client):
        mock_resp = _make_mock_response(504)
        mock_resp.json.side_effect = ValueError("not JSON")
        mock_resp.text = ""
        mock_resp.reason = "Gateway Timeout"
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        with pytest.raises(RequestException) as exc_info:
            real_etsy_client.make_request("/shops/123")
        assert exc_info.value.error == "Gateway Timeout"

    def test_non_json_success_body_returns_response(self, real_etsy_client):
        mock_resp = _make_mock_response(202)
        mock_resp.json.side_effect = ValueError("not JSON")
        mock_resp.text = ""
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        result = real_etsy_client.make_request("/shops/123")
        assert result.code == 202
        assert result.message == "OK"

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

    def test_invalid_method_payload_combo_raises_value_error(self, real_etsy_client):
        # PUT with a non-Request payload passes the "Improper payload" guard
        # (payload is not None) but falls through every isinstance branch and
        # hits the final "Invalid method or payload" else.
        with pytest.raises(ValueError, match="Invalid method or payload"):
            real_etsy_client.make_request(
                "/shops/123", method=Method.PUT, payload="not-a-request"
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

    def test_limit_per_second_read_from_its_own_header(self, real_etsy_client):
        headers = {
            "X-Limit-Per-Second": "10",
            "X-Remaining-This-Second": "5",
            "X-Limit-Per-Day": "10000",
            "X-Remaining-Today": "9500",
        }
        mock_resp = _make_mock_response(200, {"shop_id": 123}, headers)
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        result = real_etsy_client.make_request("/shops/123")
        assert result.rate_limits.limit_per_second == "10"
        assert result.rate_limits.limit_per_day == "10000"

    def test_partial_rate_limit_headers_do_not_mask_error(self, real_etsy_client):
        # A 429 that carries only the daily headers must still raise
        # RequestException, not KeyError.
        mock_resp = _make_mock_response(
            429, {"error": "Too Many Requests"}, {"X-Limit-Per-Day": "10000"}
        )
        real_etsy_client._mock_http_session.get.return_value = mock_resp

        with pytest.raises(RequestException) as exc_info:
            real_etsy_client.make_request("/shops/123")
        assert exc_info.value.code == 429
        assert exc_info.value.rate_limits.limit_per_day == "10000"
        assert exc_info.value.rate_limits.remaining_today is None

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
    @pytest.mark.parametrize(
        "status_code, body",
        [
            (502, {"error": "Bad Gateway"}),
            (200, {"error": "invalid_grant"}),
            # Tokens present but expires_in missing or not numeric.
            (200, {"access_token": "new-a", "refresh_token": "new-r"}),
            (
                200,
                {"access_token": "new-a", "refresh_token": "new-r", "expires_in": "x"},
            ),
            (
                200,
                {"access_token": "new-a", "refresh_token": "new-r", "expires_in": True},
            ),
            (
                200,
                {
                    "access_token": "new-a",
                    "refresh_token": "new-r",
                    "expires_in": float("nan"),
                },
            ),
            (
                200,
                {"access_token": "new-a", "refresh_token": "new-r", "expires_in": 10**20},
            ),
        ],
    )
    def test_failed_refresh_keeps_authorization(
        self, real_etsy_client, status_code, body
    ):
        old_expiry = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        real_etsy_client.expiry = old_expiry
        real_etsy_client.sync_refresh = MagicMock()
        real_etsy_client._mock_http_session.post.return_value = _make_mock_response(
            status_code, body
        )

        with pytest.raises(RequestException):
            real_etsy_client.make_request("/shops/123")
        # A failed refresh changes nothing: header, tokens, expiry, callback.
        assert real_etsy_client._mock_http_session.headers["Authorization"] == (
            f"Bearer {MOCK_ACCESS_TOKEN}"
        )
        assert real_etsy_client.access_token == MOCK_ACCESS_TOKEN
        assert real_etsy_client.refresh_token == MOCK_REFRESH_TOKEN
        assert real_etsy_client.expiry == old_expiry
        real_etsy_client.sync_refresh.assert_not_called()
        real_etsy_client._mock_http_session.get.assert_not_called()

    def test_invalid_expires_in_is_named_in_error(self, real_etsy_client):
        real_etsy_client.expiry = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        real_etsy_client._mock_http_session.post.return_value = _make_mock_response(
            200, {"access_token": "new-a", "refresh_token": "new-r"}
        )

        with pytest.raises(RequestException) as exc_info:
            real_etsy_client.make_request("/shops/123")
        assert exc_info.value.error_description == (
            "Token refresh response has missing or invalid: expires_in"
        )

    def test_none_header_is_stripped_by_requests(self):
        # update_token relies on requests dropping a session header that a
        # call overrides with None.
        import requests

        session = requests.Session()
        session.headers["Authorization"] = "Bearer old"
        prepared = session.prepare_request(
            requests.Request(
                "POST", "https://example.com/token", headers={"Authorization": None}
            )
        )
        assert "Authorization" not in prepared.headers

    def test_non_json_refresh_raises_request_exception(self, real_etsy_client):
        real_etsy_client.expiry = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        refresh_resp = _make_mock_response(200)
        refresh_resp.json.side_effect = ValueError("not JSON")
        refresh_resp.text = "<html>Gateway</html>"
        real_etsy_client._mock_http_session.post.return_value = refresh_resp

        with pytest.raises(RequestException, match="non-JSON"):
            real_etsy_client.make_request("/shops/123")
        assert real_etsy_client._mock_http_session.headers["Authorization"] == (
            f"Bearer {MOCK_ACCESS_TOKEN}"
        )

    def test_refresh_drops_authorization_for_that_call_only(self, real_etsy_client):
        real_etsy_client.expiry = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        real_etsy_client._mock_http_session.post.return_value = _make_mock_response(
            200,
            {"access_token": "new-a", "refresh_token": "new-r", "expires_in": 3600},
        )
        real_etsy_client._mock_http_session.get.return_value = _make_mock_response(
            200, {"shop_id": 123}
        )

        real_etsy_client.make_request("/shops/123")
        post_kwargs = real_etsy_client._mock_http_session.post.call_args.kwargs
        assert post_kwargs["headers"] == {"Authorization": None}
        assert real_etsy_client._mock_http_session.headers["Authorization"] == (
            "Bearer new-a"
        )
        assert real_etsy_client.expiry.tzinfo is not None
        remaining = real_etsy_client.expiry - datetime.now(tz=timezone.utc)
        assert timedelta(seconds=3590) < remaining <= timedelta(seconds=3600)

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

    def test_valid_token_does_not_refresh(self, real_etsy_client):
        """A token with expiry in the future should not trigger a refresh."""
        real_etsy_client.expiry = datetime.now(tz=timezone.utc) + timedelta(hours=1)

        get_resp = _make_mock_response(200, {"shop_id": 123})
        real_etsy_client._mock_http_session.get.return_value = get_resp

        result = real_etsy_client.make_request("/shops/123")
        assert isinstance(result, Response)
        # post is used for token refresh; it should not be called
        real_etsy_client._mock_http_session.post.assert_not_called()

    def test_exact_expiry_boundary_triggers_refresh(self, real_etsy_client):
        """A token with expiry at exactly now should trigger a refresh (uses >= comparison)."""
        real_etsy_client.expiry = datetime.now(tz=timezone.utc)

        refresh_resp = _make_mock_response(
            200,
            {
                "access_token": "boundary-access-token",
                "refresh_token": "boundary-refresh-token",
                "expires_in": 3600,
            },
        )
        real_etsy_client._mock_http_session.post.return_value = refresh_resp

        get_resp = _make_mock_response(200, {"shop_id": 123})
        real_etsy_client._mock_http_session.get.return_value = get_resp

        result = real_etsy_client.make_request("/shops/123")
        assert isinstance(result, Response)
        # Refresh should have been called
        real_etsy_client._mock_http_session.post.assert_called_once()
        assert real_etsy_client.access_token == "boundary-access-token"

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
