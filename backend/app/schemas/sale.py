from pydantic import BaseModel
from datetime import date, datetime
from typing import List

class SaleItemCreate(BaseModel):
    medicine_id: int
    quantity: int


class SaleCreate(BaseModel):
    invoice_number: str | None = None
    customer_name: str | None = None
    sale_date: date | None = None
    discount_amount: float = 0
    items: List[SaleItemCreate]


class SaleUpdate(BaseModel):
    customer_name: str | None = None
    discount_amount: float | None = None


class SaleItemResponse(BaseModel):
    id: int
    medicine_id: int
    batch_id: int
    quantity: int
    selling_price: float

    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    customer_name: str | None
    sale_date: date
    subtotal: float
    discount_amount: float
    total_amount: float
    created_at: datetime | None
    items: List[SaleItemResponse]

    class Config:
        from_attributes = True
