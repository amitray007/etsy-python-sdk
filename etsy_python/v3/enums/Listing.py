from enum import Enum


class WhoMade(Enum):
    I_DID = "i_did"
    SOMEONE_ELSE = "someone_else"
    COLLECTIVE = "collective"


class WhenMade(Enum):
    MADE_TO_ORDER = "made_to_order"
    TWENTY_TWENTIES = "2020_2024"
    TWENTY_TENS = "2010_2019"
    TWENTY_OH_FIVE_TO_NINE = "2005_2009"
    BEFORE_2005 = "before_2005"
    TWO_THOUSAND_TO_TWO = "2000_2004"
    NINETEEN_NINETIES = "1990s"
    NINETEEN_EIGHTIES = "1980s"
    NINETEEN_SEVENTIES = "1970s"
    NINETEEN_SIXTIES = "1960s"
    NINETEEN_FIFTIES = "1950s"
    NINETEEN_FORTIES = "1940s"
    NINETEEN_THIRTIES = "1930s"
    NINETEEN_TWENTIES = "1920s"
    NINETEEN_TENS = "1910s"
    NINETEEN_HUNDREDS = "1900s"
    EIGHTEEN_HUNDREDS = "1800s"
    SEVENTEEN_HUNDREDS = "1700s"
    BEFORE_1700 = "before_1700"


class ItemWeightUnit(Enum):
    OZ = "oz"
    LB = "lb"
    G = "g"
    KG = "kg"


class ItemDimensionsUnit(Enum):
    IN = "in"
    FT = "ft"
    CM = "cm"
    M = "m"
    MM = "mm"
    YD = "yd"
    INCHES = "inches"


class Type(Enum):
    PHYSICAL = "physical"
    DOWNLOAD = "download"
    BOTH = "both"


class State(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SOLD_OUT = "sold_out"
    DRAFT = "draft"
    EXPIRED = "expired"


class SortOn(Enum):
    CREATED = "created"
    PRICE = "price"
    UPDATED = "updated"
    SCORE = "score"


class SortOrder(Enum):
    ASC = "asc"
    ASCENDING = "ascending"
    DESC = "desc"
    DESCENDING = "descending"
    UP = "up"
    DOWN = "down"


class Includes(Enum):
    SHIPPING = "Shipping"
    IMAGES = "Images"
    SHOP = "Shop"
    USER = "User"
    TRANSLATIONS = "Translations"
    INVENTORY = "Inventory"
    VIDEOS = "Videos"


class InventoryIncludes(Enum):
    LISTING = "Listing"
