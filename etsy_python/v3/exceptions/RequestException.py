from dataclasses import dataclass
from typing import Any

from etsy_python.v3.exceptions.BaseAPIException import BaseAPIException


@dataclass
class RequestException(BaseAPIException):
    rate_limits: Any = None

    def __str__(self) -> str:
        return f"[EtsyRequestException] {super().__str__()}"
