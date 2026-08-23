from pydantic import BaseModel
from datetime import date, datetime
from typing import List

# Purchase Item Schema
class PurchaseItemCreate(BaseModel):
    medicine_id: int
    batch_no: str
    expiry_date: date
    purchase_price: float
    selling_price: float
    quantity: int

# Purchase Create Schema
class PurchaseCreate(BaseModel):
    invoice_number: str | None = None
    supplier_name: str | None = None
    purchase_date: date
    currency_code: str | None = "TZS"
    items: List[PurchaseItemCreate]


class PurchaseUpdate(BaseModel):
    supplier_name: str | None = None
    purchase_date: date | None = None
    currency_code: str | None = None

# Response Schemas
class PurchaseItemResponse(BaseModel):
    id: int
    medicine_id: int
    batch_no: str
    expiry_date: date
    purchase_price: float
    selling_price: float
    quantity: int

    class Config:
        from_attributes = True  


class PurchaseResponse(BaseModel):
    id: int
    invoice_number: str
    supplier_name: str | None
    purchase_date: date
    total_amount: float
    created_at: datetime | None
    items: List[PurchaseItemResponse]

    class Config:
        from_attributes = True
