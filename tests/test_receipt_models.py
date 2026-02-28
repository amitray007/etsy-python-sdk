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
