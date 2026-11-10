import pytest

from etsy_python.v3.common.Utils import CLEAR
from etsy_python.v3.models.ShopEconomicOperator import (
    CreateShopEconomicOperatorRequest,
    UpdateShopEconomicOperatorRequest,
)
from etsy_python.v3.resources import ShopEconomicOperatorResource
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.enums.Request import Method

from tests.conftest import MOCK_SHOP_ID

MOCK_ECONOMIC_OPERATOR_ID = 12121


def _create_kwargs():
    return {
        "operator_name": "Acme GmbH",
        "email": "safety@example.com",
        "first_line": "Hauptstrasse 1",
        "city": "Berlin",
        "zip": "10115",
        "country_iso": "DE",
        "phone": "+49 30 123456",
    }


class TestCreateShopEconomicOperatorRequest:
    def test_serializes_required_fields(self):
        result = CreateShopEconomicOperatorRequest(**_create_kwargs()).get_dict()
        assert result == _create_kwargs()

    def test_serializes_optional_fields(self):
        result = CreateShopEconomicOperatorRequest(
            **_create_kwargs(),
            second_line="Etage 2",
            state="BE",
            phone_country_iso="DE",
            trademark_name="Acme",
        ).get_dict()
        assert result["second_line"] == "Etage 2"
        assert result["state"] == "BE"
        assert result["phone_country_iso"] == "DE"
        assert result["trademark_name"] == "Acme"

    @pytest.mark.parametrize("field", list(_create_kwargs()))
    def test_missing_required_field_raises(self, field):
        kwargs = _create_kwargs()
        kwargs[field] = None
        with pytest.raises(ValueError):
            CreateShopEconomicOperatorRequest(**kwargs)


    @pytest.mark.parametrize("blank", ["", "   "])
    def test_blank_required_field_raises(self, blank):
        with pytest.raises(ValueError, match="operator_name"):
            CreateShopEconomicOperatorRequest(
                **{**_create_kwargs(), "operator_name": blank}
            )


class TestUpdateShopEconomicOperatorRequest:
    def test_sends_only_set_fields(self):
        result = UpdateShopEconomicOperatorRequest(email="new@example.com").get_dict()
        assert result == {"email": "new@example.com"}

    def test_clear_sends_null_for_nullable_fields(self):
        result = UpdateShopEconomicOperatorRequest(
            second_line=CLEAR,
            state=CLEAR,
            phone_country_iso=CLEAR,
            trademark_name=CLEAR,
        ).get_dict()
        assert result == {
            "second_line": None,
            "state": None,
            "phone_country_iso": None,
            "trademark_name": None,
        }

    def test_blank_non_nullable_field_raises(self):
        with pytest.raises(ValueError, match="phone"):
            UpdateShopEconomicOperatorRequest(phone="")

    def test_clear_on_non_nullable_field_raises(self):
        with pytest.raises(ValueError, match="city"):
            UpdateShopEconomicOperatorRequest(city=CLEAR)


class TestShopEconomicOperatorResource:
    def test_create_shop_economic_operator(self, mock_session):
        mock_session.make_request.return_value = Response(200, {})
        payload = CreateShopEconomicOperatorRequest(**_create_kwargs())
        resource = ShopEconomicOperatorResource(session=mock_session)
        resource.create_shop_economic_operator(MOCK_SHOP_ID, payload)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/economic-operators",
            method=Method.POST,
            payload=payload,
        )

    def test_get_shop_economic_operators(self, mock_session):
        mock_session.make_request.return_value = Response(200, {})
        resource = ShopEconomicOperatorResource(session=mock_session)
        resource.get_shop_economic_operators(MOCK_SHOP_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/economic-operators"
        )

    def test_get_shop_economic_operator(self, mock_session):
        mock_session.make_request.return_value = Response(200, {})
        resource = ShopEconomicOperatorResource(session=mock_session)
        resource.get_shop_economic_operator(MOCK_SHOP_ID, MOCK_ECONOMIC_OPERATOR_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/economic-operators/{MOCK_ECONOMIC_OPERATOR_ID}"
        )

    def test_update_shop_economic_operator(self, mock_session):
        mock_session.make_request.return_value = Response(200, {})
        payload = UpdateShopEconomicOperatorRequest(city="Hamburg")
        resource = ShopEconomicOperatorResource(session=mock_session)
        resource.update_shop_economic_operator(
            MOCK_SHOP_ID, MOCK_ECONOMIC_OPERATOR_ID, payload
        )
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/economic-operators/{MOCK_ECONOMIC_OPERATOR_ID}",
            method=Method.PATCH,
            payload=payload,
        )

