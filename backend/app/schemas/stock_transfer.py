from pydantic import BaseModel


class StockTransferCreate(BaseModel):
    medicine_id: int
    batch_id: int
    from_branch_id: int
    to_branch_id: int
    quantity: int
    notes: str | None = None
