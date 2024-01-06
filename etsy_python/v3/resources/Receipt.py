from dataclasses import dataclass
from typing import Optional, Union, Dict, Any

from etsy_python.v3.enums.ShopReceipt import SortOn, SortOrder
from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Receipt import CreateReceiptShipmentRequest, UpdateShopReceiptRequest
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.enums.Request import Method


@dataclass
class ReceiptResource:
    session: EtsyClient

    def get_shop_receipt(
        self, shop_id: int, receipt_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/receipts/{receipt_id}"
        return self.session.make_request(endpoint)

    def update_shop_receipt(
        self,
        shop_id: int,
        receipt_id: int,
        shop_receipt_request: UpdateShopReceiptRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/receipts/{receipt_id}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=shop_receipt_request
        )

    def get_shop_receipts(
        self,
        shop_id: int,
        min_created: Optional[int] = None,
        max_created: Optional[int] = None,
        min_last_modified: Optional[int] = None,
        max_last_modified: Optional[int] = None,
        limit: int = 25,
        offset: int = 0,
        sort_on: SortOn = SortOn.CREATED,
        sort_order: SortOrder = SortOrder.DESC,
        was_paid: Optional[bool] = None,
        was_shipped: Optional[bool] = None,
        was_delivered: Optional[bool] = None,
        was_canceled: Optional[bool] = None,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/receipts"
        kwargs: Dict[str, Any] = {
            "max_created": max_created,
            "min_created": min_created,
            "min_last_modified": min_last_modified,
            "max_last_modified": max_last_modified,
            "limit": limit,
            "offset": offset,
            "sort_on": sort_on.value,
            "sort_order": sort_order.value,
            "was_paid": was_paid,
            "was_shipped": was_shipped,
            "was_delivered": was_delivered,
            "was_canceled": was_canceled,
        }
        return self.session.make_request(endpoint, **kwargs)

    def create_receipt_shipment(
        self,
        shop_id: int,
        receipt_id: int,
        receipt_shipment_request: CreateReceiptShipmentRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/receipts/{receipt_id}/tracking"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=receipt_shipment_request
        )
