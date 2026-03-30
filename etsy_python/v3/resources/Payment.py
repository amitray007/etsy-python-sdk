import warnings
from dataclasses import dataclass
from typing import Union, Dict, Any, List

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.Response import Response


@dataclass
class PaymentResource:
    session: EtsyClient

    def get_payment_account_ledger_entry_payments(
        self, shop_id: int, ledger_entry_ids: List[int]
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/payment-account/ledger-entries/payments"
        query_params: Dict[str, Any] = {
            "ledger_entry_ids": ",".join(list(map(str, ledger_entry_ids)))
        }
        return self.session.make_request(endpoint, query_params=query_params)

    def get_shop_payment_account_ledger_entry_payments(
        self, shop_id: int, ledger_entry_ids: List[int]
    ) -> Union[Response, RequestException]:
        """Deprecated: use get_payment_account_ledger_entry_payments instead."""
        warnings.warn(
            "get_shop_payment_account_ledger_entry_payments is deprecated, "
            "use get_payment_account_ledger_entry_payments",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_payment_account_ledger_entry_payments(shop_id, ledger_entry_ids)

    def get_shop_payment_by_receipt_id(
        self, shop_id: int, receipt_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/receipts/{receipt_id}/payments"
        return self.session.make_request(endpoint)

    def get_payments(
        self, shop_id: int, payment_ids: List[int]
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/payments"
        query_params: Dict[str, Any] = {"payment_ids": ",".join(list(map(str, payment_ids)))}
        return self.session.make_request(endpoint, query_params=query_params)
