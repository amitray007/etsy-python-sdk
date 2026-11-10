from typing import Any, Dict, List, Optional, Sequence, Union

from etsy_python.v3.common.Utils import Clear
from etsy_python.v3.models.Request import Request

#: Every body field of createShopEconomicOperator and updateShopEconomicOperator.
OPERATOR_FIELDS = (
    "operator_name",
    "email",
    "first_line",
    "second_line",
    "city",
    "state",
    "zip",
    "country_iso",
    "phone",
    "phone_country_iso",
    "trademark_name",
)

#: Required on create, and never blank: Etsy rejects a blank value on update too.
NON_BLANK_FIELDS = (
    "operator_name",
    "email",
    "first_line",
    "city",
    "zip",
    "country_iso",
    "phone",
)


class _ShopEconomicOperatorRequest(Request):
    def _store_operator_fields(
        self, values: Dict[str, Any], non_blank: Sequence[str]
    ) -> None:
        self._assign_fields(OPERATOR_FIELDS, values)
        blank = [
            name
            for name in non_blank
            if isinstance(values[name], str) and not values[name].strip()
        ]
        if blank:
            raise ValueError("cannot be blank: " + ", ".join(blank))


class CreateShopEconomicOperatorRequest(_ShopEconomicOperatorRequest):
    # A new record has nothing to clear, so every field rejects a blank value.
    nullable: List[str] = []
    # A literal list, not list(NON_BLANK_FIELDS): scripts/audit_sdk.py reads it
    # from the source.
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
        # Etsy requires state for some countries (e.g. US, CA, AU) and rejects
        # the request server-side when it is missing.
        self._store_operator_fields(
            {
                "operator_name": operator_name,
                "email": email,
                "first_line": first_line,
                "second_line": second_line,
                "city": city,
                "state": state,
                "zip": zip,
                "country_iso": country_iso,
                "phone": phone,
                "phone_country_iso": phone_country_iso,
                "trademark_name": trademark_name,
            },
            non_blank=OPERATOR_FIELDS,
        )
        super().__init__(
            nullable=CreateShopEconomicOperatorRequest.nullable,
            mandatory=CreateShopEconomicOperatorRequest.mandatory,
        )


class UpdateShopEconomicOperatorRequest(_ShopEconomicOperatorRequest):
    # Pass CLEAR for one of these to send null and clear the stored value.
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
        second_line: Union[str, Clear, None] = None,
        city: Optional[str] = None,
        state: Union[str, Clear, None] = None,
        zip: Optional[str] = None,
        country_iso: Optional[str] = None,
        phone: Optional[str] = None,
        phone_country_iso: Union[str, Clear, None] = None,
        trademark_name: Union[str, Clear, None] = None,
    ) -> None:
        self._store_operator_fields(
            {
                "operator_name": operator_name,
                "email": email,
                "first_line": first_line,
                "second_line": second_line,
                "city": city,
                "state": state,
                "zip": zip,
                "country_iso": country_iso,
                "phone": phone,
                "phone_country_iso": phone_country_iso,
                "trademark_name": trademark_name,
            },
            non_blank=NON_BLANK_FIELDS,
        )
        super().__init__(
            nullable=UpdateShopEconomicOperatorRequest.nullable,
            mandatory=UpdateShopEconomicOperatorRequest.mandatory,
        )
