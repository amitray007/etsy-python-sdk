from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseAPIException(Exception):
    code: int
    error: str
    error_description: Optional[str] = None
    type: str = "ERROR"

    def __str__(self) -> str:
        return f"[code = {self.code}] [error = {self.error}] [error_description = {self.error_description}] [type = {self.type}]"
