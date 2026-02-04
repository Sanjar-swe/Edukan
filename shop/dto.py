from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class OrderCheckoutDTO:
    user_id: int
    cart_item_ids: List[int]
    address: str
