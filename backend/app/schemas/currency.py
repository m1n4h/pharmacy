from pydantic import BaseModel
from typing import List


class CurrencyConvert(BaseModel):
    amount: float
    currency_code: str = "TZS"


class CurrencyRateUpdate(BaseModel):
    code: str
    name: str | None = None
    symbol: str | None = None
    rate_to_tzs: float


class CurrencyRatesUpdate(BaseModel):
    rates: List[CurrencyRateUpdate]