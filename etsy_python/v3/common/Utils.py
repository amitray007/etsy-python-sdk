import warnings
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional


class Clear:
    """Type of ``CLEAR``. Use the ``CLEAR`` instance, not this class."""

    def __repr__(self) -> str:
        return "CLEAR"

    # Copies and pickle round trips (task queues, multiprocessing) must stay
    # the module singleton; an identity check would miss a fresh instance.
    def __copy__(self) -> "Clear":
        return self

    def __deepcopy__(self, memo: Dict[int, Any]) -> "Clear":
        return self

    def __reduce__(self) -> str:
        return "CLEAR"


#: Pass as the value of a nullable request field to send ``null`` and clear the
#: stored value. On most older models ``""``, ``[]`` and ``0`` (but not
#: ``False``) do the same for backward compatibility, and their type hints do
#: not list ``Clear`` yet. Fields added since ``CLEAR`` accept it in their hints.
CLEAR = Clear()


def is_null_value(value: Any) -> bool:
    """True for the values a nullable request field sends as JSON ``null``."""
    return (
        isinstance(value, Clear)
        or value == []
        or value == ""
        or (value == 0 and not isinstance(value, bool))
    )


def warn_removed_legacy_param(operation_id: str) -> None:
    """Warn that `legacy` was removed from an operation and is no longer sent.

    Etsy dropped the `legacy` query parameter from the listing endpoints without
    a deprecation period. The keyword argument is kept so existing callers don't
    break, but the value is not forwarded. Note `legacy` is still valid on other
    operations (receipts, transactions, getListingsByListingIds), which keep it.

    Called whenever ``legacy`` is passed explicitly — including ``legacy=False``.
    That is deliberate: ``legacy=False`` previously sent ``?legacy=false`` on the
    wire, so silently dropping it is a request-shape change the caller should
    know about, not just a no-op.
    """
    warnings.warn(
        f"'legacy' was removed from {operation_id} by Etsy and is no longer "
        "sent (any explicit value, including False, is discarded); it will be "
        "dropped from this method in a future major version.",
        DeprecationWarning,
        stacklevel=3,
    )


def join_ids(name: str, ids: Iterable[Any]) -> str:
    """Join a required list of IDs into Etsy's comma-separated query value.

    Raises ``TypeError`` for a string (iterating it would split the ID into
    characters) and ``ValueError`` when no IDs are given, so a request Etsy
    would reject is caught before it is sent.
    """
    if isinstance(ids, (str, bytes)):
        raise TypeError(f"{name} must be a list of IDs, not a string")
    joined = ",".join(map(str, ids)) if ids is not None else ""
    if not joined:
        raise ValueError(f"{name} is required and must contain at least one ID")
    return joined


def generate_get_uri(uri: str, params: Optional[Dict[str, Any]] = None) -> str:
    if not params:
        return uri
    formatted = "&".join(
        f"{key}={str(value).lower() if isinstance(value, bool) else value}"
        for key, value in params.items()
        if value is not None
    )
    return f"{uri}?{formatted}" if formatted else uri


def todict(
    obj: Any, classkey: Optional[str] = None, nullable: Optional[List[str]] = None
) -> Any:
    """Serialize ``obj`` for the API.

    A key in ``nullable`` is sent as ``null`` only when its value is a null
    value (``is_null_value``); a real value is kept. External callers may pass a
    model's full nullable list, so this check must stay value-safe.
    """
    if nullable is None:
        nullable = []
    if isinstance(obj, dict):
        data = {}
        for k, v in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif Enum in obj.__class__.__mro__:
        return todict(obj.value)
    elif isinstance(obj, Clear):
        return None
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict(
            [
                # _type -> "type": avoids shadowing Python's builtin in model attrs
                (
                    "type" if key == "_type" else key,
                    None
                    if key in nullable and is_null_value(value)
                    else todict(value, classkey),
                )
                for key, value in obj.__dict__.items()
                if not callable(value)
                and (not key.startswith("_") or key == "_type")
                and value is not None
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
