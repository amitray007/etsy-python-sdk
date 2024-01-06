from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Listing import UpdateListingVideoRequest
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method


@dataclass
class ListingVideoResource:
    session: EtsyClient

    def delete_listing_video(
        self, shop_id: int, listing_id: int, video_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/videos/{video_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def get_listing_video(
        self, video_id: int, listing_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}/videos/{video_id}"
        return self.session.make_request(endpoint)

    def get_listing_videos(self, listing_id: int) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}/videos"
        return self.session.make_request(endpoint)

    def upload_listing_video(
        self, shop_id: int, listing_id: int, listing_video: UpdateListingVideoRequest
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/videos"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=listing_video
        )
