from pydantic import BaseModel
from typing import Dict, List, Optional


class RolePermissionUpdate(BaseModel):
    role: str
    modules: Optional[List[str]] = None  # Legacy: list of module names
    permissions: Optional[Dict[str, str]] = None  # New: {module: permission_type}
