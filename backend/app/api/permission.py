from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_module
from app.db.db import get_db
from app.schemas.permission import RolePermissionUpdate
from app.services.permission_service import PermissionService, MODULES

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/modules")
def list_modules(current_user = Depends(get_current_user)):
    """List all available modules (for the permissions UI)."""
    return {"success": True, "data": {"modules": MODULES}}


@router.get("/mine")
def my_permissions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    modules = PermissionService.get_modules_for_role(db, current_user.role)
    return {
        "success": True,
        "data": {
            "role": current_user.role,
            "modules": modules,
            "is_admin": current_user.role == "admin"
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
            "modules": MODULES
        }
    }


@router.post("/update")
def update_permissions(
    payload: RolePermissionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("permissions"))
):
    # Only admin may edit permissions
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Permission denied", "error": "FORBIDDEN"}
        )

    modules = [m for m in payload.modules if m in MODULES]
    # Admin role always keeps everything
    if payload.role == "admin":
        modules = list(MODULES)

    updated = PermissionService.update_role(db, payload.role, modules)
    return {
        "success": True,
        "message": "Permissions updated",
        "data": {"role": payload.role, "modules": updated}
    }