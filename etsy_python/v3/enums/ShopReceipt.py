from enum import Enum


class SortOn(Enum):
    CREATED = "created"
    UPDATED = "updated"
    RECEIPT_ID = "receipt_id"


class SortOrder(Enum):
    ASC = "asc"
    ASCENDING = "ascending"
    DESC = "desc"
    DESCENDING = "descending"
    UP = "up"
    DOWN = "down"
