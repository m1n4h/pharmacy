from pydantic import BaseModel


class StockAdjustmentCreate(BaseModel):
    medicine_id: int
    batch_id: int
    physical_quantity: int
    reason: str | None = None
    notes: str | None = None
