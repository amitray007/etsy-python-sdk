from dataclasses import dataclass
from typing import Optional, Dict, Any, Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.enums.Listing import InventoryIncludes
from etsy_python.v3.models.Listing import UpdateListingInventoryRequest
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.enums.Request import Method
from etsy_python.v3.resources.Response import Response


@dataclass
class ListingInventoryResource:
    session: EtsyClient

    def get_listing_inventory(
        self,
        listing_id: int,
        show_deleted: bool = False,
        includes: Optional[InventoryIncludes] = None,
        legacy: Optional[bool] = None,
    ) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}/inventory"
        query_params: Dict[str, Any] = {
            "show_deleted": show_deleted,
            "includes": includes.value if includes is not None else None,
            "legacy": legacy,
        }
        return self.session.make_request(endpoint, query_params=query_params)

    def update_listing_inventory(
        self, listing_id: int, listing_inventory: UpdateListingInventoryRequest,
        legacy: Optional[bool] = None,
    ) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}/inventory"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=listing_inventory,
            query_params={"legacy": legacy},
        )
