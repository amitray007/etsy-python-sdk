import pytest

from etsy_python.v3.models.Request import Request


class ConcreteRequest(Request):
    """A concrete Request subclass for testing."""

    def __init__(self, name=None, value=None, optional_field=None):
        self.name = name
        self.value = value
        self.optional_field = optional_field
        super().__init__(
            mandatory=["name", "value"],
            nullable=["optional_field"],
        )


class NoMandatoryRequest(Request):
    """Request subclass with no mandatory fields."""

    def __init__(self, title=None, description=None):
        self.title = title
        self.description = description
        super().__init__(mandatory=[], nullable=["title", "description"])


class TestCheckMandatory:
    def test_all_mandatory_provided(self):
        req = ConcreteRequest(name="test", value=42)
        assert req.check_mandatory() is True

    def test_mandatory_field_missing(self):
        with pytest.raises(ValueError):
            ConcreteRequest(name="test", value=None)

    def test_all_mandatory_missing(self):
        with pytest.raises(ValueError):
            ConcreteRequest(name=None, value=None)

    def test_no_mandatory_fields(self):
        req = NoMandatoryRequest()
        assert req.check_mandatory() is True


class TestGetNulled:
    def test_nullable_field_empty_string(self):
        req = ConcreteRequest(name="test", value=42, optional_field="")
        nulled = req.get_nulled()
        assert "optional_field" in nulled

    def test_nullable_field_empty_list(self):
        req = ConcreteRequest(name="test", value=42, optional_field=[])
        nulled = req.get_nulled()
        assert "optional_field" in nulled

    def test_nullable_field_zero(self):
        req = ConcreteRequest(name="test", value=42, optional_field=0)
        nulled = req.get_nulled()
        assert "optional_field" in nulled

    def test_nullable_field_with_value(self):
        req = ConcreteRequest(name="test", value=42, optional_field="data")
        nulled = req.get_nulled()
        assert nulled == []

    def test_non_nullable_field_not_in_nulled(self):
        req = ConcreteRequest(name="test", value=42)
        nulled = req.get_nulled()
        assert "name" not in nulled
        assert "value" not in nulled


class TestGetDict:
    def test_basic_serialization(self):
        req = ConcreteRequest(name="test", value=42, optional_field="data")
        result = req.get_dict()
        assert result["name"] == "test"
        assert result["value"] == 42
        assert result["optional_field"] == "data"

    def test_nullable_empty_becomes_none(self):
        req = ConcreteRequest(name="test", value=42, optional_field="")
        result = req.get_dict()
        assert result["optional_field"] is None

    def test_private_fields_excluded(self):
        req = ConcreteRequest(name="test", value=42)
        result = req.get_dict()
        assert "_nullable" not in result
        assert "_mandatory" not in result

    def test_none_fields_excluded(self):
        req = ConcreteRequest(name="test", value=42)
        result = req.get_dict()
        assert "optional_field" not in result
