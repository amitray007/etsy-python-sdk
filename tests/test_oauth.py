from base64 import urlsafe_b64encode
from hashlib import sha256
from unittest.mock import MagicMock, patch

import pytest

from etsy_python.v3.auth import EtsyOAuth
from etsy_python.v3.common.Env import environment

MOCK_KEYSTRING = "test-keystring"
MOCK_REDIRECT_URI = "https://example.com/callback"
MOCK_SCOPES = ["shops_r", "listings_r"]


@pytest.fixture
def patched_session():
    """Patches OAuth2Session in the OAuth module so no real HTTP happens."""
    with patch("etsy_python.v3.auth.OAuth.OAuth2Session") as mock_cls:
        mock_session = MagicMock()
        mock_cls.return_value = mock_session
        yield mock_cls, mock_session


class TestInit:
    def test_stores_keystring_and_redirect(self, patched_session):
        oauth = EtsyOAuth(MOCK_KEYSTRING, MOCK_REDIRECT_URI, MOCK_SCOPES)
        assert oauth.keystring == MOCK_KEYSTRING
        assert oauth.redirect_url == MOCK_REDIRECT_URI
        assert oauth.scopes == MOCK_SCOPES

    def test_auto_generates_code_verifier_when_not_supplied(self, patched_session):
        oauth = EtsyOAuth(MOCK_KEYSTRING, MOCK_REDIRECT_URI)
        # token_urlsafe(32) returns a non-empty url-safe string
        assert oauth.code_verifier
        assert isinstance(oauth.code_verifier, str)

    def test_supplied_code_verifier_blanks_internal_verifier(self, patched_session):
        # Existing behavior: supplying a code_verifier sets the attribute to ""
        # (the SDK only auto-generates a verifier when none is supplied).
        oauth = EtsyOAuth(
            MOCK_KEYSTRING, MOCK_REDIRECT_URI, code_verifier="caller-supplied"
        )
        assert oauth.code_verifier == ""

    def test_auto_generates_state_when_not_supplied(self, patched_session):
        oauth = EtsyOAuth(MOCK_KEYSTRING, MOCK_REDIRECT_URI)
        assert oauth.state
        assert isinstance(oauth.state, str)

    def test_supplied_state_is_used(self, patched_session):
        oauth = EtsyOAuth(MOCK_KEYSTRING, MOCK_REDIRECT_URI, state="caller-state")
        assert oauth.state == "caller-state"

    def test_constructs_oauth2_session_with_correct_args(self, patched_session):
        mock_cls, _ = patched_session
        EtsyOAuth(MOCK_KEYSTRING, MOCK_REDIRECT_URI, MOCK_SCOPES)
        mock_cls.assert_called_once_with(
            MOCK_KEYSTRING, redirect_uri=MOCK_REDIRECT_URI, scope=MOCK_SCOPES
        )

    def test_auth_code_and_token_start_none(self, patched_session):
        oauth = EtsyOAuth(MOCK_KEYSTRING, MOCK_REDIRECT_URI)
        assert oauth.auth_code is None
        assert oauth.token is None


class TestGenerateChallenge:
    def test_matches_known_sha256_b64_no_padding(self):
        verifier = "abc123"
        expected = (
            urlsafe_b64encode(sha256(verifier.encode("utf-8")).digest())
            .decode("utf-8")
            .split("=")[0]
        )
        assert EtsyOAuth._generate_challenge(verifier) == expected

    def test_no_padding_in_output(self):
        # PKCE requires base64url without padding
        challenge = EtsyOAuth._generate_challenge("some-verifier")
        assert "=" not in challenge


class TestGetAuthCode:
    def test_calls_oauth_authorization_url_with_pkce_params(self, patched_session):
        _, mock_session = patched_session
        mock_session.authorization_url.return_value = ("https://auth/url", "state-x")

        oauth = EtsyOAuth(MOCK_KEYSTRING, MOCK_REDIRECT_URI, state="state-x")
        url, state = oauth.get_auth_code()

        assert url == "https://auth/url"
        assert state == "state-x"
        mock_session.authorization_url.assert_called_once_with(
            environment.authorization_url,
            state="state-x",
            code_challenge=oauth.code_challenge,
            code_challenge_method="S256",
        )


class TestSetAuthorisationCode:
    def test_sets_auth_code_when_state_matches(self, patched_session):
        oauth = EtsyOAuth(MOCK_KEYSTRING, MOCK_REDIRECT_URI, state="state-x")
        oauth.set_authorisation_code("the-code", "state-x")
        assert oauth.auth_code == "the-code"

    def test_raises_permission_error_when_state_mismatch(self, patched_session):
        oauth = EtsyOAuth(MOCK_KEYSTRING, MOCK_REDIRECT_URI, state="state-x")
        with pytest.raises(PermissionError):
            oauth.set_authorisation_code("the-code", "state-y")
        assert oauth.auth_code is None


class TestGetAccessToken:
    def test_calls_fetch_token_with_pkce_params(self, patched_session):
        _, mock_session = patched_session
        mock_session.fetch_token.return_value = {"access_token": "the-token"}

        oauth = EtsyOAuth(MOCK_KEYSTRING, MOCK_REDIRECT_URI, state="state-x")
        oauth.set_authorisation_code("the-code", "state-x")
        token = oauth.get_access_token()

        assert token == {"access_token": "the-token"}
        mock_session.fetch_token.assert_called_once_with(
            environment.token_url,
            code="the-code",
            code_verifier=oauth.code_verifier,
            include_client_id=True,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "x-api-key": MOCK_KEYSTRING,
            },
        )
