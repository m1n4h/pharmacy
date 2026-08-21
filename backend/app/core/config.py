from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str
    app_env: str
    database_url: str
    secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int = 30
    
    # Security settings
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    login_rate_limit_per_minute: int = 5
    login_rate_limit_per_hour: int = 20
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
