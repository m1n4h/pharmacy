from pydantic import BaseModel
from datetime import date, datetime
from typing import List

class SaleItemCreate(BaseModel):
    medicine_id: int
    quantity: int

    def model_post_init(self, __context):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")


class SaleCreate(BaseModel):
    invoice_number: str | None = None
    customer_name: str | None = None
    sale_date: date | None = None
    discount_amount: float = 0
    payment_method: str | None = "Cash"
    amount_paid: float | None = 0
    items: List[SaleItemCreate]

    def model_post_init(self, __context):
        if self.discount_amount < 0:
            raise ValueError("Discount cannot be negative")
        if self.amount_paid is not None and self.amount_paid < 0:
            raise ValueError("Amount paid cannot be negative")


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
