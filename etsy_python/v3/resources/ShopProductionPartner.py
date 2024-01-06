from dataclasses import dataclass
from typing import Union

from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Response import Response
from etsy_python.v3.resources.Session import EtsyClient


@dataclass
class ShopProductionPartnerResource:
    session: EtsyClient

    def get_shop_production_partners(
        self, shop_id: int
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/production-partners"
        return self.session.make_request(endpoint)
