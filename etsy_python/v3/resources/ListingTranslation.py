from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Listing import (
    CreateListingTranslationRequest,
    UpdateListingTranslationRequest,
)
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method
from etsy_python.v3.resources.Response import Response


@dataclass
class ListingTranslationResource:
    session: EtsyClient

    def create_listing_translation(
        self,
        shop_id: int,
        listing_id: int,
        language: str,
        listing_translation: CreateListingTranslationRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/translations/{language}"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=listing_translation
        )

    def get_listing_translation(
        self, shop_id: int, listing_id: int, language: str
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/translations/{language}"
        return self.session.make_request(endpoint)

    def update_listing_translation(
        self,
        shop_id: int,
        listing_id: int,
        language: str,
        listing_translation: UpdateListingTranslationRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/translations/{language}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=listing_translation
        )
