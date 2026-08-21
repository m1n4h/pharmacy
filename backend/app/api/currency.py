from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.db import get_db
from app.models.currency import Currency
from app.schemas.currency import CurrencyConvert, CurrencyRatesUpdate
from app.services.currency_service import CurrencyService
from app.utils.pagination import Paginator

router = APIRouter(prefix="/currencies", tags=["Currencies"])


@router.get("/")
def list_currencies(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    currencies = CurrencyService.get_all(db)
    return {
        "success": True,
        "message": "Currencies fetched",
        "data": {
            "items": [
                {
                    "id": c.id,
                    "code": c.code,
                    "name": c.name,
                    "symbol": c.symbol,
                    "rate_to_tzs": c.rate_to_tzs
                }
                for c in currencies
            ]
        }
    }


@router.post("/convert")
def convert_amount(
    payload: CurrencyConvert,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    rate = CurrencyService.get_rate(db, payload.currency_code)
    converted = CurrencyService.convert_to_tzs(db, payload.amount, payload.currency_code)
    return {
        "success": True,
        "message": "Converted",
        "data": {
            "amount": payload.amount,
            "currency_code": (payload.currency_code or "TZS").upper(),
            "rate_to_tzs": rate,
            "amount_tzs": round(converted, 2)
        }
    }


@router.put("/update")
def update_currency_rates(
    payload: CurrencyRatesUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        return {"success": False, "message": "Permission denied", "error": "FORBIDDEN"}

    for rate in payload.rates:
        cur = db.query(Currency).filter(Currency.code == rate.code.upper()).first()
        if cur:
            cur.rate_to_tzs = rate.rate_to_tzs
            if rate.name:
                cur.name = rate.name
            if rate.symbol:
                cur.symbol = rate.symbol

    db.commit()

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="settings",
        details="Currency exchange rates updated",
        user=current_user
    )

    return {"success": True, "message": "Currency rates updated"}