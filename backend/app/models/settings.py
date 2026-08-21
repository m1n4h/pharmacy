from sqlalchemy import Column, Integer, String, Text
from app.db.base_class import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)   # Always 1 for singleton
    pharmacy_name = Column(String, nullable=False, default="My Pharmacy")
    address = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    invoice_footer = Column(Text, nullable=True)
    default_currency = Column(String(3), nullable=True, default="TZS")
    expiry_warning_days = Column(Integer, nullable=True, default=30)
    low_stock_threshold = Column(Integer, nullable=True, default=10)
