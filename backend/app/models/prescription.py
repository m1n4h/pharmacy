from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    prescription_no = Column(String, unique=True, index=True, nullable=False)
    patient_name = Column(String, nullable=False)
    patient_age = Column(Integer, nullable=True)
    doctor_name = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)  # pending | dispensed | cancelled
    total_amount = Column(Float, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    dispensed_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=True)

    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    medicine_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, default=0, nullable=False)

    prescription = relationship("Prescription", back_populates="items")