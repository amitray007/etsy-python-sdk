import pytest

from etsy_python.v3.models.Shop import (
    CreateShopSectionRequest,
    UpdateShopRequest,
    UpdateShopSectionRequest,
)


class TestUpdateShopRequest:
    def test_no_mandatory_fields(self):
        req = UpdateShopRequest(title="My Updated Shop")
        assert req.title == "My Updated Shop"

    def test_empty_request(self):
        req = UpdateShopRequest()
        result = req.get_dict()
        assert "title" not in result

    def test_multiple_fields(self):
        req = UpdateShopRequest(
            title="New Title",
            announcement="New announcement",
            sale_message="Thanks!",
        )
        result = req.get_dict()
        assert result["title"] == "New Title"
        assert result["announcement"] == "New announcement"
        assert result["sale_message"] == "Thanks!"


class TestCreateShopSectionRequest:
    def test_valid_request(self):
        req = CreateShopSectionRequest(title="New Section")
        assert req.title == "New Section"

    def test_missing_title_raises(self):
        with pytest.raises(ValueError):
            CreateShopSectionRequest(title=None)


class TestUpdateShopSectionRequest:
    def test_valid_request(self):
        req = UpdateShopSectionRequest(title="Updated Section")
        assert req.title == "Updated Section"

    def test_missing_title_raises(self):
        with pytest.raises(ValueError):
            UpdateShopSectionRequest(title=None)
