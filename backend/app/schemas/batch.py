from pydantic import BaseModel
from datetime import date

class BatchBase(BaseModel):
    batch_no: str
    expiry_date: date
    purchase_price: float
    selling_price: float
    quantity: int
    medicine_id: int


class BatchCreateSchema(BatchBase):
    pass


class BatchUpdateSchema(BaseModel):
    batch_no: str | None = None
    expiry_date: date | None = None
    purchase_price: float | None = None
    selling_price: float | None = None
    quantity: int | None = None


class BatchResponse(BaseModel):
    id: int
    batch_no: str
    expiry_date: date
    purchase_price: float
    selling_price: float
    quantity: int
    medicine_id: int

    class Config:
        from_attributes = True
