import warnings
from dataclasses import dataclass
from typing import Optional, Union, Dict, Any

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.Response import Response


@dataclass
class ReceiptTransactionsResource:
    session: EtsyClient

    def get_shop_receipt_transactions_by_listing(
        self, shop_id: int, listing_id: int, limit: int = 25, offset: int = 0,
        legacy: Optional[bool] = None,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/transactions"
        query_params: Dict[str, Any] = {"limit": limit, "offset": offset, "legacy": legacy}
        return self.session.make_request(endpoint, query_params=query_params)

    def get_shop_receipt_transactions_by_receipt(
        self, shop_id: int, receipt_id: int,
        legacy: Optional[bool] = None,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/receipts/{receipt_id}/transactions"
        query_params: Dict[str, Any] = {"legacy": legacy}
        return self.session.make_request(endpoint, query_params=query_params)

    def get_shop_receipt_transaction(
        self, shop_id: int, transaction_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/transactions/{transaction_id}"
        return self.session.make_request(endpoint)

    def get_shop_receipt_transactions_by_shop(
        self, shop_id: int, limit: int = 25, offset: int = 0
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/transactions"
        query_params: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self.session.make_request(endpoint, query_params=query_params)

    def get_shop_receipt_transaction_by_shop(
        self, shop_id: int, limit: int = 25, offset: int = 0
    ) -> Union[Response, RequestException]:
        """Deprecated: use get_shop_receipt_transactions_by_shop instead."""
        warnings.warn(
            "get_shop_receipt_transaction_by_shop is deprecated, use get_shop_receipt_transactions_by_shop",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_shop_receipt_transactions_by_shop(shop_id, limit, offset)
