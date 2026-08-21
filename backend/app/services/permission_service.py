from sqlalchemy.orm import Session

from app.models.permission import RolePermission

# Modules used by the frontend menu / backend guards
MODULES = [
    "dashboard",
    "medicines",
    "inventory",
    "sales",
    "purchases",
    "suppliers",
    "reports",
    "prescriptions",
    "users",
    "settings",
    "activities",
    "permissions",
]

# Default permissions: admin = everything, staff = operations only
DEFAULT_PERMISSIONS = {
    "admin": list(MODULES),
    "staff": [
        "dashboard",
        "medicines",
        "inventory",
        "sales",
        "purchases",
        "suppliers",
        "reports",
        "prescriptions",
    ],
}


class PermissionService:

    @staticmethod
    def initialize(db: Session):
        """Seed default permissions if the table is empty."""
        existing = db.query(RolePermission).first()
        if existing:
            return
        for role, modules in DEFAULT_PERMISSIONS.items():
            for module in modules:
                db.add(RolePermission(role=role, module=module))
        db.commit()

    @staticmethod
    def get_modules_for_role(db: Session, role: str):
        rows = db.query(RolePermission).filter(RolePermission.role == role).all()
        return sorted({r.module for r in rows})

    @staticmethod
    def get_all_permissions(db: Session):
        rows = db.query(RolePermission).all()
        result = {}
        for r in rows:
            result.setdefault(r.role, []).append(r.module)
        for role in result:
            result[role] = sorted(result[role])
        return result

    @staticmethod
    def has_module(db: Session, role: str, module: str) -> bool:
        if role == "admin":
            return True
        return (
            db.query(RolePermission)
            .filter(RolePermission.role == role, RolePermission.module == module)
            .first()
            is not None
        )

    @staticmethod
    def update_role(db: Session, role: str, modules: list):
        db.query(RolePermission).filter(RolePermission.role == role).delete(
            synchronize_session=False
        )
        for module in modules:
            db.add(RolePermission(role=role, module=module))
        db.commit()
        return PermissionService.get_modules_for_role(db, role)