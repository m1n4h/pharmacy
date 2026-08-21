from pydantic import BaseModel


class SettingsUpdate(BaseModel):
    pharmacy_name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    invoice_footer: str | None = None
    default_currency: str | None = "TZS"
    expiry_warning_days: int | None = 30
    low_stock_threshold: int | None = 10


class SettingsResponse(BaseModel):
    pharmacy_name: str
    address: str | None
    phone: str | None
    email: str | None
    invoice_footer: str | None
    default_currency: str | None = "TZS"
    expiry_warning_days: int | None = 30
    low_stock_threshold: int | None = 10

    class Config:
        from_attributes = True
