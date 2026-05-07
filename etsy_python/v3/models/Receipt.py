from typing import Any, Dict, List, Optional

from etsy_python.v3.models.Request import Request


class CreateReceiptShipmentRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = []

    def __init__(
        self,
        tracking_code: Optional[str] = None,
        carrier_name: Optional[str] = None,
        send_bcc: Optional[bool] = None,
        note_to_buyer: Optional[str] = None,
        mail_class: Optional[str] = None,
        weight: Optional[float] = None,
        weight_units: Optional[str] = None,
        length: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        dimension_units: Optional[str] = None,
        shipping_label_cost: Optional[float] = None,
        shipping_label_currency: Optional[str] = None,
        revenue_eligibility: Optional[str] = None,
        ship_from_country: Optional[str] = None,
        ship_to_country: Optional[str] = None,
        incoterm: Optional[str] = None,
        customs_data: Optional[List[Dict[str, Any]]] = None,
        duty_amount: Optional[float] = None,
        duty_currency: Optional[str] = None,
        ship_date: Optional[str] = None,
    ):
        self.tracking_code = tracking_code
        self.carrier_name = carrier_name
        self.send_bcc = send_bcc
        self.note_to_buyer = note_to_buyer
        self.mail_class = mail_class
        self.weight = weight
        self.weight_units = weight_units
        self.length = length
        self.width = width
        self.height = height
        self.dimension_units = dimension_units
        self.shipping_label_cost = shipping_label_cost
        self.shipping_label_currency = shipping_label_currency
        self.revenue_eligibility = revenue_eligibility
        self.ship_from_country = ship_from_country
        self.ship_to_country = ship_to_country
        self.incoterm = incoterm
        self.customs_data = customs_data
        self.duty_amount = duty_amount
        self.duty_currency = duty_currency
        self.ship_date = ship_date

        super().__init__(
            nullable=CreateReceiptShipmentRequest.nullable,
            mandatory=CreateReceiptShipmentRequest.mandatory,
        )


class UpdateShopReceiptRequest(Request):
    nullable: List[str] = [
        "was_shipped",
        "was_paid",
    ]
    mandatory: List[str] = []

    def __init__(
        self,
        was_shipped: Optional[bool] = None,
        was_paid: Optional[bool] = None,
    ):
        self.was_shipped = was_shipped
        self.was_paid = was_paid

        super().__init__(
            nullable=UpdateShopReceiptRequest.nullable,
            mandatory=UpdateShopReceiptRequest.mandatory,
        )
