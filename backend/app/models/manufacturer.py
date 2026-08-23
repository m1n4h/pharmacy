from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    country = Column(String, nullable=True)
    contact_info = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
