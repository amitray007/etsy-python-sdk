from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Offering:
    price: float
    quantity: int
    is_enabled: bool


@dataclass
class PropertyValues:
    property_id: int
    value_ids: List[int]
    values: List[str]
    property_name: Optional[str] = ""
    scale_id: Optional[int] = None


@dataclass
class VariationImage:
    property_id: int
    value_id: int
    image_id: int
