from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union

from v3.enums.Listing import Includes, State, SortOn, SortOrder
from v3.exceptions.RequestException import RequestException
from v3.models.Listing import CreateDraftListingRequest
from v3.resources.enums.Request import Method
from v3.resources.Session import EtsyClient
from v3.resources.Response import Response


@dataclass
class ListingResource:
    session: EtsyClient

    def create_draft_listing(
        self, shop_id: int, listing: CreateDraftListingRequest
    ) -> Union[Response, RequestException]:
        uri = f"/shops/{shop_id}/listings"
        return self.session.make_request(
            uri, method=Method.POST, request_payload=listing
        )

    def get_listings_by_shop(
        self,
        shop_id: int,
        state: Optional[State] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_on: Optional[SortOn] = None,
        sort_order: Optional[SortOrder] = None,
        includes: Optional[List[Includes]] = None,
    ) -> Union[Response, RequestException]:
        uri = f"/shops/{shop_id}/listings"
        kwargs: Dict[str, Any] = {
            "state": state.value if state is not None else None,
            "limit": limit,
            "offset": offset,
            "sort_on": sort_on.value if sort_on is not None else None,
            "sort_order": sort_order.value if sort_order is not None else None,
            "includes": ",".join([x.value for x in includes])
            if includes is not None
            else None,
        }
        return self.session.make_request(uri, **kwargs)

    def delete_listing(self, listing_id: int) -> Union[Response, RequestException]:
        uri = f"/listings/{listing_id}"
        return self.session.make_request(uri, method=Method.DELETE)

    def get_listing(
        self, listing_id: int, includes: Optional[List[Includes]] = None
    ) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}"
        includes_string = (
            ",".join(list(map(lambda inc: inc.value, includes))) if includes else None
        )
        kwargs: Dict[str, Any] = {"includes": includes_string}
        return self.session.make_request(endpoint, **kwargs)
