from dataclasses import dataclass
from typing import Union, Dict, Any, List

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.Response import Response


@dataclass
class PaymentResource:
    session: EtsyClient

    def get_shop_payment_account_ledger_entry_payments(
        self, shop_id: int, ledger_entry_ids: List[int]
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/payment-account/ledger-entries/payments"
        kwargs: Dict[str, Any] = {
            "ledger_entry_ids": ",".join(list(map(str, ledger_entry_ids)))
        }
        return self.session.make_request(endpoint, **kwargs)

    def get_shop_payment_by_receipt_id(
        self, shop_id: int, receipt_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/receipts/{receipt_id}/payments"
        return self.session.make_request(endpoint)

    def get_payments(
        self, shop_id: int, payment_ids: List[int]
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/payments"
        kwargs: Dict[str, Any] = {"payment_ids": ",".join(list(map(str, payment_ids)))}
        return self.session.make_request(endpoint, **kwargs)
