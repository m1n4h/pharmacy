from pydantic import BaseModel, EmailStr

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    success: bool
    message: str
    data: dict

class LoginErrorResponse(BaseModel):
    success: bool
    message: str
    error: str
