from dataclasses import dataclass
from typing import Any


@dataclass
class Response:
    code: int
    message: str
    rate_limits: Any = None

    def __str__(self) -> str:
        return f"[EtsyResponse] code = {self.code} message = {self.message}"
