from pydantic import BaseModel
from typing import Optional
from datetime import date


class ExpiredActionCreate(BaseModel):
    action_type: str  # quarantine, dispose, return
    medicine_id: Optional[int] = None
    medicine_name: Optional[str] = None
    batch_no: Optional[str] = None
    batch_id: Optional[int] = None
    quantity: int
    expiry_date: Optional[date] = None
    reason: Optional[str] = None
    responsible_person: Optional[str] = None
    notes: Optional[str] = None


class ExpiredActionResponse(BaseModel):
    id: int
    action_type: str
    medicine_name: Optional[str]
    batch_no: Optional[str]
    quantity: int
    expiry_date: Optional[date]
    reason: Optional[str]
    responsible_person: Optional[str]
    notes: Optional[str]
    created_at: str

    class Config:
        from_attributes = True
