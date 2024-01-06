from dataclasses import dataclass
from typing import Union, Dict, Any

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.Response import Response


@dataclass
class PaymentLedgeEntryResource:
    session: EtsyClient

    def get_shop_payment_account_ledger_entry(
        self, shop_id: int, ledger_entry_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/payment-account/ledger-entries/{ledger_entry_id}"
        return self.session.make_request(endpoint)

    def get_shop_payment_account_ledger_entries(
        self,
        shop_id: int,
        min_created: int,
        max_created: int,
        limit: int = 25,
        offset: int = 0,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/payment-account/ledger-entries"
        kwargs: Dict[str, Any] = {
            "max_created": max_created,
            "min_created": min_created,
            "limit": limit,
            "offset": offset,
        }
        return self.session.make_request(endpoint, **kwargs)
