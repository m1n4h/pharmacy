from pydantic import BaseModel
from typing import List


class RolePermissionUpdate(BaseModel):
    role: str
    modules: List[str]