import pytest

from etsy_python.v3.resources.Receipt import ReceiptResource
from etsy_python.v3.resources.ReceiptTransactions import ReceiptTransactionsResource
from etsy_python.v3.resources.Payment import PaymentResource
from etsy_python.v3.resources.Response import Response


@pytest.mark.readonly
class TestReceipt:
    def test_get_shop_receipts(self, etsy_client, shop_id):
        resource = ReceiptResource(session=etsy_client)
        response = resource.get_shop_receipts(shop_id)
        assert isinstance(response, Response)
        assert response.code == 200

    def test_get_shop_receipt_transactions_by_shop(self, etsy_client, shop_id):
        resource = ReceiptTransactionsResource(session=etsy_client)
        response = resource.get_shop_receipt_transaction_by_shop(shop_id)
        assert isinstance(response, Response)
        assert response.code == 200


@pytest.mark.readonly
class TestPayment:
    def test_get_payment_by_receipt_id(self, etsy_client, shop_id):
        """Get payments for the first available receipt, if any exist."""
        receipt_resource = ReceiptResource(session=etsy_client)
        receipts_response = receipt_resource.get_shop_receipts(shop_id)
        assert isinstance(receipts_response, Response)
        assert receipts_response.code == 200

        results = receipts_response.message.get("results", [])
        if not results:
            pytest.skip("No receipts available to test payment lookup")

        receipt_id = results[0]["receipt_id"]
        payment_resource = PaymentResource(session=etsy_client)
        response = payment_resource.get_shop_payment_by_receipt_id(
            shop_id, receipt_id
        )
        assert isinstance(response, Response)
        assert response.code == 200
