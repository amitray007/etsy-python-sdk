from unittest.mock import MagicMock

from etsy_python.v3.models.Listing import (
    CreateListingTranslationRequest,
    UpdateListingTranslationRequest,
    UpdateListingInventoryRequest,
    UpdateListingVideoRequest,
    UpdateVariationImagesRequest,
    UploadListingFileRequest,
)
from etsy_python.v3.models.Miscellaneous import GetTokenScopes
from etsy_python.v3.models.Shop import (
    CreateShopSectionRequest,
    UpdateShopSectionRequest,
)
from etsy_python.v3.models.ShopReturnPolicy import (
    ConsolidateShopReturnPoliciesRequest,
    CreateShopReturnPolicyRequest,
    UpdateShopReturnPolicyRequest,
)
from etsy_python.v3.models.HolidayPreferences import UpdateHolidayPreferencesRequest
from etsy_python.v3.resources.HolidayPreferences import HolidayPreferencesResource
from etsy_python.v3.resources.ListingFile import ListingFileResource
from etsy_python.v3.resources.ListingInventory import ListingInventoryResource
from etsy_python.v3.resources.ListingOffering import ListingOfferingResource
from etsy_python.v3.resources.ListingProduct import ListingProductResource
from etsy_python.v3.resources.ListingTranslation import ListingTranslationResource
from etsy_python.v3.resources.ListingVariationImages import (
    ListingVariationImagesResource,
)
from etsy_python.v3.resources.ListingVideo import ListingVideoResource
from etsy_python.v3.resources.Miscellaneous import MiscellaneousResource
from etsy_python.v3.resources.PaymentLedgerEntry import PaymentLedgeEntryResource
from etsy_python.v3.resources.ReceiptTransactions import ReceiptTransactionsResource
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Review import ReviewResource
from etsy_python.v3.resources.ShopProductionPartner import (
    ShopProductionPartnerResource,
)
from etsy_python.v3.resources.ShopReturnPolicy import ShopReturnPolicyResource
from etsy_python.v3.resources.ShopSection import ShopSectionResource
from etsy_python.v3.resources.Taxonomy import (
    BuyerTaxonomyResource,
    SellerTaxonomyResource,
)
from etsy_python.v3.resources.UserAddress import UserAddressResource
from etsy_python.v3.resources.enums.Request import Method

from tests.conftest import (
    MOCK_HOLIDAY_ID,
    MOCK_LEDGER_ENTRY_ID,
    MOCK_LISTING_FILE_ID,
    MOCK_LISTING_ID,
    MOCK_OFFERING_ID,
    MOCK_PRODUCT_ID,
    MOCK_RECEIPT_ID,
    MOCK_RETURN_POLICY_ID,
    MOCK_SECTION_ID,
    MOCK_SHOP_ID,
    MOCK_TAXONOMY_ID,
    MOCK_TRANSACTION_ID,
    MOCK_USER_ADDRESS_ID,
    MOCK_VIDEO_ID,
)
from tests.fixtures.responses import (
    make_collection,
    make_holiday_preference,
    make_ledger_entry,
    make_listing_file,
    make_listing_inventory,
    make_listing_offering,
    make_listing_product,
    make_listing_translation,
    make_listing_variation_images,
    make_listing_video,
    make_pong,
    make_production_partner,
    make_return_policy,
    make_review,
    make_shop_section,
    make_taxonomy_node,
    make_taxonomy_property,
    make_token_scopes,
    make_transaction,
    make_user_address,
)


# --- ListingFile ---
class TestListingFileResource:
    def test_get_all_listing_files(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_listing_file)
        )
        resource = ListingFileResource(session=mock_session)
        result = resource.get_all_listing_files(MOCK_SHOP_ID, MOCK_LISTING_ID)
        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/files"
        )

    def test_get_listing_file(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_listing_file())
        resource = ListingFileResource(session=mock_session)
        result = resource.get_listing_file(
            MOCK_SHOP_ID, MOCK_LISTING_ID, MOCK_LISTING_FILE_ID
        )
        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/files/{MOCK_LISTING_FILE_ID}"
        )

    def test_upload_listing_file(self, mock_session):
        mock_session.make_request.return_value = Response(201, make_listing_file())
        resource = ListingFileResource(session=mock_session)
        payload = MagicMock(spec=UploadListingFileRequest)
        resource.upload_listing_file(MOCK_SHOP_ID, MOCK_LISTING_ID, payload)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/files",
            method=Method.POST,
            payload=payload,
        )

    def test_delete_listing_file(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = ListingFileResource(session=mock_session)
        resource.delete_listing_file(
            MOCK_SHOP_ID, MOCK_LISTING_ID, MOCK_LISTING_FILE_ID
        )
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/files/{MOCK_LISTING_FILE_ID}",
            method=Method.DELETE,
        )


# --- ListingInventory ---
class TestListingInventoryResource:
    def test_get_listing_inventory(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_listing_inventory()
        )
        resource = ListingInventoryResource(session=mock_session)
        result = resource.get_listing_inventory(MOCK_LISTING_ID)
        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == f"/listings/{MOCK_LISTING_ID}/inventory"

    def test_update_listing_inventory(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_listing_inventory()
        )
        resource = ListingInventoryResource(session=mock_session)
        payload = MagicMock(spec=UpdateListingInventoryRequest)
        resource.update_listing_inventory(MOCK_LISTING_ID, payload)
        mock_session.make_request.assert_called_once_with(
            f"/listings/{MOCK_LISTING_ID}/inventory",
            method=Method.PUT,
            payload=payload,
            query_params={"legacy": None},
        )


# --- ListingVideo ---
class TestListingVideoResource:
    def test_get_listing_videos(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_listing_video)
        )
        resource = ListingVideoResource(session=mock_session)
        result = resource.get_listing_videos(MOCK_LISTING_ID)
        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/listings/{MOCK_LISTING_ID}/videos"
        )

    def test_get_listing_video(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_listing_video())
        resource = ListingVideoResource(session=mock_session)
        resource.get_listing_video(MOCK_VIDEO_ID, MOCK_LISTING_ID)
        mock_session.make_request.assert_called_once_with(
            f"/listings/{MOCK_LISTING_ID}/videos/{MOCK_VIDEO_ID}"
        )

    def test_upload_listing_video(self, mock_session):
        mock_session.make_request.return_value = Response(201, make_listing_video())
        resource = ListingVideoResource(session=mock_session)
        payload = MagicMock(spec=UpdateListingVideoRequest)
        resource.upload_listing_video(MOCK_SHOP_ID, MOCK_LISTING_ID, payload)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/videos",
            method=Method.POST,
            payload=payload,
        )

    def test_delete_listing_video(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = ListingVideoResource(session=mock_session)
        resource.delete_listing_video(MOCK_SHOP_ID, MOCK_LISTING_ID, MOCK_VIDEO_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/videos/{MOCK_VIDEO_ID}",
            method=Method.DELETE,
        )


# --- ListingTranslation ---
class TestListingTranslationResource:
    def test_get_listing_translation(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_listing_translation()
        )
        resource = ListingTranslationResource(session=mock_session)
        resource.get_listing_translation(MOCK_SHOP_ID, MOCK_LISTING_ID, "fr")
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/translations/fr"
        )

    def test_create_listing_translation(self, mock_session):
        mock_session.make_request.return_value = Response(
            201, make_listing_translation()
        )
        resource = ListingTranslationResource(session=mock_session)
        payload = MagicMock(spec=CreateListingTranslationRequest)
        resource.create_listing_translation(
            MOCK_SHOP_ID, MOCK_LISTING_ID, "fr", payload
        )
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/translations/fr",
            method=Method.POST,
            payload=payload,
        )

    def test_update_listing_translation(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_listing_translation()
        )
        resource = ListingTranslationResource(session=mock_session)
        payload = MagicMock(spec=UpdateListingTranslationRequest)
        resource.update_listing_translation(
            MOCK_SHOP_ID, MOCK_LISTING_ID, "fr", payload
        )
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/translations/fr",
            method=Method.PUT,
            payload=payload,
        )


# --- ListingVariationImages ---
class TestListingVariationImagesResource:
    def test_get_listing_variation_images(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_listing_variation_images()
        )
        resource = ListingVariationImagesResource(session=mock_session)
        resource.get_listing_variation_images(MOCK_SHOP_ID, MOCK_LISTING_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/variation-images"
        )

    def test_update_variation_images(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_listing_variation_images()
        )
        resource = ListingVariationImagesResource(session=mock_session)
        payload = MagicMock(spec=UpdateVariationImagesRequest)
        resource.update_variation_images(MOCK_SHOP_ID, MOCK_LISTING_ID, payload)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/variation-images",
            method=Method.POST,
            payload=payload,
        )


# --- ShopSection ---
class TestShopSectionResource:
    def test_get_shop_sections(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_shop_section)
        )
        resource = ShopSectionResource(session=mock_session)
        resource.get_shop_sections(MOCK_SHOP_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/sections"
        )

    def test_get_shop_section(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop_section())
        resource = ShopSectionResource(session=mock_session)
        resource.get_shop_section(MOCK_SHOP_ID, MOCK_SECTION_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/sections/{MOCK_SECTION_ID}"
        )

    def test_create_shop_section(self, mock_session):
        mock_session.make_request.return_value = Response(201, make_shop_section())
        resource = ShopSectionResource(session=mock_session)
        payload = MagicMock(spec=CreateShopSectionRequest)
        resource.create_shop_section(MOCK_SHOP_ID, payload)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/sections",
            method=Method.POST,
            payload=payload,
        )

    def test_update_shop_section(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop_section())
        resource = ShopSectionResource(session=mock_session)
        payload = MagicMock(spec=UpdateShopSectionRequest)
        resource.update_shop_section(MOCK_SHOP_ID, MOCK_SECTION_ID, payload)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/sections/{MOCK_SECTION_ID}",
            method=Method.PUT,
            payload=payload,
        )

    def test_delete_shop_section(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = ShopSectionResource(session=mock_session)
        resource.delete_shop_section(MOCK_SHOP_ID, MOCK_SECTION_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/sections/{MOCK_SECTION_ID}",
            method=Method.DELETE,
        )


# --- ShopReturnPolicy ---
class TestShopReturnPolicyResource:
    def test_get_shop_return_policies(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_return_policy)
        )
        resource = ShopReturnPolicyResource(session=mock_session)
        resource.get_shop_return_policies(MOCK_SHOP_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/policies/return"
        )

    def test_get_shop_return_policy(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_return_policy())
        resource = ShopReturnPolicyResource(session=mock_session)
        resource.get_shop_return_policy(MOCK_SHOP_ID, MOCK_RETURN_POLICY_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/policies/return/{MOCK_RETURN_POLICY_ID}"
        )

    def test_create_shop_return_policy(self, mock_session):
        mock_session.make_request.return_value = Response(201, make_return_policy())
        resource = ShopReturnPolicyResource(session=mock_session)
        payload = MagicMock(spec=CreateShopReturnPolicyRequest)
        resource.create_shop_return_policy(MOCK_SHOP_ID, payload)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/policies/return",
            method=Method.POST,
            payload=payload,
        )

    def test_update_shop_return_policy(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_return_policy())
        resource = ShopReturnPolicyResource(session=mock_session)
        payload = MagicMock(spec=UpdateShopReturnPolicyRequest)
        resource.update_shop_return_policy(
            MOCK_SHOP_ID, MOCK_RETURN_POLICY_ID, payload
        )
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/policies/return/{MOCK_RETURN_POLICY_ID}",
            method=Method.PUT,
            payload=payload,
        )

    def test_delete_shop_return_policy(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = ShopReturnPolicyResource(session=mock_session)
        resource.delete_shop_return_policy(MOCK_SHOP_ID, MOCK_RETURN_POLICY_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/policies/return/{MOCK_RETURN_POLICY_ID}",
            method=Method.DELETE,
        )

    def test_consolidate_shop_return_policies(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_return_policy())
        resource = ShopReturnPolicyResource(session=mock_session)
        payload = MagicMock(spec=ConsolidateShopReturnPoliciesRequest)
        resource.consolidate_shop_return_policies(MOCK_SHOP_ID, payload)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/policies/return/consolidate",
            method=Method.POST,
            payload=payload,
        )


# --- Review ---
class TestReviewResource:
    def test_get_reviews_by_listing(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_review)
        )
        resource = ReviewResource(session=mock_session)
        result = resource.get_reviews_by_listing(MOCK_LISTING_ID)
        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == f"/listings/{MOCK_LISTING_ID}/reviews"

    def test_get_reviews_by_shop(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_review)
        )
        resource = ReviewResource(session=mock_session)
        result = resource.get_reviews_by_shop(MOCK_SHOP_ID)
        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == f"/shops/{MOCK_SHOP_ID}/reviews"


# --- Taxonomy ---
class TestBuyerTaxonomyResource:
    def test_get_buyer_taxonomy_nodes(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_taxonomy_node)
        )
        resource = BuyerTaxonomyResource(session=mock_session)
        resource.get_buyer_taxonomy_nodes()
        mock_session.make_request.assert_called_once_with("/buyer-taxonomy/nodes")

    def test_get_properties_by_buyer_taxonomy_id(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_taxonomy_property)
        )
        resource = BuyerTaxonomyResource(session=mock_session)
        resource.get_properties_by_buyer_taxonomy_id(MOCK_TAXONOMY_ID)
        mock_session.make_request.assert_called_once_with(
            f"/buyer-taxonomy/nodes/{MOCK_TAXONOMY_ID}/properties"
        )


class TestSellerTaxonomyResource:
    def test_get_seller_taxonomy_nodes(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_taxonomy_node)
        )
        resource = SellerTaxonomyResource(session=mock_session)
        resource.get_seller_taxonomy_nodes()
        mock_session.make_request.assert_called_once_with("/seller-taxonomy/nodes")

    def test_get_properties_by_taxonomy_id(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_taxonomy_property)
        )
        resource = SellerTaxonomyResource(session=mock_session)
        resource.get_properties_by_taxonomy_id(MOCK_TAXONOMY_ID)
        mock_session.make_request.assert_called_once_with(
            f"/seller-taxonomy/nodes/{MOCK_TAXONOMY_ID}/properties"
        )


# --- Miscellaneous ---
class TestMiscellaneousResource:
    def test_ping(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_pong())
        resource = MiscellaneousResource(session=mock_session)
        result = resource.ping()
        assert result.code == 200
        mock_session.make_request.assert_called_once_with("/openapi-ping")

    def test_token_scopes(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_token_scopes())
        resource = MiscellaneousResource(session=mock_session)
        payload = MagicMock(spec=GetTokenScopes)
        resource.token_scopes(payload)
        mock_session.make_request.assert_called_once_with(
            "/scopes", method=Method.POST, payload=payload
        )


# --- ReceiptTransactions ---
class TestReceiptTransactionsResource:
    def test_get_shop_receipt_transactions_by_listing(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_transaction)
        )
        resource = ReceiptTransactionsResource(session=mock_session)
        resource.get_shop_receipt_transactions_by_listing(
            MOCK_SHOP_ID, MOCK_LISTING_ID
        )
        call_args = mock_session.make_request.call_args
        assert (
            call_args[0][0]
            == f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/transactions"
        )

    def test_get_shop_receipt_transactions_by_receipt(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_transaction)
        )
        resource = ReceiptTransactionsResource(session=mock_session)
        resource.get_shop_receipt_transactions_by_receipt(
            MOCK_SHOP_ID, MOCK_RECEIPT_ID
        )
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/receipts/{MOCK_RECEIPT_ID}/transactions",
            query_params={"legacy": None},
        )

    def test_get_shop_receipt_transaction(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_transaction())
        resource = ReceiptTransactionsResource(session=mock_session)
        resource.get_shop_receipt_transaction(MOCK_SHOP_ID, MOCK_TRANSACTION_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/transactions/{MOCK_TRANSACTION_ID}"
        )

    def test_get_shop_receipt_transaction_by_shop(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_transaction)
        )
        resource = ReceiptTransactionsResource(session=mock_session)
        resource.get_shop_receipt_transaction_by_shop(MOCK_SHOP_ID)
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == f"/shops/{MOCK_SHOP_ID}/transactions"


# --- PaymentLedgerEntry ---
class TestPaymentLedgeEntryResource:
    def test_get_shop_payment_account_ledger_entry(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_ledger_entry())
        resource = PaymentLedgeEntryResource(session=mock_session)
        resource.get_shop_payment_account_ledger_entry(
            MOCK_SHOP_ID, MOCK_LEDGER_ENTRY_ID
        )
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/payment-account/ledger-entries/{MOCK_LEDGER_ENTRY_ID}"
        )

    def test_get_shop_payment_account_ledger_entries(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_ledger_entry)
        )
        resource = PaymentLedgeEntryResource(session=mock_session)
        resource.get_shop_payment_account_ledger_entries(
            MOCK_SHOP_ID, min_created=1640000000, max_created=1641000000
        )
        call_args = mock_session.make_request.call_args
        assert (
            call_args[0][0]
            == f"/shops/{MOCK_SHOP_ID}/payment-account/ledger-entries"
        )
        qp = call_args[1]["query_params"]
        assert qp["min_created"] == 1640000000
        assert qp["max_created"] == 1641000000


# --- ShopProductionPartner ---
class TestShopProductionPartnerResource:
    def test_get_shop_production_partners(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_production_partner)
        )
        resource = ShopProductionPartnerResource(session=mock_session)
        resource.get_shop_production_partners(MOCK_SHOP_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/production-partners"
        )


# --- UserAddress ---
class TestUserAddressResource:
    def test_get_user_addresses(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_user_address)
        )
        resource = UserAddressResource(session=mock_session)
        resource.get_user_addresses()
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == "/user/addresses"

    def test_get_user_address(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_user_address())
        resource = UserAddressResource(session=mock_session)
        resource.get_user_address(MOCK_USER_ADDRESS_ID)
        mock_session.make_request.assert_called_once_with(
            f"/user/addresses/{MOCK_USER_ADDRESS_ID}"
        )

    def test_delete_user_address(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = UserAddressResource(session=mock_session)
        resource.delete_user_address(MOCK_USER_ADDRESS_ID)
        mock_session.make_request.assert_called_once_with(
            f"/user/addresses/{MOCK_USER_ADDRESS_ID}", method=Method.DELETE
        )


# --- HolidayPreferences ---
class TestHolidayPreferencesResource:
    def test_get_holiday_preferences(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_holiday_preference)
        )
        resource = HolidayPreferencesResource(session=mock_session)
        resource.get_holiday_preferences(MOCK_SHOP_ID)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/holiday-preferences"
        )

    def test_update_holiday_preferences(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_holiday_preference()
        )
        resource = HolidayPreferencesResource(session=mock_session)
        payload = MagicMock(spec=UpdateHolidayPreferencesRequest)
        resource.update_holiday_preferences(MOCK_SHOP_ID, MOCK_HOLIDAY_ID, payload)
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/holiday-preferences/{MOCK_HOLIDAY_ID}",
            method=Method.PUT,
            payload=payload,
        )


# --- ListingOffering ---
class TestListingOfferingResource:
    def test_get_listing_offering(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_listing_offering())
        resource = ListingOfferingResource(session=mock_session)
        resource.get_listing_offering(MOCK_LISTING_ID, MOCK_PRODUCT_ID, MOCK_OFFERING_ID)
        mock_session.make_request.assert_called_once_with(
            f"/listings/{MOCK_LISTING_ID}/products/{MOCK_PRODUCT_ID}/offerings/{MOCK_OFFERING_ID}",
            query_params={"legacy": None},
        )


# --- ListingProduct ---
class TestListingProductResource:
    def test_get_listing_product(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_listing_product())
        resource = ListingProductResource(session=mock_session)
        resource.get_listing_product(MOCK_LISTING_ID, MOCK_PRODUCT_ID)
        mock_session.make_request.assert_called_once_with(
            f"/listings/{MOCK_LISTING_ID}/inventory/products/{MOCK_PRODUCT_ID}",
            query_params={"legacy": None},
        )
