from enum import Enum

from etsy_python.v3.common.Utils import generate_get_uri, todict


class TestGenerateGetUri:
    def test_no_kwargs(self):
        assert generate_get_uri("/shops/123") == "/shops/123"

    def test_empty_kwargs(self):
        assert generate_get_uri("/shops/123") == "/shops/123"

    def test_single_kwarg(self):
        result = generate_get_uri("/shops/123", limit=25)
        assert result == "/shops/123?limit=25"

    def test_multiple_kwargs(self):
        result = generate_get_uri("/shops/123", limit=25, offset=0)
        assert "limit=25" in result
        assert "offset=0" in result
        assert result.startswith("/shops/123?")

    def test_none_values_filtered(self):
        result = generate_get_uri("/shops/123", limit=25, keywords=None)
        assert result == "/shops/123?limit=25"
        assert "keywords" not in result

    def test_all_none_values(self):
        result = generate_get_uri("/shops/123", limit=None, offset=None)
        assert result == "/shops/123"


class SampleEnum(Enum):
    VALUE_A = "alpha"
    VALUE_B = "beta"


class SimpleObj:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class TestTodict:
    def test_simple_object(self):
        obj = SimpleObj(1, "hello")
        result = todict(obj)
        assert result == {"x": 1, "y": "hello"}

    def test_enum_value(self):
        result = todict(SampleEnum.VALUE_A)
        assert result == "alpha"

    def test_nested_object(self):
        inner = SimpleObj(10, 20)
        outer = SimpleObj(inner, "outer")
        result = todict(outer)
        assert result == {"x": {"x": 10, "y": 20}, "y": "outer"}

    def test_dict_passthrough(self):
        result = todict({"a": 1, "b": 2})
        assert result == {"a": 1, "b": 2}

    def test_list_iteration(self):
        result = todict([1, 2, 3])
        assert result == [1, 2, 3]

    def test_string_passthrough(self):
        result = todict("hello")
        assert result == "hello"

    def test_int_passthrough(self):
        result = todict(42)
        assert result == 42

    def test_none_fields_excluded(self):
        obj = SimpleObj(None, "hello")
        result = todict(obj)
        assert result == {"y": "hello"}

    def test_nullable_fields(self):
        obj = SimpleObj("", "hello")
        result = todict(obj, nullable=["x"])
        assert result == {"x": None, "y": "hello"}

    def test_type_renaming(self):
        """_type attribute should be renamed to 'type' in output."""

        class ObjWithType:
            def __init__(self):
                self._type = "physical"
                self.name = "test"

        result = todict(ObjWithType())
        assert "type" in result
        assert result["type"] == "physical"
        assert "_type" not in result

    def test_private_fields_excluded(self):
        """Fields starting with _ (except _type) should be excluded."""

        class ObjWithPrivate:
            def __init__(self):
                self.public = "visible"
                self._private = "hidden"

        result = todict(ObjWithPrivate())
        assert result == {"public": "visible"}

    def test_callable_fields_excluded(self):
        class ObjWithMethod:
            def __init__(self):
                self.value = 42
                self.method = lambda: None

        result = todict(ObjWithMethod())
        assert result == {"value": 42}

    def test_enum_in_object(self):
        class ObjWithEnum:
            def __init__(self):
                self.status = SampleEnum.VALUE_A
                self.name = "test"

        result = todict(ObjWithEnum())
        assert result == {"status": "alpha", "name": "test"}

    def test_classkey(self):
        obj = SimpleObj(1, 2)
        result = todict(obj, classkey="__class__")
        assert result["__class__"] == "SimpleObj"
        assert result["x"] == 1

    def test_bool_false_not_excluded(self):
        """Boolean False should be kept, not treated as empty."""

        class ObjWithBool:
            def __init__(self):
                self.flag = False

        result = todict(ObjWithBool())
        assert result == {"flag": False}
