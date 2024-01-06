from enum import Enum
from typing import Any, Dict, List, Optional


def generate_get_uri(uri: str, **kwargs: Dict[str, Any]) -> str:
    if kwargs == {} or kwargs is None:
        return uri
    params = "&".join(
        [f"{key}={value}" for key, value in kwargs.items() if value is not None]
    )
    uri = f"{uri}?{params}" if params != "" else uri
    return uri


def todict(
    obj: Any, classkey: Optional[str] = None, nullable: Optional[List[str]] = None
) -> Any:
    if nullable is None:
        nullable = []
    if isinstance(obj, dict):
        data = {}
        for k, v in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif Enum in obj.__class__.__mro__:
        return todict(obj.value)
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict(
            [
                ("type" if key == "_type" else key, todict(value, classkey))
                if key not in nullable and value not in [[], "" or 0]
                else (key, None)
                for key, value in obj.__dict__.items()
                if not callable(value) and not key.startswith("_") and value is not None
            ]
        )
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


def generate_bytes_from_file(file: str) -> bytes:
    with open(file, "rb") as f:
        f_bytes = f.read()
    return f_bytes
