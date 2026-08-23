from sqlalchemy import Column, Integer, String, Float, DateTime, Date, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    generic_name = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    category = Column(String, nullable=True)
    form = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    strength = Column(String, nullable=True)
    barcode = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    default_purchase_price = Column(Float, nullable=True, default=0)
    default_selling_price = Column(Float, nullable=True, default=0)
    manufacturer = Column(String, nullable=True)
    storage_condition = Column(String, nullable=True)
    prescription_required = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    max_stock_level = Column(Integer, default=100)
    last_sold_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    batches = relationship("Batch", back_populates="medicine", cascade="all, delete")
