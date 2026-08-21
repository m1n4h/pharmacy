from pydantic import BaseModel

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

    class Config:
        from_attributes = True
