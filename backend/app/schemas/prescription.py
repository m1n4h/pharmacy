from pydantic import BaseModel, field_validator
from typing import List


class PrescriptionItemCreate(BaseModel):
    medicine_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v


class PrescriptionCreate(BaseModel):
    patient_name: str
    patient_age: int | None = None
    doctor_name: str | None = None
    notes: str | None = None
    items: List[PrescriptionItemCreate]

    @field_validator("patient_name")
    @classmethod
    def name_not_empty(cls, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Patient name is required")
        return v

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v):
        if not v:
            raise ValueError("Prescription must contain at least one item")
        return v


class PrescriptionUpdate(BaseModel):
    patient_name: str
    patient_age: int | None = None
    doctor_name: str | None = None
    notes: str | None = None
    items: List[PrescriptionItemCreate] | None = None

    @field_validator("patient_name")
    @classmethod
    def name_not_empty(cls, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Patient name is required")
        return v


class PrescriptionItemResponse(BaseModel):
    id: int
    medicine_id: int
    medicine_name: str
    quantity: int
    price: float

    class Config:
        from_attributes = True


class PrescriptionResponse(BaseModel):
    id: int
    prescription_no: str
    patient_name: str
    patient_age: int | None
    doctor_name: str | None
    notes: str | None
    status: str
    total_amount: float
    created_at: object | None
    dispensed_at: object | None
    items: List[PrescriptionItemResponse]

    class Config:
        from_attributes = True