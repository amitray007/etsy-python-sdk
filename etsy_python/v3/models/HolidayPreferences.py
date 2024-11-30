from typing import Optional

from etsy_python.v3.models.Request import Request

class UpdateHolidayPreferencesRequest(Request):
    nullable = [
    ]
    mandatory = [
        "is_working"
    ]

    def __init__(
        self,
        is_working: Optional[bool] = False,
    ):
        self.is_working = is_working
        super().__init__(
            nullable=UpdateHolidayPreferencesRequest.nullable,
            mandatory=UpdateHolidayPreferencesRequest.mandatory,
        )
