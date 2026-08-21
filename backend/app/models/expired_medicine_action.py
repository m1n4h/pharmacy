from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, func
from app.db.base_class import Base


class ExpiredMedicineAction(Base):
    __tablename__ = "expired_medicine_actions"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String, nullable=False)  # quarantine, dispose, return
    medicine_id = Column(Integer, nullable=True)
    medicine_name = Column(String, nullable=True)
    batch_no = Column(String, nullable=True)
    batch_id = Column(Integer, nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    expiry_date = Column(Date, nullable=True)
    reason = Column(Text, nullable=True)
    responsible_person = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
