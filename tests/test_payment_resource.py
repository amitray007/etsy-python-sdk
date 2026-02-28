from etsy_python.v3.resources.Payment import PaymentResource
from etsy_python.v3.resources.Response import Response

from tests.conftest import MOCK_LEDGER_ENTRY_ID, MOCK_PAYMENT_ID, MOCK_RECEIPT_ID, MOCK_SHOP_ID
from tests.fixtures.responses import make_payment, make_payment_collection


class TestGetShopPaymentByReceiptId:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_payment_collection()
        )
        resource = PaymentResource(session=mock_session)

        result = resource.get_shop_payment_by_receipt_id(MOCK_SHOP_ID, MOCK_RECEIPT_ID)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/receipts/{MOCK_RECEIPT_ID}/payments"
        )


class TestGetPayments:
    def test_payment_ids_joined(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_payment_collection()
        )
        resource = PaymentResource(session=mock_session)

        resource.get_payments(MOCK_SHOP_ID, [MOCK_PAYMENT_ID, 20202])

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp["payment_ids"] == f"{MOCK_PAYMENT_ID},20202"


class TestGetShopPaymentAccountLedgerEntryPayments:
    def test_ledger_entry_ids_joined(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_payment_collection()
        )
        resource = PaymentResource(session=mock_session)

        resource.get_shop_payment_account_ledger_entry_payments(
            MOCK_SHOP_ID, [MOCK_LEDGER_ENTRY_ID, 30303]
        )

        call_args = mock_session.make_request.call_args
        assert (
            call_args[0][0]
            == f"/shops/{MOCK_SHOP_ID}/payment-account/ledger-entries/payments"
        )
        assert call_args[1]["query_params"]["ledger_entry_ids"] == f"{MOCK_LEDGER_ENTRY_ID},30303"
