from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from etsy_python.v3.resources.Session import EtsyClient

# Test constants
MOCK_KEYSTRING = "test-api-key-12345"
MOCK_ACCESS_TOKEN = "12345678.test-access-token"
MOCK_REFRESH_TOKEN = "test-refresh-token"
MOCK_USER_ID = "12345678"
MOCK_SHOP_ID = 98765
MOCK_LISTING_ID = 11111
MOCK_RECEIPT_ID = 22222
MOCK_LISTING_IMAGE_ID = 33333
MOCK_SHIPPING_PROFILE_ID = 44444
MOCK_SHIPPING_PROFILE_DESTINATION_ID = 55555
MOCK_SHIPPING_PROFILE_UPGRADE_ID = 66666
MOCK_SECTION_ID = 77777
MOCK_RETURN_POLICY_ID = 88888
MOCK_TRANSACTION_ID = 99999
MOCK_PAYMENT_ID = 10101
MOCK_LEDGER_ENTRY_ID = 20202
MOCK_TAXONOMY_ID = 30303
MOCK_PROPERTY_ID = 40404
MOCK_LISTING_FILE_ID = 50505
MOCK_VIDEO_ID = 60606
MOCK_PRODUCT_ID = 70707
MOCK_OFFERING_ID = 80808
MOCK_USER_ADDRESS_ID = 90909
MOCK_HOLIDAY_ID = "thanksgiving"


@pytest.fixture
def mock_session():
    """A MagicMock spec'd to EtsyClient, injected into resource dataclasses."""
    session = MagicMock(spec=EtsyClient)
    session.user_id = MOCK_USER_ID
    session.keystring = MOCK_KEYSTRING
    session.expiry = datetime.now(tz=timezone.utc) + timedelta(hours=1)
    return session


@pytest.fixture
def real_etsy_client():
    """A real EtsyClient with requests.Session patched out."""
    with patch("etsy_python.v3.resources.Session.Session") as mock_http_session_cls:
        mock_http_session = MagicMock()
        mock_http_session_cls.return_value = mock_http_session
        mock_http_session.headers = {}

        client = EtsyClient(
            keystring=MOCK_KEYSTRING,
            access_token=MOCK_ACCESS_TOKEN,
            refresh_token=MOCK_REFRESH_TOKEN,
            expiry=datetime.now(tz=timezone.utc) + timedelta(hours=1),
        )
        client._mock_http_session = mock_http_session
        yield client
