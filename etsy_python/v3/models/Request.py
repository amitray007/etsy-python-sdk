from typing import Any, Dict, List, Optional, Sequence

from etsy_python.v3.common.Utils import Clear, is_null_value, todict


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
        self._reject_clear_on_non_nullable()

    def check_mandatory(self) -> bool:
        # Keys must match the attribute name (e.g. "_type", not "type").
        if self._mandatory is not None:
            for key in self._mandatory:
                try:
                    if self.__dict__[key] is None:
                        return False
                except Exception:
                    return False
        return True

    def _reject_clear_on_non_nullable(self) -> None:
        misplaced = [
            key
            for key, value in self.__dict__.items()
            if isinstance(value, Clear) and key not in self._nullable
        ]
        if misplaced:
            raise ValueError(
                "CLEAR is only valid for nullable fields: " + ", ".join(misplaced)
            )

    def _assign_fields(self, names: Sequence[str], values: Dict[str, Any]) -> None:
        """Set each named field from ``values``, which must hold exactly ``names``."""
        if set(values) != set(names):
            raise TypeError(
                f"expected fields {sorted(names)}, got {sorted(values)}"
            )
        for name in names:
            setattr(self, name, values[name])

    def get_nulled(self) -> List[str]:
        return [
            key
            for key, value in self.__dict__.items()
            if key in self._nullable and is_null_value(value)
        ]

    def get_dict(self) -> Any:
        # Repeated here because a field can be set to CLEAR after construction.
        self._reject_clear_on_non_nullable()
        nulled = self.get_nulled()
        return todict(self, nullable=nulled)
