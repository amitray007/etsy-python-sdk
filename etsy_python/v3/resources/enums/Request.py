from enum import Enum, auto as enum_auto


class Method(Enum):
    GET = enum_auto()
    POST = enum_auto()
    PUT = enum_auto()
    DELETE = enum_auto()
    PATCH = enum_auto()
