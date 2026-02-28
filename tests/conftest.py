import os
from datetime import datetime, timezone

import pytest

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from etsy_python.v3.resources.Session import EtsyClient


def _get_env(name: str) -> str:
    """Get a required environment variable."""
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"Missing required env var: {name}")
    return value


@pytest.fixture(scope="session")
def api_key() -> str:
    return _get_env("ETSY_API_KEY")


@pytest.fixture(scope="session")
def shop_id() -> int:
    return int(_get_env("ETSY_SHOP_ID"))


@pytest.fixture(scope="session")
def etsy_client(api_key) -> EtsyClient:
    """Create an EtsyClient for the test session."""
    access_token = _get_env("ETSY_ACCESS_TOKEN")
    refresh_token = _get_env("ETSY_REFRESH_TOKEN")
    expiry_str = _get_env("ETSY_TOKEN_EXPIRY")

    try:
        expiry = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
    except ValueError:
        expiry = datetime.now(tz=timezone.utc)

    return EtsyClient(
        keystring=api_key,
        access_token=access_token,
        refresh_token=refresh_token,
        expiry=expiry,
    )
