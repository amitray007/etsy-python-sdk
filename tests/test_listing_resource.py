from unittest.mock import MagicMock

import pytest

from etsy_python.v3.enums.Listing import (
    Includes,
    SortOn,
    SortOrder,
    State,
)
from etsy_python.v3.models.Listing import (
    CreateDraftListingRequest,
    UpdateListingPropertyRequest,
    UpdateListingRequest,
)
from etsy_python.v3.resources.Listing import ListingResource
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.enums.Request import Method

from tests.conftest import (
    MOCK_LISTING_ID,
    MOCK_PROPERTY_ID,
    MOCK_RECEIPT_ID,
    MOCK_RETURN_POLICY_ID,
    MOCK_SECTION_ID,
    MOCK_SHOP_ID,
)
from tests.fixtures.responses import make_shop_listing, make_shop_listing_collection


class TestCreateDraftListing:
    def test_calls_post_with_payload(self, mock_session):
        mock_session.make_request.return_value = Response(201, make_shop_listing())
        resource = ListingResource(session=mock_session)
        payload = MagicMock(spec=CreateDraftListingRequest)

        result = resource.create_draft_listing(MOCK_SHOP_ID, payload)

        assert result.code == 201
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings",
            method=Method.POST,
            payload=payload,
        )


class TestGetListingsByShop:
    def test_default_params(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        result = resource.get_listings_by_shop(MOCK_SHOP_ID)

        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == f"/shops/{MOCK_SHOP_ID}/listings"
        assert call_args[1]["state"] == State.ACTIVE.value
        assert call_args[1]["sort_on"] == SortOn.CREATED.value
        assert call_args[1]["sort_order"] == SortOrder.DESC.value

    def test_with_includes(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        resource.get_listings_by_shop(
            MOCK_SHOP_ID, includes=[Includes.IMAGES, Includes.SHOP]
        )

        call_kwargs = mock_session.make_request.call_args[1]
        assert call_kwargs["includes"] == "Images,Shop"

    def test_custom_state_and_sort(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        resource.get_listings_by_shop(
            MOCK_SHOP_ID,
            state=State.DRAFT,
            sort_on=SortOn.PRICE,
            sort_order=SortOrder.ASC,
        )

        call_kwargs = mock_session.make_request.call_args[1]
        assert call_kwargs["state"] == "draft"
        assert call_kwargs["sort_on"] == "price"
        assert call_kwargs["sort_order"] == "asc"


class TestDeleteListing:
    def test_calls_delete(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = ListingResource(session=mock_session)

        result = resource.delete_listing(MOCK_LISTING_ID)

        assert result.code == 204
        mock_session.make_request.assert_called_once_with(
            f"/listings/{MOCK_LISTING_ID}", method=Method.DELETE
        )


class TestGetListing:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop_listing())
        resource = ListingResource(session=mock_session)

        result = resource.get_listing(MOCK_LISTING_ID)

        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == f"/listings/{MOCK_LISTING_ID}"

    def test_with_includes_and_language(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop_listing())
        resource = ListingResource(session=mock_session)

        resource.get_listing(
            MOCK_LISTING_ID, includes=[Includes.IMAGES], language="fr"
        )

        call_kwargs = mock_session.make_request.call_args[1]
        assert call_kwargs["includes"] == "Images"
        assert call_kwargs["language"] == "fr"


class TestFindAllListingsActive:
    def test_default_params(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        result = resource.find_all_listings_active()

        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == "/listings/active"
        assert call_args[1]["limit"] == 25
        assert call_args[1]["offset"] == 0

    def test_with_keywords_and_price_range(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        resource.find_all_listings_active(
            keywords="ceramic mug", min_price=10.0, max_price=50.0
        )

        call_kwargs = mock_session.make_request.call_args[1]
        assert call_kwargs["keywords"] == "ceramic mug"
        assert call_kwargs["min_price"] == 10.0
        assert call_kwargs["max_price"] == 50.0


class TestFindAllActiveListingsByShop:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        result = resource.find_all_active_listings_by_shop(MOCK_SHOP_ID)

        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == f"/shops/{MOCK_SHOP_ID}/listings/active"


class TestGetListingsByListingsIds:
    def test_listing_ids_joined(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        resource.get_listings_by_listings_ids([111, 222, 333])

        call_kwargs = mock_session.make_request.call_args[1]
        assert call_kwargs["listing_ids"] == "111,222,333"


class TestGetFeaturedListingsByShop:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        result = resource.get_featured_listings_by_shop(MOCK_SHOP_ID)

        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert call_args[0][0] == f"/shops/{MOCK_SHOP_ID}/listings/featured"


class TestDeleteListingProperty:
    def test_calls_delete(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = ListingResource(session=mock_session)

        result = resource.delete_listing_property(
            MOCK_SHOP_ID, MOCK_LISTING_ID, MOCK_PROPERTY_ID
        )

        assert result.code == 204
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/properties/{MOCK_PROPERTY_ID}",
            method=Method.DELETE,
        )


class TestUpdateListingProperty:
    def test_calls_put_with_payload(self, mock_session):
        mock_session.make_request.return_value = Response(200, {})
        resource = ListingResource(session=mock_session)
        payload = MagicMock(spec=UpdateListingPropertyRequest)

        resource.update_listing_property(
            MOCK_SHOP_ID, MOCK_LISTING_ID, MOCK_PROPERTY_ID, payload
        )

        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/properties/{MOCK_PROPERTY_ID}",
            method=Method.PUT,
            payload=payload,
        )


class TestGetListingProperty:
    def test_raises_not_implemented(self, mock_session):
        resource = ListingResource(session=mock_session)
        with pytest.raises(NotImplementedError):
            resource.get_listing_property()


class TestGetListingProperties:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(200, {"results": []})
        resource = ListingResource(session=mock_session)

        result = resource.get_listing_properties(MOCK_SHOP_ID, MOCK_LISTING_ID)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/properties"
        )


class TestUpdateListing:
    def test_calls_patch_with_payload(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_shop_listing())
        resource = ListingResource(session=mock_session)
        payload = MagicMock(spec=UpdateListingRequest)

        resource.update_listing(MOCK_SHOP_ID, MOCK_LISTING_ID, payload)

        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}",
            method=Method.PATCH,
            payload=payload,
        )


class TestGetListingsByShopReceipt:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        result = resource.get_listings_by_shop_receipt(MOCK_SHOP_ID, MOCK_RECEIPT_ID)

        assert result.code == 200
        call_args = mock_session.make_request.call_args
        assert (
            call_args[0][0]
            == f"/shops/{MOCK_SHOP_ID}/receipts/{MOCK_RECEIPT_ID}/listings"
        )


class TestGetListingsByShopReturnPolicy:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        result = resource.get_listings_by_shop_return_policy(
            MOCK_SHOP_ID, MOCK_RETURN_POLICY_ID
        )

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/policies/return/{MOCK_RETURN_POLICY_ID}/listings"
        )


class TestGetListingsByShopSectionId:
    def test_with_section_ids(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        resource.get_listings_by_shop_section_id(
            MOCK_SHOP_ID, shop_section_ids=[111, 222]
        )

        call_kwargs = mock_session.make_request.call_args[1]
        assert call_kwargs["shop_section_ids"] == "111,222"

    def test_without_section_ids(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        resource.get_listings_by_shop_section_id(MOCK_SHOP_ID)

        call_kwargs = mock_session.make_request.call_args[1]
        assert call_kwargs["shop_section_ids"] is None
