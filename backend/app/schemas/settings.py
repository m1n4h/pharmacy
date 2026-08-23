from pydantic import BaseModel
from typing import Optional


class SettingsUpdate(BaseModel):
    pharmacy_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None
    invoice_footer: Optional[str] = None
    default_currency: Optional[str] = "TZS"
    expiry_warning_days: Optional[int] = 30
    low_stock_threshold: Optional[int] = 10
    tax_rate: Optional[float] = 0
    registration_number: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None


class SettingsResponse(BaseModel):
    pharmacy_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None
    invoice_footer: Optional[str] = None
    default_currency: Optional[str] = "TZS"
    expiry_warning_days: Optional[int] = 30
    low_stock_threshold: Optional[int] = 10
    tax_rate: Optional[float] = 0
    registration_number: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None

    class Config:
        from_attributes = True
