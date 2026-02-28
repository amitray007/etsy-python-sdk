from unittest.mock import MagicMock

from etsy_python.v3.models.Listing import UploadListingImageRequest
from etsy_python.v3.resources.ListingImage import ListingImageResource
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.enums.Request import Method

from tests.conftest import MOCK_LISTING_ID, MOCK_LISTING_IMAGE_ID, MOCK_SHOP_ID
from tests.fixtures.responses import make_collection, make_listing_image


class TestGetListingImages:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(
            200, make_collection(make_listing_image)
        )
        resource = ListingImageResource(session=mock_session)

        result = resource.get_listing_images(MOCK_LISTING_ID)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/listings/{MOCK_LISTING_ID}/images"
        )


class TestGetListingImage:
    def test_basic_call(self, mock_session):
        mock_session.make_request.return_value = Response(200, make_listing_image())
        resource = ListingImageResource(session=mock_session)

        result = resource.get_listing_image(MOCK_LISTING_ID, MOCK_LISTING_IMAGE_ID)

        assert result.code == 200
        mock_session.make_request.assert_called_once_with(
            f"/listings/{MOCK_LISTING_ID}/images/{MOCK_LISTING_IMAGE_ID}"
        )


class TestUploadListingImage:
    def test_calls_post_with_payload(self, mock_session):
        mock_session.make_request.return_value = Response(201, make_listing_image())
        resource = ListingImageResource(session=mock_session)
        payload = MagicMock(spec=UploadListingImageRequest)

        result = resource.upload_listing_image(MOCK_SHOP_ID, MOCK_LISTING_ID, payload)

        assert result.code == 201
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/images",
            method=Method.POST,
            payload=payload,
        )


class TestDeleteListingImage:
    def test_calls_delete(self, mock_session):
        mock_session.make_request.return_value = Response(204, "OK")
        resource = ListingImageResource(session=mock_session)

        result = resource.delete_listing_image(
            MOCK_SHOP_ID, MOCK_LISTING_ID, MOCK_LISTING_IMAGE_ID
        )

        assert result.code == 204
        mock_session.make_request.assert_called_once_with(
            f"/shops/{MOCK_SHOP_ID}/listings/{MOCK_LISTING_ID}/images/{MOCK_LISTING_IMAGE_ID}",
            method=Method.DELETE,
        )
