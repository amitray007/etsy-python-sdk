from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional

from requests import Session

from etsy_python.v3.common.Request import NO_RESPONSE_CODES
from etsy_python.v3.common.Env import environment
from etsy_python.v3.common.Utils import generate_get_uri
from etsy_python.v3.resources.enums.Request import Method
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Request import Request
from etsy_python.v3.models.FileRequest import FileRequest
from etsy_python.v3.resources.enums.RateLimit import RateLimit


class EtsyClient:
    def __init__(
        self,
        keystring: str,
        access_token: str,
        refresh_token: str,
        expiry: datetime,
        sync_refresh: Optional[Callable[[str, str, datetime], None]] = None,
    ) -> None:
        self.keystring = keystring
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry = expiry
        self.sync_refresh = sync_refresh

        self.user_id = self._get_user_id(access_token)

        self.session = Session()
        self.session.headers = self._get_resource_headers(keystring, access_token)

    def update_token(self) -> tuple:
        refresh_json = self._get_refresh_json(self.keystring, self.refresh_token)
        # Drop Authorization for this call only. The shared session header is
        # never touched, so a failed refresh cannot leave later requests
        # unauthenticated.
        response = self.session.post(
            environment.token_url, json=refresh_json, headers={"Authorization": None}
        )
        response_json = self._process_request(response).message
        if not isinstance(response_json, dict):
            raise RequestException(
                code=response.status_code,
                error="Token refresh returned a non-JSON body",
            )
        access_token = response_json.get("access_token")
        refresh_token = response_json.get("refresh_token")
        expires_in = response_json.get("expires_in")
        # expires_in must be a positive int; bool is an int subclass, and
        # floats allow NaN/inf, which timedelta cannot handle.
        invalid = [
            name
            for name, ok in (
                ("access_token", bool(access_token)),
                ("refresh_token", bool(refresh_token)),
                (
                    "expires_in",
                    isinstance(expires_in, int)
                    and not isinstance(expires_in, bool)
                    and 0 < expires_in <= 10**9,
                ),
            )
            if not ok
        ]
        if invalid:
            raise RequestException(
                code=401,
                error=response_json.get("error", "Something went wrong!"),
                error_description=response_json.get("error_description")
                or "Token refresh response has missing or invalid: "
                + ", ".join(invalid),
            )

        # Store the new tokens only once the whole response is valid.
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)

        self.session.headers.update(
            self._prepare_authorization_token(self.access_token)
        )
        updated_tuple = (self.access_token, self.refresh_token, self.expiry)
        if self.sync_refresh is not None:
            self.sync_refresh(*updated_tuple)
        return updated_tuple

    def _get_resource_headers(self, keystring: str, access_token: str) -> dict:
        return {
            **self._prepare_authorization_token(access_token),
            **self._get_request_headers(keystring),
        }

    @staticmethod
    def _prepare_authorization_token(access_token: str) -> dict:
        return {"Authorization": f"Bearer {access_token}"}

    @staticmethod
    def _get_request_headers(keystring: str) -> dict:
        return {"Accept": "application/json", "x-api-key": keystring}

    @staticmethod
    def _get_refresh_json(keystring: str, refresh_token: str) -> dict:
        return {
            "grant_type": "refresh_token",
            "client_id": keystring,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def _get_user_id(access_token: str):
        return access_token.split(".")[0]
    
    @staticmethod
    def ensure_utc(expiry_time: datetime):
        if expiry_time.tzinfo is None:
            expiry_time = expiry_time.replace(tzinfo=timezone.utc)
        else:
            expiry_time = expiry_time.astimezone(timezone.utc)
        return expiry_time

    def make_request(
        self,
        uri_path: str,
        method: Method = Method.GET,
        payload: Optional[Request] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if method not in {Method.GET, Method.DELETE} and payload is None:
            raise ValueError(f"Improper payload for {method}")

        is_token_expired = datetime.now(tz=timezone.utc) >= self.ensure_utc(self.expiry)
        if is_token_expired:
            self.update_token()

        uri_path = f"{environment.request_url}{uri_path}"
        uri_path = generate_get_uri(uri_path, query_params)
        if method == Method.GET:
            response = self.session.get(uri_path)
        elif method == Method.PUT and isinstance(payload, Request):
            response = self.session.put(uri_path, json=payload.get_dict())
        elif method == Method.POST and isinstance(payload, FileRequest):
            response = self.session.post(
                uri_path, files=payload.file, data=payload.data
            )
        elif method == Method.POST and isinstance(payload, Request):
            response = self.session.post(uri_path, json=payload.get_dict())
        elif method == Method.PATCH and isinstance(payload, Request):
            response = self.session.patch(uri_path, json=payload.get_dict())
        elif method == Method.DELETE:
            response = self.session.delete(uri_path)
        else:
            raise ValueError("Invalid method or payload")
        return self._process_request(response)

    def _process_request(self, response: Any) -> Any:
        # Any 4xx/5xx is an error, including codes Etsy documents later
        # (e.g. 429 for the uploadListingVideo daily limit).
        is_error = response.status_code >= 400

        rate_limits = None
        if "X-Limit-Per-Day" in response.headers:
            rate_limits = RateLimit(
                response.headers.get("X-Limit-Per-Second"),
                response.headers.get("X-Remaining-This-Second"),
                response.headers.get("X-Limit-Per-Day"),
                response.headers.get("X-Remaining-Today"),
            )

        if is_error:
            try:
                response_json = response.json()
            except ValueError:
                # Gateway and method errors (405, 502, 504) can return a
                # non-JSON or empty body; keep the text, or the reason phrase.
                response_json = response.text or response.reason
            error_response = (
                response_json
                if isinstance(response_json, dict)
                else dict(error=response_json)
            )
            error_message = error_response.get("error")
            error_description = error_response.get("error_description")
            raise RequestException(
                response.status_code,
                error_message,
                error_description,
                rate_limits=rate_limits,
            )
        response_json = None
        if response.status_code not in NO_RESPONSE_CODES:
            try:
                response_json = response.json()
            except ValueError:
                # A success with an empty or non-JSON body (202, 304, ...).
                response_json = response.text
        return Response(
            response.status_code, response_json or "OK", rate_limits=rate_limits
        )
