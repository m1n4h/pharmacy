from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date


class ExpenseCreate(BaseModel):
    category: str
    description: Optional[str] = None
    amount: float
    date: date
    payment_method: Optional[str] = "Cash"
    reference: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    category: str
    description: Optional[str]
    amount: float
    date: date
    payment_method: Optional[str]
    reference: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True
