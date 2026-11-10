from typing import List, Optional

from etsy_python.v3.models.Request import Request


class CreateShopEconomicOperatorRequest(Request):
    nullable: List[str] = ["phone_country_iso"]
    mandatory: List[str] = [
        "operator_name",
        "email",
        "first_line",
        "city",
        "zip",
        "country_iso",
        "phone",
    ]

    def __init__(
        self,
        operator_name: str,
        email: str,
        first_line: str,
        city: str,
        zip: str,
        country_iso: str,
        phone: str,
        second_line: Optional[str] = None,
        state: Optional[str] = None,
        phone_country_iso: Optional[str] = None,
        trademark_name: Optional[str] = None,
    ) -> None:
        self.operator_name = operator_name
        self.email = email
        self.first_line = first_line
        self.city = city
        self.zip = zip
        self.country_iso = country_iso
        self.phone = phone
        self.second_line = second_line
        # Etsy requires state for some countries (e.g. US, CA, AU) and rejects
        # the request server-side when it is missing.
        self.state = state
        self.phone_country_iso = phone_country_iso
        self.trademark_name = trademark_name

        super().__init__(
            nullable=CreateShopEconomicOperatorRequest.nullable,
            mandatory=CreateShopEconomicOperatorRequest.mandatory,
        )


class UpdateShopEconomicOperatorRequest(Request):
    # Pass "" for one of these to send null and clear the stored value.
    nullable: List[str] = [
        "second_line",
        "state",
        "phone_country_iso",
        "trademark_name",
    ]
    mandatory: List[str] = []

    def __init__(
        self,
        operator_name: Optional[str] = None,
        email: Optional[str] = None,
        first_line: Optional[str] = None,
        second_line: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip: Optional[str] = None,
        country_iso: Optional[str] = None,
        phone: Optional[str] = None,
        phone_country_iso: Optional[str] = None,
        trademark_name: Optional[str] = None,
    ) -> None:
        self.operator_name = operator_name
        self.email = email
        self.first_line = first_line
        self.second_line = second_line
        self.city = city
        self.state = state
        self.zip = zip
        self.country_iso = country_iso
        self.phone = phone
        self.phone_country_iso = phone_country_iso
        self.trademark_name = trademark_name

        super().__init__(
            nullable=UpdateShopEconomicOperatorRequest.nullable,
            mandatory=UpdateShopEconomicOperatorRequest.mandatory,
        )
