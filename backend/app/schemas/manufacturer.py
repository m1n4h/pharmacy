from pydantic import BaseModel


class ManufacturerCreate(BaseModel):
    name: str
    country: str | None = None
    contact_info: str | None = None


class ManufacturerUpdate(BaseModel):
    name: str | None = None
    country: str | None = None
    contact_info: str | None = None
