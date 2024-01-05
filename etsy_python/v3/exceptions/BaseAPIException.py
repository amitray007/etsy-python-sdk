from dataclasses import dataclass


@dataclass
class BaseAPIException(Exception):
    code: int
    message: str
    type: str = "ERROR"

    def __str__(self) -> str:
        return f"code = {self.code} message = {self.message} type = {self.type}"
