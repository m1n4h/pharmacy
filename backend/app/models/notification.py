from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from app.db.base_class import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False, default="system")  # low_stock, expiry, supplier_payment, expense, system
    title = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    module = Column(String, nullable=True)
    reference_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
