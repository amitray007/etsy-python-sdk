from typing import Any, List, Optional, Union

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

#: Required on create.
REQUIRED_FIELDS = (
    "operator_name",
    "email",
    "first_line",
    "city",
    "zip",
    "country_iso",
    "phone",
)


class _ShopEconomicOperatorRequest(Request):
    """Shared storage and validation. Clear a field with CLEAR, never ``""``."""

    def _store_operator_fields(self, **values: Any) -> None:
        self._assign_fields(OPERATOR_FIELDS, values)

    def validate(self) -> None:
        super().validate()
        blank = [
            name
            for name in OPERATOR_FIELDS
            if isinstance(getattr(self, name), str) and not getattr(self, name).strip()
        ]
        if blank:
            raise ValueError("cannot be blank: " + ", ".join(blank))


class CreateShopEconomicOperatorRequest(_ShopEconomicOperatorRequest):
    # A new record has nothing to clear.
    nullable: List[str] = []
    # A literal list, not list(REQUIRED_FIELDS): scripts/audit_sdk.py reads it
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
            operator_name=operator_name,
            email=email,
            first_line=first_line,
            second_line=second_line,
            city=city,
            state=state,
            zip=zip,
            country_iso=country_iso,
            phone=phone,
            phone_country_iso=phone_country_iso,
            trademark_name=trademark_name,
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

    def validate(self) -> None:
        super().validate()
        if all(getattr(self, name) is None for name in OPERATOR_FIELDS):
            raise ValueError("set at least one field to update")

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
            operator_name=operator_name,
            email=email,
            first_line=first_line,
            second_line=second_line,
            city=city,
            state=state,
            zip=zip,
            country_iso=country_iso,
            phone=phone,
            phone_country_iso=phone_country_iso,
            trademark_name=trademark_name,
        )
        super().__init__(
            nullable=UpdateShopEconomicOperatorRequest.nullable,
            mandatory=UpdateShopEconomicOperatorRequest.mandatory,
        )
