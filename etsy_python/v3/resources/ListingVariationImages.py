from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Listing import UpdateVariationImagesRequest
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.enums.Request import Method


@dataclass
class ListingVariationImagesResource:
    session: EtsyClient

    def get_listing_variation_images(
        self, shop_id: int, listing_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/variation-images"
        return self.session.make_request(endpoint)

    def update_variation_images(
        self,
        shop_id: int,
        listing_id: int,
        listing_variation_image: UpdateVariationImagesRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/variation-images"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=listing_variation_image
        )
