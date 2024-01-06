from dataclasses import dataclass
from typing import Union, Dict, Any, Optional

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.Response import Response


@dataclass
class ReviewResource:
    session: EtsyClient

    def get_reviews_by_listing(
        self,
        listing_id: int,
        limit: int = 25,
        offset: int = 0,
        min_created: Optional[int] = None,
        max_created: Optional[int] = None,
    ) -> Union[Response, RequestException]:
        endpoint = f"/listings/{listing_id}/reviews"
        kwargs: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "min_created": min_created,
            "max_created": max_created,
        }
        return self.session.make_request(endpoint, **kwargs)

    def get_reviews_by_shop(
        self,
        shop_id: int,
        limit: int = 25,
        offset: int = 0,
        min_created: Optional[int] = None,
        max_created: Optional[int] = None,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/reviews"
        kwargs: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "min_created": min_created,
            "max_created": max_created,
        }
        return self.session.make_request(endpoint, **kwargs)
