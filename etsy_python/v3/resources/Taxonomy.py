from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient


@dataclass
class BuyerTaxonomyResource:
    session: EtsyClient

    def get_buyer_taxonomy_nodes(self) -> Union[Response, RequestException]:
        endpoint = "/buyer-taxonomy/nodes"
        return self.session.make_request(endpoint)

    def get_properties_by_buyer_taxonomy_id(
        self, taxonomy_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/buyer-taxonomy/nodes/{taxonomy_id}/properties"
        return self.session.make_request(endpoint)


@dataclass
class SellerTaxonomyResource:
    session: EtsyClient

    def get_seller_taxonomy_nodes(self) -> Union[Response, RequestException]:
        endpoint = "/seller-taxonomy/nodes"
        return self.session.make_request(endpoint)

    def get_properties_by_taxonomy_id(
        self, taxonomy_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/seller-taxonomy/nodes/{taxonomy_id}/properties"
        return self.session.make_request(endpoint)
