from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimit:
    limit_per_second: Optional[int]
    remaining_this_second: Optional[int]
    limit_per_day: Optional[int]
    remaining_today: Optional[int]
