from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.Response import Response


@dataclass
class ListingOfferingResource:
    session: EtsyClient

    def get_listing_offering(
        self, listing_id: int, product_id: int, product_offering_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}/products/{product_id}/offerings/{product_offering_id}"
        return self.session.make_request(endpoint)
