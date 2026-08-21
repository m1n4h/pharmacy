from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal
from app.core.security_utils import SecurityUtils


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""
    role: Literal["admin", "staff"] = "staff"

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        is_valid, message = SecurityUtils.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str