from sqlalchemy.orm import Session
from app.models.currency import Currency


class CurrencyService:

    @staticmethod
    def get_all(db: Session):
        return db.query(Currency).order_by(Currency.id).all()

    @staticmethod
    def get_by_code(db: Session, code: str):
        if not code:
            return None
        return db.query(Currency).filter(Currency.code == code.upper()).first()

    @staticmethod
    def convert_to_tzs(db: Session, amount: float, currency_code: str) -> float:
        """Convert an amount in a foreign currency to TZS. TZS amounts pass through."""
        if not amount:
            return 0.0
        code = (currency_code or "TZS").upper()
        if code == "TZS":
            return float(amount)
        cur = CurrencyService.get_by_code(db, code)
        rate = cur.rate_to_tzs if cur else 1.0
        return float(amount) * rate

    @staticmethod
    def get_rate(db: Session, currency_code: str) -> float:
        code = (currency_code or "TZS").upper()
        if code == "TZS":
            return 1.0
        cur = CurrencyService.get_by_code(db, code)
        return cur.rate_to_tzs if cur else 1.0


def format_tzs(amount) -> str:
    """Format a TZS amount with thousand separators."""
    try:
        return f"{float(amount):,.0f}"
    except (TypeError, ValueError):
        return "0"