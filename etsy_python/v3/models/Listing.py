from typing import List, Optional, Dict, Any

from v3.enums.Listing import (
    WhoMade,
    WhenMade,
    SortOn,
    SortOrder,
    Includes,
    ItemWeightUnit,
    ItemDimensionsUnit,
    Type,
    State,
)
from v3.models.Product import Product
from v3.models.Request import Request
from v3.models.FileRequest import FileRequest


class CreateDraftListingRequest(Request):
    nullable = [
        "shipping_profile_id",
        "materials",
        "shop_section_id",
        "processing_min",
        "processing_max",
        "tags",
        "styles",
        "item_weight",
        "item_length",
        "item_width",
        "item_height",
        "item_weight_unit",
        "item_dimensions_unit",
        "production_partner_ids",
        "image_ids",
    ]
    mandatory = [
        "quantity",
        "title",
        "description",
        "price",
        "who_made",
        "when_made",
        "taxonomy_id",
    ]

    def __init__(
        self,
        quantity: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        who_made: Optional[WhoMade] = None,
        when_made: Optional[WhenMade] = None,
        taxonomy_id: Optional[int] = None,
        shipping_profile_id: Optional[int] = None,
        materials: Optional[List[str]] = None,
        shop_section_id: Optional[int] = None,
        processing_min: Optional[int] = None,
        processing_max: Optional[int] = None,
        tags: Optional[List[str]] = None,
        styles: Optional[List[str]] = None,
        item_weight: Optional[float] = None,
        item_length: Optional[float] = None,
        item_width: Optional[float] = None,
        item_height: Optional[float] = None,
        item_weight_unit: Optional[ItemWeightUnit] = None,
        item_dimensions_unit: Optional[ItemDimensionsUnit] = None,
        is_personalizable: Optional[bool] = None,
        personalization_is_required: Optional[bool] = None,
        personalization_char_count_max: Optional[int] = None,
        personalization_instructions: Optional[str] = None,
        production_partner_ids: Optional[int] = None,
        image_ids: Optional[List[int]] = None,
        is_supply: Optional[bool] = None,
        is_customizable: Optional[bool] = None,
        should_auto_renew: Optional[bool] = None,
        is_taxable: Optional[bool] = None,
        listing_type: Optional[Type] = None,
    ):
        self.quantity = quantity
        self.title = title
        self.description = description
        self.price = price
        self.who_made = who_made
        self.when_made = when_made
        self.taxonomy_id = taxonomy_id
        self.shipping_profile_id = shipping_profile_id
        self.materials = materials
        self.shop_section_id = shop_section_id
        self.processing_min = processing_min
        self.processing_max = processing_max
        self.tags = tags
        self.styles = styles
        self.item_weight = item_weight
        self.item_length = item_length
        self.item_width = item_width
        self.item_height = item_height
        self.item_weight_unit = item_weight_unit
        self.item_dimensions_unit = item_dimensions_unit
        self.is_personalizable = is_personalizable
        self.personalization_is_required = personalization_is_required
        self.personalization_char_count_max = personalization_char_count_max
        self.personalization_instructions = personalization_instructions
        self.production_partner_ids = production_partner_ids
        self.image_ids = image_ids
        self.is_supply = is_supply
        self.is_customizable = is_customizable
        self.should_auto_renew = should_auto_renew
        self.is_taxable = is_taxable
        self.listing_type = listing_type
        super().__init__(
            nullable=CreateDraftListingRequest.nullable,
            mandatory=CreateDraftListingRequest.mandatory,
        )


class UpdateListingRequest(Request):
    nullable: List[str] = [
        "materials",
        "shipping_profile_id",
        "shop_section_id",
        "item_weight",
        "item_length",
        "item_width",
        "item_height",
        "item_weight_unit",
        "item_dimensions_unit",
        "tags",
        "featured_rank",
        "production_partner_ids",
        "type",
    ]

    mandatory: List[str] = []

    def __init__(
        self,
        image_ids: Optional[List[str]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        materials: Optional[List[str]] = None,
        should_auto_renew: Optional[bool] = None,
        shipping_profile_id: Optional[int] = None,
        shop_section_id: Optional[int] = None,
        item_weight: Optional[float] = None,
        item_length: Optional[float] = None,
        item_width: Optional[float] = None,
        item_height: Optional[float] = None,
        item_weight_unit: Optional[ItemWeightUnit] = None,
        item_dimensions_unit: Optional[ItemDimensionsUnit] = None,
        is_taxable: Optional[bool] = None,
        taxonomy_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        who_made: Optional[WhoMade] = None,
        when_made: Optional[WhenMade] = None,
        featured_rank: Optional[int] = None,
        is_personalizable: Optional[bool] = None,
        personalization_is_required: Optional[bool] = None,
        personalization_char_count_max: Optional[int] = None,
        personalization_instructions: Optional[str] = None,
        state: Optional[State] = None,
        is_supply: Optional[bool] = None,
        production_partner_ids: Optional[List[int]] = None,
        listing_type: Optional[Type] = None,
    ):
        self.image_ids = image_ids
        self.title = title
        self.description = description
        self.materials = materials
        self.should_auto_renew = should_auto_renew
        self.shipping_profile_id = shipping_profile_id
        self.shop_section_id = shop_section_id
        self.item_weight = item_weight
        self.item_length = item_length
        self.item_width = item_width
        self.item_height = item_height
        self.item_weight_unit = item_weight_unit
        self.item_dimensions_unit = item_dimensions_unit
        self.is_taxable = is_taxable
        self.taxonomy_id = taxonomy_id
        self.tags = tags
        self.who_made = who_made
        self.when_made = when_made
        self.featured_rank = featured_rank
        self.is_personalizable = is_personalizable
        self.personalization_is_required = personalization_is_required
        self.personalization_char_count_max = personalization_char_count_max
        self.personalization_instructions = personalization_instructions
        self.state = state
        self.is_supply = is_supply
        self.production_partner_ids = production_partner_ids
        self.listing_type = listing_type
        super().__init__(nullable=UpdateListingRequest.nullable)


class UpdateListingInventoryRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = ["products"]

    def __init__(
        self,
        products: List[Product],
        price_on_property: Optional[List[int]] = None,
        quantity_on_property: Optional[List[int]] = None,
        sku_on_property: Optional[List[int]] = None,
    ):
        self.products = products
        self.price_on_property = price_on_property
        self.quantity_on_property = quantity_on_property
        self.sku_on_property = sku_on_property
        super().__init__(
            nullable=UpdateListingInventoryRequest.nullable,
            mandatory=UpdateListingInventoryRequest.mandatory,
        )

    @staticmethod
    def generate_request_from_inventory_response(
        response: Dict[str, Any]
    ) -> UpdateListingInventoryRequest:
        products = []
        for product in response["products"]:
            property_values = product["property_values"]
            for prop_val in property_values:
                prop_val.pop("scale_name", None)
                prop_val.pop("value_pairs", None)
            offerings = product["offerings"]
            for offering in offerings:
                offering.pop("is_deleted", None)
                offering.pop("offering_id", None)
                offering["price"] = (
                    offering["price"]["amount"] / offering["price"]["divisor"]
                )
            products.append(Product(product["sku"], property_values, offerings))
        price_on_property = response["price_on_property"]
        quantity_on_property = response["quantity_on_property"]
        sku_on_property = response["sku_on_property"]
        return UpdateListingInventoryRequest(
            products, price_on_property, quantity_on_property, sku_on_property
        )


class UpdateListingPropertyRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = [
        "value_ids",
        "values",
    ]

    def __init__(
        self,
        value_ids: Optional[List[int]] = None,
        values: Optional[List[str]] = None,
        scale_id: Optional[int] = None,
    ):
        self.value_ids = value_ids
        self.values = values
        self.scale_id = scale_id
        super().__init__(
            nullable=UpdateListingPropertyRequest.nullable,
            mandatory=UpdateListingPropertyRequest.mandatory,
        )


class UploadListingImageRequest(FileRequest):
    nullable: List[str] = ["file"]
    mandatory: List[str] = []

    def __init__(
        self,
        image_bytes: bytes,
        listing_image_id: Optional[int] = None,
        rank: Optional[int] = None,
        overwrite: Optional[bool] = None,
        is_watermarked: Optional[bool] = None,
        alt_text: Optional[str] = None,
    ) -> None:
        self.file = {"image": image_bytes}
        self.data = {
            "listing_image_id": listing_image_id,
            "rank": rank,
            "overwrite": overwrite,
            "is_watermarked": is_watermarked,
            "alt_text": alt_text,
        }

        super().__init__(
            nullable=UploadListingImageRequest.nullable,
            mandatory=UploadListingImageRequest.mandatory,
        )


class UploadListingFileRequest(FileRequest):
    nullable: List[str] = ["file"]
    mandatory: List[str] = []

    def __init__(
        self,
        file_bytes: bytes,
        listing_file_id: Optional[int] = None,
        name: Optional[str] = None,
        rank: Optional[int] = None,
    ) -> None:
        self.file = {"file": (name, file_bytes, "multipart/form-data")}
        self.data = {"listing_file_id": listing_file_id, "rank": rank, "name": name}

        super().__init__(
            nullable=UploadListingFileRequest.nullable,
            mandatory=UploadListingFileRequest.mandatory,
        )


class UpdateVariationImagesRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = []

    def __init__(self, variation_images: List[Dict[str, Any]]) -> None:
        self.variation_images = variation_images
        super().__init__(
            nullable=UpdateVariationImagesRequest.nullable,
            mandatory=UpdateVariationImagesRequest.mandatory,
        )

    @staticmethod
    def generate_request_from_variation_images_response(
        response: Dict[str, Any]
    ) -> UpdateVariationImagesRequest:
        variation_images = response["results"]
        for variation_image in variation_images:
            variation_image.pop("value", None)
        return UpdateVariationImagesRequest(variation_images)


class CreateListingTranslationRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = [
        "title",
        "description",
    ]

    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        self.title = title
        self.description = description
        self.tags = tags
        super().__init__(
            nullable=CreateListingTranslationRequest.nullable,
            mandatory=CreateListingTranslationRequest.mandatory,
        )


class UpdateListingTranslationRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = [
        "title",
        "description",
    ]

    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        self.title = title
        self.description = description
        self.tags = tags

        super().__init__(
            nullable=UpdateListingTranslationRequest.nullable,
            mandatory=UpdateListingTranslationRequest.mandatory,
        )


class UpdateListingVideoRequest(FileRequest):
    nullable: List[str] = ["file"]
    mandatory: List[str] = []

    def __init__(
        self,
        video_id: Optional[int] = None,
        video_bytes: Optional[bytes] = None,
        name: Optional[str] = None,
    ) -> None:
        self.file = {"video": video_bytes}
        self.data = {"video_id": video_id, "name": name}

        super().__init__(
            nullable=UpdateListingVideoRequest.nullable,
            mandatory=UpdateListingVideoRequest.mandatory,
        )
