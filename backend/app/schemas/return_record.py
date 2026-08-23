from pydantic import BaseModel
from typing import List


class ReturnItemCreate(BaseModel):
    sale_item_id: int | None = None
    medicine_id: int
    batch_id: int
    quantity: int
    unit_price: float
    condition: str = "good"


class ReturnCreate(BaseModel):
    sale_id: int
    reason: str | None = None
    items: List[ReturnItemCreate]
