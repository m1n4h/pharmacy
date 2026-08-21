from pydantic import BaseModel
from typing import Optional


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: Optional[str]
    module: Optional[str]
    reference_id: Optional[int]
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True
