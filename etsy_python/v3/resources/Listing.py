from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union

from etsy_python.v3.enums.Listing import Includes, State, SortOn, SortOrder
from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.models.Listing import (
    CreateDraftListingRequest,
    UpdateListingPropertyRequest,
    UpdateListingRequest,
)
from etsy_python.v3.resources.enums.Request import Method
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.Response import Response


@dataclass
class ListingResource:
    session: EtsyClient

    def create_draft_listing(
        self, shop_id: int, listing: CreateDraftListingRequest
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings"
        return self.session.make_request(endpoint, method=Method.POST, payload=listing)

    def get_listings_by_shop(
        self,
        shop_id: int,
        state: State = State.ACTIVE,
        limit: Optional[int] = 25,
        offset: Optional[int] = 0,
        sort_on: SortOn = SortOn.CREATED,
        sort_order: SortOrder = SortOrder.DESC,
        includes: Optional[List[Includes]] = None,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings"
        kwargs: Dict[str, Any] = {
            "state": state.value,
            "limit": limit,
            "offset": offset,
            "sort_on": sort_on.value,
            "sort_order": sort_order.value,
            "includes": ",".join(list(map(lambda inc: inc.value, includes)))
            if includes is not None
            else None,
        }
        return self.session.make_request(endpoint, **kwargs)

    def delete_listing(self, listing_id: int) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def get_listing(
        self,
        listing_id: int,
        includes: Optional[List[Includes]] = None,
        language: Optional[str] = None,
    ) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}"
        kwargs: Dict[str, Any] = {
            "includes": ",".join(list(map(lambda inc: inc.value, includes)))
            if includes is not None
            else None,
            "language": language,
        }
        return self.session.make_request(endpoint, **kwargs)

    def find_all_listings_active(
        self,
        limit: int = 25,
        offset: int = 0,
        keywords: Optional[str] = None,
        sort_on: SortOn = SortOn.CREATED,
        sort_order: SortOrder = SortOrder.DESC,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        taxonomy_id: Optional[int] = None,
        shop_location: Optional[str] = None,
    ) -> Union[Response, RequestException]:
        endpoint = "/listings/active"
        kwargs: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "keywords": keywords,
            "sort_on": sort_on.value,
            "sort_order": sort_order.value,
            "min_price": min_price,
            "max_price": max_price,
            "taxonomy_id": taxonomy_id,
            "shop_location": shop_location,
        }
        return self.session.make_request(endpoint, **kwargs)

    def find_all_active_listings_by_shop(
        self,
        shop_id: int,
        limit: Optional[int] = 25,
        sort_on: SortOn = SortOn.CREATED,
        sort_order: SortOrder = SortOrder.DESC,
        offset: Optional[int] = 0,
        keywords: Optional[str] = None,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/active"
        kwargs: Dict[str, Any] = {
            "limit": limit,
            "sort_on": sort_on.value,
            "sort_order": sort_order.value,
            "offset": offset,
            "keywords": keywords,
        }
        return self.session.make_request(endpoint, **kwargs)

    def get_listings_by_listings_ids(
        self, listing_ids: List[int], includes: Optional[List[Includes]] = None
    ) -> Union[Response, RequestException]:
        endpoint = "/listings/batch"
        kwargs: Dict[str, Any] = {
            "listing_ids": ",".join(list(map(str, listing_ids))),
            "includes": ",".join(list(map(lambda inc: inc.value, includes)))
            if includes is not None
            else None,
        }
        return self.session.make_request(endpoint, **kwargs)

    def get_featured_listings_by_shop(
        self, shop_id: int, limit: int = 25, offset: int = 0
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/featured"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self.session.make_request(endpoint, **kwargs)

    def delete_listing_property(
        self, shop_id: int, listing_id: int, property_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/properties/{property_id}"
        return self.session.make_request(endpoint, method=Method.DELETE)

    def update_listing_property(
        self,
        shop_id: int,
        listing_id: int,
        property_id: int,
        listing_property: UpdateListingPropertyRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/properties/{property_id}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=listing_property
        )

    def get_listing_property(self):
        raise NotImplementedError

    def get_listing_properties(
        self, shop_id: int, listing_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}/properties"
        return self.session.make_request(endpoint)

    def update_listing(
        self, shop_id: int, listing_id: int, listing: UpdateListingRequest
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/listings/{listing_id}"
        return self.session.make_request(endpoint, method=Method.PATCH, payload=listing)

    def get_listings_by_shop_receipt(
        self, shop_id: int, receipt_id: int, limit: int = 25, offset: int = 0
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/receipts/{receipt_id}/listings"
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        return self.session.make_request(endpoint, **kwargs)

    def get_listings_by_shop_return_policy(
        self, shop_id: int, return_policy_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/policies/return/{return_policy_id}/listings"
        return self.session.make_request(endpoint)

    def get_listings_by_shop_section_id(
        self,
        shop_id: int,
        shop_section_ids: Optional[List[int]] = None,
        limit: int = 25,
        offset: int = 0,
        sort_on: SortOn = SortOn.CREATED,
        sort_order: SortOrder = SortOrder.DESC,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/shop-sections/listings"
        kwargs: Dict[str, Any] = {
            "shop_section_ids": ",".join(list(map(str, shop_section_ids)))
            if shop_section_ids is not None
            else None,
            "limit": limit,
            "offset": offset,
            "sort_on": sort_on.value,
            "sort_order": sort_order.value,
        }
        return self.session.make_request(endpoint, **kwargs)
