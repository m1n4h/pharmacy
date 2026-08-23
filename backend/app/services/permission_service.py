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
    "branches",
    "categories",
    "manufacturers",
    "customers",
    "stock_adjustments",
    "returns",
    "stock_transfers",
    "expiry",
    "expenses",
    "backup",
]

# Permission types
PERMISSION_TYPES = ["read", "write", "delete", "*"]  # * = all

# Default permissions: admin = everything, staff = operations only
DEFAULT_PERMISSIONS = {
    "admin": {m: "*" for m in MODULES},
    "staff": {
        "dashboard": "*",
        "medicines": "read",
        "inventory": "read",
        "sales": "*",
        "purchases": "read",
        "suppliers": "read",
        "reports": "read",
        "prescriptions": "*",
        "customers": "read",
        "expiry": "read",
    },
    "pharmacist": {
        "dashboard": "*",
        "medicines": "*",
        "inventory": "*",
        "sales": "*",
        "purchases": "read",
        "suppliers": "read",
        "reports": "read",
        "prescriptions": "*",
        "customers": "*",
        "expiry": "*",
    },
    "cashier": {
        "dashboard": "read",
        "medicines": "read",
        "inventory": "read",
        "sales": "*",
        "customers": "read",
        "prescriptions": "read",
    },
    "accountant": {
        "dashboard": "read",
        "reports": "*",
        "expenses": "*",
        "sales": "read",
        "purchases": "read",
    },
}


class PermissionService:

    @staticmethod
    def initialize(db: Session):
        """Seed default permissions if the table is empty."""
        existing = db.query(RolePermission).first()
        if existing:
            return
        for role, perms in DEFAULT_PERMISSIONS.items():
            for module, perm_type in perms.items():
                db.add(RolePermission(role=role, module=module, permission_type=perm_type))
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
            if r.role not in result:
                result[r.role] = {}
            result[r.role][r.module] = r.permission_type or "*"
        return result

    @staticmethod
    def get_role_permissions(db: Session, role: str):
        """Get detailed permissions for a role."""
        rows = db.query(RolePermission).filter(RolePermission.role == role).all()
        return {r.module: r.permission_type or "*" for r in rows}

    @staticmethod
    def has_module(db: Session, role: str, module: str) -> bool:
        if role in ("admin", "superadmin"):
            return True
        return (
            db.query(RolePermission)
            .filter(RolePermission.role == role, RolePermission.module == module)
            .first()
            is not None
        )

    @staticmethod
    def has_permission(db: Session, role: str, module: str, permission_type: str = "read") -> bool:
        """Check if role has specific permission type for a module."""
        if role in ("admin", "superadmin"):
            return True
        row = (
            db.query(RolePermission)
            .filter(RolePermission.role == role, RolePermission.module == module)
            .first()
        )
        if not row:
            return False
        pt = row.permission_type or "*"
        if pt == "*":
            return True
        if permission_type == "read":
            return pt in ("read", "write", "delete")
        if permission_type == "write":
            return pt in ("write", "delete")
        if permission_type == "delete":
            return pt == "delete"
        return False

    @staticmethod
    def update_role(db: Session, role: str, permissions: dict):
        """Update role permissions. permissions = {module: permission_type}"""
        db.query(RolePermission).filter(RolePermission.role == role).delete(
            synchronize_session=False
        )
        for module, perm_type in permissions.items():
            db.add(RolePermission(role=role, module=module, permission_type=perm_type))
        db.commit()
        return PermissionService.get_role_permissions(db, role)

    @staticmethod
    def update_role_legacy(db: Session, role: str, modules: list):
        """Legacy update - sets all listed modules to * (all permissions)."""
        perms = {m: "*" for m in modules}
        return PermissionService.update_role(db, role, perms)
