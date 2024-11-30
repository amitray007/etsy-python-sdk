from enum import Enum

"""
Reference:
Official Documentation: https://developer.etsy.com/documentation/tutorials/fulfillment/#country-holidays
"""

class HOLIDAYS(Enum):
    """
    # Note:
    1. More Holidays are pending to be added, as Etsy only supports US and CA holidays as of Release (3.0.0 General Release 2024-07-24).
    2. String values from "1" till "105" are supported by Etsy based on selected regions.
    """
    pass

class US_HOLIDAYS(Enum):
    NEW_YEARS_DAY = "1"
    MARTIN_LUTHER_KING_JR_DAY = "2"
    PRESIDENTS_DAY = "3"
    MEMORIAL_DAY = "4"
    JUNETEENTH = "5"
    INDEPENDENCE_DAY = "6"
    LABOR_DAY = "7"
    COLUMBUS_DAY = "8"
    VETERANS_DAY = "9"
    THANKSGIVING_DAY = "10"
    CHRISTMAS_DAY = "11"

class CA_HOLIDAYS(Enum):
    GOOD_FRIDAY = "12"
    EASTER = "13"
    VICTORIA_DAY = "14"
    CANADA_DAY = "15"
    TRUTH_AND_RECONCILIATION_DAY = "16"
    REMEMBRANCE_DAY = "17"
    CIVIC_HOLIDAY = "18"
    BOXING_DAY = "19"
    NEW_YEARS_DAY = "20"
    LABOR_DAY = "21"
    THANKSGIVING_DAY = "22"
    CHRISTMAS_DAY = "23"
