from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

from requests import Session

from etsy_python.v3.common.Request import ERROR_CODES
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
        response = self.session.post(environment.token_url, json=refresh_json)
        response_json = self._process_request(response).message

        self.token = response_json.get("access_token")
        self.refresh_token = response_json.get("refresh_token")
        if not (self.token and self.refresh_token):
            raise RequestException(code=401, error=response_json.get("error", "Something went wrong!"))

        updated_expiry = datetime.utcnow() + timedelta(
            seconds=response_json["expires_in"]
        )
        self.expiry = updated_expiry

        self.session.headers.update(self._prepare_authorization_token(self.token))
        updated_tuple = (self.token, self.refresh_token, self.expiry)
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

    def make_request(
        self,
        uri_path: str,
        method: Method = Method.GET,
        payload: Optional[Request] = None,
        **kwargs: Dict[str, Any],
    ) -> Any:
        if method not in {Method.GET, Method.DELETE} and payload is None:
            raise ValueError(f"Improper payload for {method}")

        if datetime.utcnow() >= self.expiry:
            self.update_token()

        uri_path = f"{environment.request_url}{uri_path}"
        if method == Method.GET:
            uri_path = generate_get_uri(uri_path, **kwargs)
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
        is_error = response.status_code in ERROR_CODES

        rate_limits = None
        if "X-Limit-Per-Day" in response.headers:
            rate_limits = RateLimit(
                response.headers["X-Limit-Per-Day"],
                response.headers["X-Remaining-This-Second"],
                response.headers["X-Limit-Per-Day"],
                response.headers["X-Remaining-Today"],
            )

        response_json = response.json()
        if is_error:
            error_message = response_json.get("error")
            error_description = response_json.get("error_description")
            raise RequestException(
                response.status_code,
                error_message,
                error_description,
                rate_limits=rate_limits,
            )
        return Response(
            response.status_code, response_json or "OK", rate_limits=rate_limits
        )
