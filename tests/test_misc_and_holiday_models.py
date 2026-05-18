import pytest

from etsy_python.v3.models.HolidayPreferences import UpdateHolidayPreferencesRequest
from etsy_python.v3.models.Miscellaneous import GetTokenScopes


class TestGetTokenScopes:
    def test_stores_token(self):
        req = GetTokenScopes(token="abc123")
        assert req.token == "abc123"

    def test_missing_mandatory_raises(self):
        with pytest.raises(Exception):
            GetTokenScopes()


class TestUpdateHolidayPreferencesRequest:
    def test_stores_is_working_true(self):
        req = UpdateHolidayPreferencesRequest(is_working=True)
        assert req.is_working is True

    def test_stores_is_working_false(self):
        # False is the documented default; constructor must still accept it
        # without raising and preserve the literal False.
        req = UpdateHolidayPreferencesRequest(is_working=False)
        assert req.is_working is False
        result = req.get_dict()
        assert result["is_working"] is False
