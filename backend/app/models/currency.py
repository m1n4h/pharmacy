from sqlalchemy import Column, Integer, String, Float
from app.db.base_class import Base


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), nullable=False, unique=True, index=True)  # e.g. TZS, USD, ZMW
    name = Column(String, nullable=True)
    symbol = Column(String, nullable=True)  # e.g. TSh, $, K
    rate_to_tzs = Column(Float, nullable=False, default=1.0)  # 1 unit = rate_to_tzs TZS