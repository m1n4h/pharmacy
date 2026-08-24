from pydantic import BaseModel, field_validator

class MedicineAISuggestSchema(BaseModel):
    name: str
    strength: str | None = None
    category: str | None = None
    generic_name: str | None = None


class MedicineBase(BaseModel):
    name: str
    generic_name: str | None = None
    brand: str | None = None
    category: str | None = None
    form: str | None = None
    unit: str | None = None
    strength: str | None = None
    barcode: str | None = None
    image_url: str | None = None
    default_purchase_price: float | None = 0
    default_selling_price: float | None = 0

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Medicine name cannot be empty")
        return v.strip()

    @field_validator("default_purchase_price", "default_selling_price")
    @classmethod
    def validate_prices(cls, v):
        if v is not None and v < 0:
            raise ValueError("Price cannot be negative")
        return v


class MedicineCreateSchema(MedicineBase):
    pass


class MedicineUpdateSchema(BaseModel):
    name: str | None = None
    generic_name: str | None = None
    brand: str | None = None
    category: str | None = None
    form: str | None = None
    unit: str | None = None
    strength: str | None = None
    barcode: str | None = None
    image_url: str | None = None
    default_purchase_price: float | None = None
    default_selling_price: float | None = None


class MedicineResponse(BaseModel):
    id: int
    name: str
    generic_name: str | None
    brand: str | None
    category: str | None
    form: str | None
    unit: str | None
    strength: str | None
    barcode: str | None
    image_url: str | None
    default_purchase_price: float | None
    default_selling_price: float | None

    class Config:
        from_attributes = True
