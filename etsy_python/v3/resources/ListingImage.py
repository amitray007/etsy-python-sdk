from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Listing import UploadListingImageRequest
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method
from etsy_python.v3.resources.Response import Response


@dataclass
class ListingImageResource:
    session: EtsyClient

    def delete_listing_image(
        self, shop_id: int, listing_id: int, listing_image_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/images/{listing_image_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def get_listing_image(
        self, listing_id: int, listing_image_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}/images/{listing_image_id}"
        return self.session.make_request(endpoint)

    def get_listing_images(self, listing_id: int) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}/images"
        return self.session.make_request(endpoint)

    def upload_listing_image(
        self, shop_id: int, listing_id: int, listing_image: UploadListingImageRequest
    ) -> Union[Response, RequestException]:
        endpoint = f"shops/{shop_id}/listings/{listing_id}/images"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=listing_image
        )
