from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.user import UserCreateSchema
from app.services.user_service import UserService
from app.core.deps import get_current_user
from app.db.db import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role not in ("admin", "superadmin"):
        return {"success": False, "message": "Permission denied", "error": "FORBIDDEN"}

    users = UserService.list_users(db)
    return {
        "success": True,
        "message": "Users fetched",
        "data": {
            "items": [
                {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                    "role": u.role,
                    "is_active": u.is_active == 1,
                    "is_superuser": getattr(u, 'is_superuser', 0) == 1
                }
                for u in users
            ]
        }
    }


@router.post("/{user_id}/toggle-active")
def toggle_active_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.role != "superadmin":
        return {"success": False, "message": "Permission denied", "error": "FORBIDDEN"}

    target = UserService.get_user_by_id(db, user_id)
    if target and getattr(target, 'is_superuser', 0) == 1:
        return {"success": False, "message": "Cannot modify the superuser account", "error": "SUPERUSER_PROTECTED"}

    user, error = UserService.toggle_active(db, user_id)
    if error:
        return {"success": False, "message": "User not found", "error": error}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="users",
        details=f"Toggled user {user.email} active={user.is_active == 1}",
        user=current_user
    )

    return {
        "success": True,
        "message": "User status updated",
        "data": {"id": user.id, "email": user.email, "is_active": user.is_active == 1}
    }

@router.post("/create")
def create_user_endpoint(
    payload: UserCreateSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # Allow only admin or superadmin to create users
    if current_user.role not in ("admin", "superadmin"):
        return {
            "success": False,
            "message": "Permission denied",
            "error": "FORBIDDEN"
        }

    user, error = UserService.create_user(
        db=db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role
    )

    if error == "EMAIL_EXISTS":
        return {
            "success": False,
            "message": "Email already registered",
            "error": "EMAIL_EXISTS"
        }

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="users",
        details=f"Created user {user.email} (role: {user.role})",
        user=current_user
    )

    return {
        "success": True,
        "message": "User created successfully",
        "data": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.delete("/{user_id}")
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.role != "superadmin":
        return {"success": False, "message": "Permission denied", "error": "FORBIDDEN"}

    if current_user.id == user_id:
        return {
            "success": False,
            "message": "Cannot delete your own account",
            "error": "SELF_DELETE"
        }

    target = UserService.get_user_by_id(db, user_id)
    if target and getattr(target, 'is_superuser', 0) == 1:
        return {"success": False, "message": "Cannot delete the superuser account", "error": "SUPERUSER_PROTECTED"}

    # Prevent deleting the last remaining active admin
    if target and target.role == "admin":
        if UserService.count_active_admins(db, exclude_user_id=user_id) == 0:
            return {
                "success": False,
                "message": "Cannot delete the last active admin",
                "error": "LAST_ADMIN"
            }

    user, error = UserService.delete_user(db, user_id)
    if error:
        return {"success": False, "message": "User not found", "error": error}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DELETE", module="users",
        details=f"Deleted user {user.email} (role: {user.role})",
        user=current_user
    )

    return {
        "success": True,
        "message": "User deleted successfully",
        "data": {"id": user.id, "email": user.email}
    }
