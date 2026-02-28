from dataclasses import dataclass
from typing import Optional, Union

from etsy_python.v3.enums.HolidayPreferences import CA_HOLIDAYS, HOLIDAYS, US_HOLIDAYS
from etsy_python.v3.models.HolidayPreferences import UpdateHolidayPreferencesRequest
from etsy_python.v3.resources.enums.Request import Method
from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Session import EtsyClient
from etsy_python.v3.resources.Response import Response


@dataclass
class HolidayPreferencesResource:
    session: EtsyClient

    def get_holiday_preferences(self, shop_id: int) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/holiday-preferences"
        return self.session.make_request(endpoint)

    def update_holiday_preferences(
        self,
        shop_id: int,
        holiday_id: Optional[Union[HOLIDAYS, US_HOLIDAYS, CA_HOLIDAYS, int]],
        holiday_preference: UpdateHolidayPreferencesRequest,
    ) -> Union[Response, RequestException]:
        endpoint = f"/shops/{shop_id}/holiday-preferences/{holiday_id}"
        return self.session.make_request(
            endpoint, method=Method.PUT, payload=holiday_preference
        )
