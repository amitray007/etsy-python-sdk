from typing import Optional, List, Any

from etsy_python.v3.common.Utils import todict


class Request:
    def __init__(
        self,
        nullable: Optional[List[str]] = None,
        mandatory: Optional[List[str]] = None,
    ):
        self._nullable = nullable if nullable is not None else []
        self._mandatory = mandatory if mandatory is not None else []
        if not self.check_mandatory():
            raise ValueError

    def check_mandatory(self) -> bool:
        if self._mandatory is not None:
            for key in self._mandatory:
                try:
                    if self.__dict__[key] is None:
                        return False
                except Exception:
                    return False
        return True

    def get_nulled(self) -> List[str]:
        return [
            key
            for key, value in self.__dict__.items()
            if key in self._nullable and (value == [] or value == "" or value == 0)
        ]

    def get_dict(self) -> Any:
        nulled = self.get_nulled()
        return todict(self, nullable=nulled)
