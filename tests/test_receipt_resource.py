from unittest.mock import MagicMock

from etsy_python.v3.enums.ShopReceipt import SortOn, SortOrder
from etsy_python.v3.models.Receipt import (
    CreateReceiptShipmentRequest,
    UpdateShopReceiptRequest,
)
from etsy_python.v3.resources.Receipt import ReceiptResource
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.enums.Request import Method

from tests.conftest import MOCK_RECEIPT_ID, MOCK_SHOP_ID
from tests.fixtures.responses import make_shop_receipt, make_shop_receipt_collection


class TestGetShopReceipt:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop_receipt())
        resource = ReceiptResource(session=mock_session)

        result = resource.get_shop_receipt(MOCK_SHOP_ID, MOCK_RECEIPT_ID)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/receipts/{MOCK_RECEIPT_ID}",
            query_params={"legacy": None},
        )


class TestUpdateShopReceipt:
    def test_calls_put_with_payload(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop_receipt())
        resource = ReceiptResource(session=mock_session)
        payload = MagicMock(spec=UpdateShopReceiptRequest)

        result = resource.update_shop_receipt(MOCK_SHOP_ID, MOCK_RECEIPT_ID, payload)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/receipts/{MOCK_RECEIPT_ID}",
            method=Method.PUT,
            payload=payload,
            query_params={"legacy": None},
        )


class TestGetShopReceipts:
    def test_default_params(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_receipt_collection()
        )
        resource = ReceiptResource(session=mock_session)

        result = resource.get_shop_receipts(MOCK_SHOP_ID)

        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == f"/shops/{MOCK_SHOP_ID}/receipts"
        qp = call_args[1]["query_params"]
        assert qp["sort_on"] == SortOn.CREATED.value
        assert qp["sort_order"] == SortOrder.DESC.value

    def test_with_filters(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_receipt_collection()
        )
        resource = ReceiptResource(session=mock_session)

        resource.get_shop_receipts(
            MOCK_SHOP_ID,
            was_paid=True,
            was_shipped=False,
            min_created=1640000000,
            max_created=1641000000,
        )

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp["was_paid"] is True
        assert qp["was_shipped"] is False
        assert qp["min_created"] == 1640000000
        assert qp["max_created"] == 1641000000


class TestCreateReceiptShipment:
    def test_calls_post_with_payload(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop_receipt())
        resource = ReceiptResource(session=mock_session)
        payload = MagicMock(spec=CreateReceiptShipmentRequest)

        result = resource.create_receipt_shipment(
            MOCK_SHOP_ID, MOCK_RECEIPT_ID, payload
        )

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/receipts/{MOCK_RECEIPT_ID}/tracking",
            method=Method.POST,
            payload=payload,
            query_params={"legacy": None},
        )
