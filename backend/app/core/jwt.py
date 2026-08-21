from datetime import datetime, timedelta
from jose import jwt
from app.core.config import get_settings
import secrets

settings = get_settings()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key,
        algorithm="HS256"
    )
    return encoded_jwt, settings.access_token_expire_minutes * 60

def create_refresh_token():
    return secrets.token_urlsafe(32)

def decode_token(token: str):
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
