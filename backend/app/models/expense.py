from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, func
from app.db.base_class import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False, default="Other")
    description = Column(String, nullable=True)
    amount = Column(Float, nullable=False, default=0)
    date = Column(Date, nullable=False)
    payment_method = Column(String, nullable=True, default="Cash")
    reference = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())