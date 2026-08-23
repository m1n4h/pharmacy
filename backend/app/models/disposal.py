from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Disposal(Base):
    __tablename__ = "disposals"

    id = Column(Integer, primary_key=True, index=True)
    disposal_number = Column(String, unique=True, nullable=False, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    disposal_method = Column(String, nullable=False)  # incineration, landfill, return_to_supplier, other
    reason = Column(Text, nullable=True)
    estimated_value = Column(Float, default=0)
    witness_name = Column(String, nullable=True)
    witness_title = Column(String, nullable=True)
    certificate_number = Column(String, nullable=True)
    tmda_reference = Column(String, nullable=True)
    disposal_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # pending, approved, disposed
    disposed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    medicine = relationship("Medicine")
    batch = relationship("Batch")
