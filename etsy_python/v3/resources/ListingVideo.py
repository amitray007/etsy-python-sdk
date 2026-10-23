import warnings
from dataclasses import dataclass
from typing import Optional, Union

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
        self,
        shop_id: int,
        listing_id: int,
        listing_video: UpdateListingVideoRequest,
        is_multi_video: Optional[bool] = None,
    ) -> Union[Response, RequestException]:
        """Upload a video to a listing.

        ``is_multi_video`` is deprecated: Etsy removed it from
        uploadListingVideo, so any value is discarded and not sent, and Etsy
        no longer documents whether an upload replaces an existing video. To
        replace one, remove it with ``delete_listing_video`` before uploading
        the new video. Etsy limits uploads to 10 per listing per day.
        """
        if is_multi_video is not None:
            warnings.warn(
                "'is_multi_video' was removed from uploadListingVideo by Etsy "
                "and is no longer sent; to replace a video, remove it with "
                "delete_listing_video first. The argument will be dropped from "
                "this method in a future major version.",
                DeprecationWarning,
                stacklevel=2,
            )
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/videos"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=listing_video
        )
