from typing import List, Optional

from etsy_python.v3.enums.ShippingProfile import DestinationRegion, ProcessingTimeUnit, Type
from etsy_python.v3.models.Request import Request


class CreateShopShippingProfileRequest(Request):
    nullable: List[str] = [
        "destination_country_iso",
        "mail_class",
        "min_delivery_days",
        "max_delivery_days",
    ]
    mandatory: List[str] = [
        "title",
        "origin_country_iso",
        "primary_cost",
        "secondary_cost",
        "min_processing_time",
        "max_processing_time",
    ]

    def __init__(
        self,
        title: Optional[str] = None,
        origin_country_iso: Optional[str] = None,
        primary_cost: Optional[float] = None,
        secondary_cost: Optional[float] = None,
        min_processing_time: Optional[int] = None,
        max_processing_time: Optional[int] = None,
        processing_time_unit: ProcessingTimeUnit = ProcessingTimeUnit.BUSINESS_DAYS,
        destination_country_iso: Optional[str] = None,
        destination_region: DestinationRegion = DestinationRegion.NONE,
        origin_postal_code: str = "",
        shipping_carrier_id: int = 0,
        mail_class: Optional[str] = None,
        min_delivery_days: Optional[int] = None,
        max_delivery_days: Optional[int] = None,
    ):
        self.title = title
        self.origin_country_iso = origin_country_iso
        self.primary_cost = primary_cost
        self.secondary_cost = secondary_cost
        self.min_processing_time = min_processing_time
        self.max_processing_time = max_processing_time
        self.processing_time_unit = processing_time_unit.value
        self.destination_country_iso = destination_country_iso
        self.destination_region = destination_region.value
        self.origin_postal_code = origin_postal_code
        self.shipping_carrier_id = shipping_carrier_id
        self.mail_class = mail_class
        self.min_delivery_days = min_delivery_days
        self.max_delivery_days = max_delivery_days

        super().__init__(
            nullable=CreateShopShippingProfileRequest.nullable,
            mandatory=CreateShopShippingProfileRequest.mandatory,
        )


class UpdateShopShippingProfileRequest(Request):
    nullable: List[str] = [
        "origin_postal_code",
    ]
    mandatory: List[str] = []

    def __init__(
        self,
        title: Optional[str] = None,
        origin_country_iso: Optional[str] = None,
        min_processing_time: Optional[int] = None,
        max_processing_time: Optional[int] = None,
        processing_time_unit: ProcessingTimeUnit = ProcessingTimeUnit.BUSINESS_DAYS,
        origin_postal_code: Optional[str] = None,
    ) -> None:
        self.title = title
        self.origin_country_iso = origin_country_iso
        self.min_processing_time = min_processing_time
        self.max_processing_time = max_processing_time
        self.processing_time_unit = processing_time_unit.value
        self.origin_postal_code = origin_postal_code

        super().__init__(
            nullable=UpdateShopShippingProfileRequest.nullable,
            mandatory=UpdateShopShippingProfileRequest.mandatory,
        )


class CreateShopShippingProfileDestinationRequest(Request):
    nullable: List[str] = [
        "destination_country_iso",
        "mail_class",
        "min_delivery_days",
        "max_delivery_days",
    ]
    mandatory: List[str] = [
        "primary_cost",
        "secondary_cost",
    ]

    def __init__(
        self,
        primary_cost: Optional[float] = None,
        secondary_cost: Optional[float] = None,
        destination_country_iso: Optional[str] = None,
        destination_region: DestinationRegion = DestinationRegion.NONE,
        shipping_carrier_id: int = 0,
        mail_class: Optional[str] = None,
        min_delivery_days: Optional[int] = None,
        max_delivery_days: Optional[int] = None,
    ):
        self.primary_cost = primary_cost
        self.secondary_cost = secondary_cost
        self.destination_country_iso = destination_country_iso
        self.destination_region = destination_region.value
        self.shipping_carrier_id = shipping_carrier_id
        self.mail_class = mail_class
        self.min_delivery_days = min_delivery_days
        self.max_delivery_days = max_delivery_days

        super().__init__(
            nullable=CreateShopShippingProfileDestinationRequest.nullable,
            mandatory=CreateShopShippingProfileDestinationRequest.mandatory,
        )


class UpdateShopShippingProfileDestinationRequest(Request):
    nullable: List[str] = [
        "primary_cost",
        "secondary_cost" "destination_country_iso",
        "shipping_carrier_id",
        "mail_class",
        "min_delivery_days",
        "max_delivery_days",
    ]
    mandatory: List[str] = []

    def __init__(
        self,
        primary_cost: Optional[float] = None,
        secondary_cost: Optional[float] = None,
        destination_country_iso: Optional[str] = None,
        destination_region: DestinationRegion = DestinationRegion.NONE,
        shipping_carrier_id: int = 0,
        mail_class: Optional[str] = None,
        min_delivery_days: Optional[int] = None,
        max_delivery_days: Optional[int] = None,
    ):
        self.primary_cost = primary_cost
        self.secondary_cost = secondary_cost
        self.destination_country_iso = destination_country_iso
        self.destination_region = destination_region.value
        self.shipping_carrier_id = shipping_carrier_id
        self.mail_class = mail_class
        self.min_delivery_days = min_delivery_days
        self.max_delivery_days = max_delivery_days

        super().__init__(
            nullable=CreateShopShippingProfileDestinationRequest.nullable,
            mandatory=CreateShopShippingProfileDestinationRequest.mandatory,
        )


class CreateShopShippingProfileUpgradeRequest(Request):
    nullable: List[str] = [
        "mail_class",
        "min_delivery_days",
        "max_delivery_days",
    ]
    mandatory: List[str] = [
        "type",
        "upgrade_name",
        "price",
        "secondary_price",
    ]

    def __init__(
        self,
        profile_type: Optional[Type] = None,
        upgrade_name: Optional[str] = None,
        price: Optional[float] = None,
        secondary_price: Optional[float] = None,
        shipping_carrier_id: int = 0,
        mail_class: Optional[str] = None,
        min_delivery_days: Optional[int] = None,
        max_delivery_days: Optional[int] = None,
    ) -> None:
        self._type = profile_type.value if profile_type else None
        self.upgrade_name = upgrade_name
        self.price = price
        self.secondary_price = secondary_price
        self.shipping_carrier_id = shipping_carrier_id
        self.mail_class = mail_class
        self.min_delivery_days = min_delivery_days
        self.max_delivery_days = max_delivery_days

        super().__init__(
            nullable=CreateShopShippingProfileUpgradeRequest.nullable,
            mandatory=CreateShopShippingProfileUpgradeRequest.mandatory,
        )


class UpdateShopShippingProfileUpgradeRequest(Request):
    nullable: List[str] = [
        "upgrade_name",
        "price",
        "secondary_price",
        "shipping_carrier_id" "mail_class",
        "min_delivery_days",
        "max_delivery_days",
    ]
    mandatory: List[str] = []

    def __init__(
        self,
        upgrade_name: Optional[str] = None,
        profile_type: Optional[Type] = None,
        price: Optional[float] = None,
        secondary_price: Optional[float] = None,
        shipping_carrier_id: int = 0,
        mail_class: Optional[str] = None,
        min_delivery_days: Optional[int] = None,
        max_delivery_days: Optional[int] = None,
    ) -> None:
        self.upgrade_name = upgrade_name
        self._type = profile_type.value if profile_type else None
        self.price = price
        self.secondary_price = secondary_price
        self.shipping_carrier_id = shipping_carrier_id
        self.mail_class = mail_class
        self.min_delivery_days = min_delivery_days
        self.max_delivery_days = max_delivery_days

        super().__init__(
            nullable=CreateShopShippingProfileUpgradeRequest.nullable,
            mandatory=CreateShopShippingProfileUpgradeRequest.mandatory,
        )
