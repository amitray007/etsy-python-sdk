from enum import Enum


class ReadinessState(Enum):
    READY_TO_SHIP = "ready_to_ship"
    MADE_TO_ORDER = "made_to_order"


class ProcessingTimeUnit(Enum):
    DAYS = "days"
    WEEKS = "weeks"
