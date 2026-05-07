from etsy_python.v3.models.Receipt import (
    CreateReceiptShipmentRequest,
    UpdateShopReceiptRequest,
)


class TestCreateReceiptShipmentRequest:
    def test_no_mandatory_fields(self):
        req = CreateReceiptShipmentRequest(
            tracking_code="1Z999AA10123456784",
            carrier_name="USPS",
        )
        assert req.tracking_code == "1Z999AA10123456784"
        assert req.carrier_name == "USPS"

    def test_empty_request(self):
        req = CreateReceiptShipmentRequest()
        result = req.get_dict()
        # All None fields excluded
        assert "tracking_code" not in result

    def test_with_note_and_bcc(self):
        req = CreateReceiptShipmentRequest(
            tracking_code="TRACK123",
            carrier_name="FedEx",
            send_bcc=True,
            note_to_buyer="Shipping soon!",
        )
        result = req.get_dict()
        assert result["send_bcc"] is True
        assert result["note_to_buyer"] == "Shipping soon!"

    def test_with_shipping_label_fields(self):
        req = CreateReceiptShipmentRequest(
            tracking_code="TRACK123",
            carrier_name="USPS",
            mail_class="Priority",
            weight=1.5,
            weight_units="lb",
            length=10.0,
            width=8.0,
            height=4.0,
            dimension_units="in",
            shipping_label_cost=8.95,
            shipping_label_currency="USD",
            ship_from_country="US",
            ship_to_country="CA",
            ship_date="2026-05-07",
        )
        result = req.get_dict()
        assert result["mail_class"] == "Priority"
        assert result["weight"] == 1.5
        assert result["weight_units"] == "lb"
        assert result["length"] == 10.0
        assert result["width"] == 8.0
        assert result["height"] == 4.0
        assert result["dimension_units"] == "in"
        assert result["shipping_label_cost"] == 8.95
        assert result["shipping_label_currency"] == "USD"
        assert result["ship_from_country"] == "US"
        assert result["ship_to_country"] == "CA"
        assert result["ship_date"] == "2026-05-07"

    def test_with_customs_and_duty_fields(self):
        customs = [
            {
                "country_of_origin": "US",
                "declared_value": 25.00,
                "HS_code": "9503.00.00",
            }
        ]
        req = CreateReceiptShipmentRequest(
            tracking_code="TRACK123",
            customs_data=customs,
            incoterm="DDP",
            duty_amount=2.50,
            duty_currency="USD",
            revenue_eligibility="eligible",
        )
        result = req.get_dict()
        assert result["customs_data"] == customs
        assert result["incoterm"] == "DDP"
        assert result["duty_amount"] == 2.50
        assert result["duty_currency"] == "USD"
        assert result["revenue_eligibility"] == "eligible"

    def test_new_optional_fields_excluded_when_none(self):
        req = CreateReceiptShipmentRequest(tracking_code="TRACK123")
        result = req.get_dict()
        for key in (
            "mail_class", "weight", "weight_units", "length", "width", "height",
            "dimension_units", "shipping_label_cost", "shipping_label_currency",
            "revenue_eligibility", "ship_from_country", "ship_to_country",
            "incoterm", "customs_data", "duty_amount", "duty_currency", "ship_date",
        ):
            assert key not in result


class TestUpdateShopReceiptRequest:
    def test_no_mandatory_fields(self):
        req = UpdateShopReceiptRequest(was_shipped=True)
        assert req.was_shipped is True

    def test_nullable_fields_with_false(self):
        req = UpdateShopReceiptRequest(was_shipped=False, was_paid=False)
        # Boolean False is a valid distinct value from null; it should serialize as False
        result = req.get_dict()
        assert result["was_shipped"] is False
        assert result["was_paid"] is False

    def test_nullable_fields_with_true(self):
        req = UpdateShopReceiptRequest(was_shipped=True, was_paid=True)
        result = req.get_dict()
        assert result["was_shipped"] is True
        assert result["was_paid"] is True
