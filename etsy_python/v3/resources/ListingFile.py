from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Listing import UploadListingFileRequest
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method
from etsy_python.v3.resources.Response import Response


@dataclass
class ListingFileResource:
    session: EtsyClient

    def delete_listing_file(
        self, shop_id: int, listing_id: int, listing_file_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/files/{listing_file_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def get_listing_file(
        self, shop_id: int, listing_id: int, listing_file_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/files/{listing_file_id}"
        return self.session.make_request(endpoint)

    def get_all_listing_files(
        self, shop_id: int, listing_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/files"
        return self.session.make_request(endpoint)

    def upload_listing_file(
        self, shop_id: int, listing_id: int, listing_file: UploadListingFileRequest
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/files"
        return self.session.make_request(
            endpoint, method=Method.POST, payload=listing_file
        )
