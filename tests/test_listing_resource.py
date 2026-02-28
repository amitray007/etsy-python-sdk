from unittest.mock import MagicMock

import pytest

from etsy_python.v3.enums.Listing import (
    Includes,
    SortOn,
    SortOrder,
    State,
)
from etsy_python.v3.exceptions.RequestException import RequestException
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
            query_params={"legacy": None},
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
        qp = call_args[1]["query_params"]
        assert qp["state"] == State.ACTIVE.value
        assert qp["sort_on"] == SortOn.CREATED.value
        assert qp["sort_order"] == SortOrder.DESC.value

    def test_with_includes(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        resource.get_listings_by_shop(
            MOCK_SHOP_ID, includes=[Includes.IMAGES, Includes.SHOP]
        )

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp["includes"] == "Images,Shop"

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

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp["state"] == "draft"
        assert qp["sort_on"] == "price"
        assert qp["sort_order"] == "asc"


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

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp["includes"] == "Images"
        assert qp["language"] == "fr"


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
        qp = call_args[1]["query_params"]
        assert qp["limit"] == 25
        assert qp["offset"] == 0

    def test_with_keywords_and_price_range(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        resource.find_all_listings_active(
            keywords="ceramic mug", min_price=10.0, max_price=50.0
        )

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp["keywords"] == "ceramic mug"
        assert qp["min_price"] == 10.0
        assert qp["max_price"] == 50.0


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

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp["listing_ids"] == "111,222,333"


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
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(200, {"property_id": 513})
        resource = ListingResource(session=mock_session)
        result = resource.get_listing_property(11111, 513)
        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            "/listings/11111/properties/513"
        )


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
            query_params={"legacy": None},
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
            f"/shops/{MOCK_SHOP_ID}/policies/return/{MOCK_RETURN_POLICY_ID}/listings",
            query_params={"legacy": None},
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

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp["shop_section_ids"] == "111,222"

    def test_without_section_ids(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        resource.get_listings_by_shop_section_id(MOCK_SHOP_ID)

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp["shop_section_ids"] is None


class TestErrorPropagation:
    def test_request_exception_propagates(self, mock_session):
        """Resource methods must not swallow RequestException from make_request."""
        mock_session.make_request.side_effect = RequestException(
            code=404, error="Not Found"
        )
        resource = ListingResource(session=mock_session)

        with pytest.raises(RequestException) as exc_info:
            resource.get_listing(MOCK_LISTING_ID)
        assert exc_info.value.code == 404


class TestResponseDataValidation:
    def test_create_draft_listing_returns_listing_data(self, mock_session):
        listing_data = make_shop_listing()
        mock_session.make_request.return_value = Response(201, listing_data)
        resource = ListingResource(session=mock_session)
        payload = MagicMock(spec=CreateDraftListingRequest)

        result = resource.create_draft_listing(MOCK_SHOP_ID, payload)

        assert result.code == 201
        assert result.message["listing_id"] == listing_data["listing_id"]
        assert result.message["title"] == listing_data["title"]

    def test_get_listings_by_shop_returns_collection(self, mock_session):
        collection = make_shop_listing_collection()
        mock_session.make_request.return_value = Response(200, collection)
        resource = ListingResource(session=mock_session)

        result = resource.get_listings_by_shop(MOCK_SHOP_ID)

        assert result.message["count"] == collection["count"]
        assert len(result.message["results"]) == len(collection["results"])


class TestNoneOptionalParams:
    def test_none_optional_params_excluded_from_query_params(self, mock_session):
        """Optional params passed as None should appear in query_params (filtered by generate_get_uri)."""
        mock_session.make_request.return_value = Response(
            200, make_shop_listing_collection()
        )
        resource = ListingResource(session=mock_session)

        resource.find_all_listings_active(keywords=None, min_price=None)

        qp = mock_session.make_request.call_args[1]["query_params"]
        assert qp["keywords"] is None
        assert qp["min_price"] is None
