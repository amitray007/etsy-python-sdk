from dataclasses import dataclass
from typing import Any

from v3.resources.Session import EtsyClient


@dataclass
class BuyerTaxonomy:
    session: EtsyClient

    def get_buyer_taxonomy_nodes(self) -> Any:
        uri = "/buyer-taxonomy/nodes"
        return self.session.make_request(uri)

    def get_properties_by_buyer_taxonomy_id(self, taxonomy_id: int) -> Any:
        uri = f"/buyer-taxonomy/nodes/{taxonomy_id}/properties"
        return self.session.make_request(uri)


@dataclass
class SellerTaxonomy:
    session: EtsyClient

    def get_seller_taxonomy_nodes(self) -> Any:
        uri = "/seller-taxonomy/nodes"
        return self.session.make_request(uri)

    def get_properties_by_taxonomy_id(self, taxonomy_id: int) -> Any:
        uri = f"/seller-taxonomy/nodes/{taxonomy_id}/properties"
        return self.session.make_request(uri)
