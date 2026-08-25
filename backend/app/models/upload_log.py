from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.db.base_class import Base


class SalesUploadLog(Base):
    __tablename__ = "sales_upload_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, default=0)
    rows_extracted = Column(Integer, default=0)
    sales_created = Column(Integer, default=0)
    errors = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, processed, failed
    created_at = Column(DateTime, nullable=False, server_default=func.now())
