from pydantic import BaseModel, field_validator
from datetime import date

class BatchBase(BaseModel):
    batch_no: str
    expiry_date: date
    purchase_price: float
    selling_price: float
    quantity: int
    medicine_id: int

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, v):
        if v < date.today():
            raise ValueError("Expiry date cannot be in the past")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v

    @field_validator("purchase_price", "selling_price")
    @classmethod
    def validate_prices(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v


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
