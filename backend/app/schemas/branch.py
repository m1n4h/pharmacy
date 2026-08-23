from pydantic import BaseModel


class BranchCreate(BaseModel):
    name: str
    code: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    region: str | None = None
    district: str | None = None
    is_main: bool = False
    is_active: bool = True


class BranchUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    region: str | None = None
    district: str | None = None
    is_main: bool | None = None
    is_active: bool | None = None
