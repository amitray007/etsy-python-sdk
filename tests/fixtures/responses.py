"""Factory functions that return dicts matching Etsy OAS response schemas."""


def make_money(**overrides):
    data = {
        "amount": 1500,
        "divisor": 100,
        "currency_code": "USD",
    }
    data.update(overrides)
    return data


def make_shop(**overrides):
    data = {
        "shop_id": 98765,
        "user_id": 12345678,
        "shop_name": "TestShop",
        "create_date": 1609459200,
        "created_timestamp": 1609459200,
        "title": "My Test Shop",
        "announcement": "Welcome to my shop!",
        "currency_code": "USD",
        "is_vacation": False,
        "vacation_message": None,
        "sale_message": "Thanks for your purchase!",
        "digital_sale_message": "Thanks for your digital purchase!",
        "update_date": 1640995200,
        "updated_timestamp": 1640995200,
        "listing_active_count": 42,
        "digital_listing_count": 5,
        "login_name": "testshopowner",
        "accepts_custom_requests": True,
        "vacation_autoreply": None,
        "url": "https://www.etsy.com/shop/TestShop",
        "image_url_760x100": None,
        "num_favorers": 150,
        "languages": ["en-US"],
        "icon_url_fullxfull": None,
        "is_using_structured_policies": True,
        "has_onboarded_structured_policies": True,
        "include_dispute_form_link": False,
        "is_direct_checkout_onboarded": True,
        "is_etsy_payments_onboarded": True,
        "is_opted_in_to_buyer_promise": False,
        "is_calculated_eligible": True,
        "is_shop_us_based": True,
        "transaction_sold_count": 500,
        "shipping_from_country_iso": "US",
        "shop_location_country_iso": "US",
        "policy_welcome": None,
        "policy_payment": None,
        "policy_shipping": None,
        "policy_refunds": None,
        "policy_additional": None,
        "policy_seller_info": None,
        "policy_update_date": 1640995200,
        "policy_has_private_receipt_info": False,
        "has_unstructured_policies": False,
        "policy_privacy": None,
        "review_average": 4.8,
        "review_count": 100,
    }
    data.update(overrides)
    return data


def make_shop_listing(**overrides):
    data = {
        "listing_id": 11111,
        "user_id": 12345678,
        "shop_id": 98765,
        "title": "Handmade Ceramic Mug",
        "description": "A beautiful handmade ceramic mug.",
        "state": "active",
        "creation_timestamp": 1609459200,
        "created_timestamp": 1609459200,
        "ending_timestamp": 1640995200,
        "original_creation_timestamp": 1609459200,
        "last_modified_timestamp": 1640995200,
        "updated_timestamp": 1640995200,
        "state_timestamp": 1609459200,
        "quantity": 10,
        "shop_section_id": 77777,
        "featured_rank": 0,
        "url": "https://www.etsy.com/listing/11111",
        "num_favorers": 25,
        "non_taxable": False,
        "is_taxable": True,
        "is_customizable": False,
        "is_personalizable": False,
        "personalization_is_required": False,
        "personalization_char_count_max": None,
        "personalization_instructions": None,
        "listing_type": "physical",
        "tags": ["ceramic", "mug", "handmade"],
        "materials": ["ceramic", "glaze"],
        "processing_min": 3,
        "processing_max": 5,
        "who_made": "i_did",
        "when_made": "2020_2026",
        "is_supply": False,
        "item_weight": 12.0,
        "item_weight_unit": "oz",
        "item_length": 4.0,
        "item_width": 3.5,
        "item_height": 4.5,
        "item_dimensions_unit": "in",
        "is_private": False,
        "style": None,
        "file_data": None,
        "has_variations": False,
        "should_auto_renew": True,
        "language": "en-US",
        "price": make_money(amount=2500),
        "taxonomy_id": 30303,
        "shipping_profile": None,
        "views": 150,
        "production_partners": [],
        "skus": ["MUG-001"],
        "images": [],
        "videos": [],
        "inventory": None,
        "translations": None,
    }
    data.update(overrides)
    return data


def make_shop_listing_collection(count=2, **overrides):
    return {
        "count": count,
        "results": [make_shop_listing(**overrides) for _ in range(count)],
    }


def make_shop_receipt(**overrides):
    data = {
        "receipt_id": 22222,
        "receipt_type": 0,
        "seller_user_id": 12345678,
        "seller_email": "seller@example.com",
        "buyer_user_id": 87654321,
        "buyer_email": "buyer@example.com",
        "name": "Test Buyer",
        "first_line": "123 Main St",
        "second_line": None,
        "city": "Portland",
        "state": "OR",
        "zip": "97201",
        "status": "paid",
        "formatted_address": "123 Main St\nPortland, OR 97201",
        "country_iso": "US",
        "payment_method": "cc",
        "payment_email": "buyer@example.com",
        "message_from_payment": None,
        "message_from_seller": None,
        "message_from_buyer": "Please ship quickly!",
        "is_shipped": False,
        "is_paid": True,
        "create_timestamp": 1640995200,
        "created_timestamp": 1640995200,
        "update_timestamp": 1640995200,
        "updated_timestamp": 1640995200,
        "is_gift": False,
        "gift_message": "",
        "grandtotal": make_money(amount=3500),
        "subtotal": make_money(amount=2500),
        "total_price": make_money(amount=2500),
        "total_shipping_cost": make_money(amount=500),
        "total_tax_cost": make_money(amount=500),
        "total_vat_cost": make_money(amount=0),
        "discount_amt": make_money(amount=0),
        "gift_wrap_price": make_money(amount=0),
        "shipments": [],
        "transactions": [],
        "refunds": [],
    }
    data.update(overrides)
    return data


def make_shop_receipt_collection(count=2, **overrides):
    return {
        "count": count,
        "results": [make_shop_receipt(**overrides) for _ in range(count)],
    }


def make_user(**overrides):
    data = {
        "user_id": 12345678,
        "login_name": "testuser",
        "primary_email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "create_timestamp": 1609459200,
        "created_timestamp": 1609459200,
        "bio": "I make things.",
        "gender": "",
        "birth_month": 0,
        "birth_day": 0,
        "transaction_buy_count": 10,
        "transaction_sold_count": 500,
        "is_seller": True,
        "image_url_75x75": None,
    }
    data.update(overrides)
    return data


def make_payment(**overrides):
    data = {
        "payment_id": 10101,
        "buyer_user_id": 87654321,
        "shop_id": 98765,
        "receipt_id": 22222,
        "amount_gross": make_money(amount=3500),
        "amount_fees": make_money(amount=350),
        "amount_net": make_money(amount=3150),
        "posted_gross": make_money(amount=3500),
        "posted_fees": make_money(amount=350),
        "posted_net": make_money(amount=3150),
        "adjusted_gross": make_money(amount=3500),
        "adjusted_fees": make_money(amount=350),
        "adjusted_net": make_money(amount=3150),
        "currency": "USD",
        "shop_currency": "USD",
        "buyer_currency": "USD",
        "shipping_user_id": 87654321,
        "shipping_address_id": 90909,
        "billing_address_id": 90909,
        "status": "settled",
        "shipped_timestamp": 1640995200,
        "create_timestamp": 1640995200,
        "created_timestamp": 1640995200,
        "update_timestamp": 1640995200,
        "updated_timestamp": 1640995200,
        "payment_adjustments": [],
    }
    data.update(overrides)
    return data


def make_payment_collection(count=2, **overrides):
    return {
        "count": count,
        "results": [make_payment(**overrides) for _ in range(count)],
    }


def make_shipping_profile(**overrides):
    data = {
        "shipping_profile_id": 44444,
        "title": "Standard Shipping",
        "user_id": 12345678,
        "min_processing_days": 3,
        "max_processing_days": 5,
        "processing_days_display_label": "3-5 business days",
        "origin_country_iso": "US",
        "is_deleted": False,
        "shipping_profile_destinations": [],
        "shipping_profile_upgrades": [],
        "origin_postal_code": "97201",
        "profile_type": "manual",
        "domestic_handling_fee": 0.0,
        "international_handling_fee": 0.0,
    }
    data.update(overrides)
    return data


def make_shipping_profile_destination(**overrides):
    data = {
        "shipping_profile_destination_id": 55555,
        "shipping_profile_id": 44444,
        "origin_country_iso": "US",
        "destination_country_iso": "US",
        "destination_region": "none",
        "primary_cost": make_money(amount=500),
        "secondary_cost": make_money(amount=200),
        "shipping_carrier_id": 0,
        "mail_class": None,
        "min_delivery_days": 3,
        "max_delivery_days": 7,
    }
    data.update(overrides)
    return data


def make_shipping_profile_upgrade(**overrides):
    data = {
        "shipping_profile_id": 44444,
        "upgrade_id": 66666,
        "upgrade_name": "Priority Shipping",
        "type": "0",
        "rank": 0,
        "language": "en-US",
        "price": make_money(amount=1000),
        "secondary_price": make_money(amount=500),
        "shipping_carrier_id": 0,
        "mail_class": None,
        "min_delivery_days": 1,
        "max_delivery_days": 3,
    }
    data.update(overrides)
    return data


def make_shop_section(**overrides):
    data = {
        "shop_section_id": 77777,
        "title": "Mugs",
        "rank": 1,
        "user_id": 12345678,
        "active_listing_count": 10,
    }
    data.update(overrides)
    return data


def make_listing_image(**overrides):
    data = {
        "listing_id": 11111,
        "listing_image_id": 33333,
        "hex_code": "FFFFFF",
        "red": 255,
        "green": 255,
        "blue": 255,
        "hue": 0,
        "saturation": 0,
        "brightness": 100,
        "is_black_and_white": False,
        "creation_tsz": 1609459200,
        "created_timestamp": 1609459200,
        "rank": 1,
        "url_75x75": "https://i.etsystatic.com/test/75x75.jpg",
        "url_170x135": "https://i.etsystatic.com/test/170x135.jpg",
        "url_570xN": "https://i.etsystatic.com/test/570xN.jpg",
        "url_fullxfull": "https://i.etsystatic.com/test/fullxfull.jpg",
        "full_height": 1000,
        "full_width": 1000,
        "alt_text": "A ceramic mug",
    }
    data.update(overrides)
    return data


def make_listing_file(**overrides):
    data = {
        "listing_file_id": 50505,
        "listing_id": 11111,
        "rank": 1,
        "filename": "pattern.pdf",
        "filesize": "2.5 MB",
        "size_bytes": 2621440,
        "filetype": "application/pdf",
        "create_timestamp": 1609459200,
        "created_timestamp": 1609459200,
    }
    data.update(overrides)
    return data


def make_listing_video(**overrides):
    data = {
        "video_id": 60606,
        "height": 1080,
        "width": 1920,
        "thumbnail_url": "https://i.etsystatic.com/test/video_thumb.jpg",
        "video_url": "https://v.etsystatic.com/test/video.mp4",
        "video_state": "active",
    }
    data.update(overrides)
    return data


def make_listing_inventory(**overrides):
    data = {
        "products": [make_listing_product()],
        "price_on_property": [],
        "quantity_on_property": [],
        "sku_on_property": [],
        "listing": None,
    }
    data.update(overrides)
    return data


def make_listing_product(**overrides):
    data = {
        "product_id": 70707,
        "sku": "MUG-001",
        "is_deleted": False,
        "offerings": [make_listing_offering()],
        "property_values": [],
    }
    data.update(overrides)
    return data


def make_listing_offering(**overrides):
    data = {
        "offering_id": 80808,
        "quantity": 10,
        "is_enabled": True,
        "is_deleted": False,
        "price": make_money(amount=2500),
    }
    data.update(overrides)
    return data


def make_review(**overrides):
    data = {
        "shop_id": 98765,
        "listing_id": 11111,
        "transaction_id": 99999,
        "buyer_user_id": 87654321,
        "rating": 5,
        "review": "Beautiful mug, exactly as described!",
        "language": "en",
        "image_url_fullxfull": None,
        "create_timestamp": 1640995200,
        "created_timestamp": 1640995200,
        "update_timestamp": 1640995200,
        "updated_timestamp": 1640995200,
    }
    data.update(overrides)
    return data


def make_taxonomy_node(**overrides):
    data = {
        "id": 30303,
        "level": 1,
        "name": "Jewelry",
        "parent_id": None,
        "children": [],
        "full_path_taxonomy_ids": [30303],
    }
    data.update(overrides)
    return data


def make_taxonomy_property(**overrides):
    data = {
        "property_id": 40404,
        "name": "Material",
        "display_name": "Material",
        "scales": [],
        "is_required": False,
        "supports_attributes": True,
        "supports_variations": False,
        "is_multivalued": True,
        "max_values_allowed": None,
        "possible_values": [],
        "selected_values": [],
    }
    data.update(overrides)
    return data


def make_pong():
    return {"application_id": 12345}


def make_transaction(**overrides):
    data = {
        "transaction_id": 99999,
        "title": "Handmade Ceramic Mug",
        "description": "A beautiful handmade ceramic mug.",
        "seller_user_id": 12345678,
        "buyer_user_id": 87654321,
        "create_timestamp": 1640995200,
        "created_timestamp": 1640995200,
        "paid_timestamp": 1640995200,
        "shipped_timestamp": None,
        "quantity": 1,
        "listing_image_id": 33333,
        "receipt_id": 22222,
        "is_digital": False,
        "file_data": "",
        "listing_id": 11111,
        "sku": "MUG-001",
        "product_id": 70707,
        "transaction_type": "listing",
        "price": make_money(amount=2500),
        "shipping_cost": make_money(amount=500),
        "variations": [],
        "product_data": [],
        "shipping_profile_id": 44444,
        "min_processing_days": 3,
        "max_processing_days": 5,
        "shipping_method": None,
        "shipping_upgrade": None,
        "expected_ship_date": 1641600000,
        "buyer_coupon": 0,
        "shop_coupon": 0,
    }
    data.update(overrides)
    return data


def make_ledger_entry(**overrides):
    data = {
        "entry_id": 20202,
        "ledger_id": 30303,
        "sequence_number": 1,
        "amount": 2500,
        "currency": "USD",
        "description": "Sale",
        "balance": 10000,
        "create_date": 1640995200,
        "created_timestamp": 1640995200,
        "ledger_type": "sale",
    }
    data.update(overrides)
    return data


def make_return_policy(**overrides):
    data = {
        "return_policy_id": 88888,
        "shop_id": 98765,
        "accepts_returns": True,
        "accepts_exchanges": True,
        "return_deadline": 30,
    }
    data.update(overrides)
    return data


def make_listing_translation(**overrides):
    data = {
        "listing_id": 11111,
        "language": "fr",
        "title": "Tasse en ceramique faite a la main",
        "description": "Une belle tasse en ceramique faite a la main.",
        "tags": ["ceramique", "tasse"],
    }
    data.update(overrides)
    return data


def make_listing_variation_images(**overrides):
    data = {
        "count": 1,
        "results": [
            {
                "property_id": 40404,
                "value_id": 1,
                "value": "Blue",
                "image_id": 33333,
            }
        ],
    }
    data.update(overrides)
    return data


def make_production_partner(**overrides):
    data = {
        "production_partner_id": 12345,
        "partner_name": "Local Pottery Co.",
        "location": "Portland, OR",
    }
    data.update(overrides)
    return data


def make_user_address(**overrides):
    data = {
        "user_address_id": 90909,
        "user_id": 12345678,
        "name": "Test User",
        "first_line": "123 Main St",
        "second_line": None,
        "city": "Portland",
        "state": "OR",
        "zip": "97201",
        "iso_country_code": "US",
        "country_name": "United States",
        "is_default_shipping_address": True,
    }
    data.update(overrides)
    return data


def make_holiday_preference(**overrides):
    data = {
        "holiday_id": "thanksgiving",
        "holiday_name": "Thanksgiving",
        "is_working": False,
    }
    data.update(overrides)
    return data


def make_shipping_carrier(**overrides):
    data = {
        "shipping_carrier_id": 1,
        "name": "USPS",
        "domestic_classes": [
            {"mail_class_key": "usps_first_class", "name": "First Class"}
        ],
        "international_classes": [],
    }
    data.update(overrides)
    return data


def make_token_scopes(**overrides):
    data = {
        "scopes": ["listings_r", "listings_w", "transactions_r"],
    }
    data.update(overrides)
    return data


def make_collection(factory, count=2, **overrides):
    """Generic collection wrapper for any factory function."""
    return {
        "count": count,
        "results": [factory(**overrides) for _ in range(count)],
    }
