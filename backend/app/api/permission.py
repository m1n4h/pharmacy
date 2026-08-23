from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_module
from app.db.db import get_db
from app.schemas.permission import RolePermissionUpdate
from app.services.permission_service import PermissionService, MODULES, PERMISSION_TYPES

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/modules")
def list_modules(current_user = Depends(get_current_user)):
    """List all available modules and permission types (for the permissions UI)."""
    return {"success": True, "data": {"modules": MODULES, "permission_types": PERMISSION_TYPES}}


@router.get("/mine")
def my_permissions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    modules = PermissionService.get_modules_for_role(db, current_user.role)
    detailed = PermissionService.get_role_permissions(db, current_user.role)
    is_admin = current_user.role in ("admin", "superadmin")
    return {
        "success": True,
        "data": {
            "role": current_user.role,
            "modules": modules,
            "detailed": detailed,
            "is_admin": is_admin
        }
    }


@router.get("/")
def get_all_permissions(
    db: Session = Depends(get_db),
    current_user = Depends(require_module("permissions"))
):
    return {
        "success": True,
        "data": {
            "permissions": PermissionService.get_all_permissions(db),
            "modules": MODULES,
            "permission_types": PERMISSION_TYPES
        }
    }


@router.post("/update")
def update_permissions(
    payload: RolePermissionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("permissions"))
):
    # Only admin may edit permissions
    if current_user.role not in ("admin", "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Permission denied", "error": "FORBIDDEN"}
        )

    # Admin role always keeps everything
    if payload.role == "admin":
        perms = {m: "*" for m in MODULES}
    else:
        perms = {}
        for module, perm_type in payload.permissions.items():
            if module in MODULES and perm_type in PERMISSION_TYPES:
                perms[module] = perm_type

    updated = PermissionService.update_role(db, payload.role, perms)
    return {
        "success": True,
        "message": "Permissions updated",
        "data": {"role": payload.role, "permissions": updated}
    }
