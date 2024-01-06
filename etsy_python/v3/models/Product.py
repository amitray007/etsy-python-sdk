from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Product:
    sku: str
    property_values: List[Dict[str, Any]]
    offerings: List[Dict[str, Any]]
