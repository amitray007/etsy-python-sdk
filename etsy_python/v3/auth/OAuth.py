from base64 import urlsafe_b64encode
from hashlib import sha256 as hash_sha256
from secrets import token_urlsafe
from typing import List, Optional, Tuple

from requests_oauthlib import OAuth2Session

from etsy_python.v3.common.Env import environment


class EtsyOAuth:
    def __init__(
        self,
        keystring: str,
        redirect_uri: str,
        scopes: Optional[List[str]] = None,
        code_verifier: Optional[str] = None,
        state: Optional[str] = None,
    ) -> None:
        self.keystring = keystring
        self.redirect_url = redirect_uri
        self.scopes = scopes
        self.code_verifier = token_urlsafe(32) if not code_verifier else ""
        self.code_challenge = EtsyOAuth._generate_challenge(self.code_verifier)
        self.oauth = OAuth2Session(
            keystring, redirect_uri=self.redirect_url, scope=scopes
        )
        self.state = token_urlsafe(16) if state is None else state
        self.auth_code: Optional[str] = None
        self.token: Optional[str] = None

    def get_auth_code(self) -> Tuple[str, str]:
        authorisation_url, state = self.oauth.authorization_url(
            environment.authorization_url,
            state=self.state,
            code_challenge=self.code_challenge,
            code_challenge_method="S256",
        )
        return authorisation_url, state

    def set_authorisation_code(self, code: str, state: str) -> None:
        if state != self.state:
            raise PermissionError
        self.auth_code = code

    def get_access_token(self) -> Optional[str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "x-api-key": self.keystring,
        }
        self.token = self.oauth.fetch_token(
            environment.token_url,
            code=self.auth_code,
            code_verifier=self.code_verifier,
            include_client_id=True,
            headers=headers,
        )
        return self.token

    @staticmethod
    def _generate_challenge(code_verifier: str) -> str:
        m = hash_sha256(code_verifier.encode("utf-8"))
        b64_encode = urlsafe_b64encode(m.digest()).decode("utf-8")
        return b64_encode.split("=")[0]
