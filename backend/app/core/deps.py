from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.db import get_db
from app.models.user import User
from app.services.auth_service import AuthService

settings = get_settings()

def auth_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "success": False,
            "message": "Invalid or missing token",
            "error": "UNAUTHORIZED"
        },
        headers={"WWW-Authenticate": "Bearer"},
    )

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    if not credentials:
        raise auth_exception()

    # Check if token is blocked
    if AuthService.is_token_blocked(db, credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Token has been revoked",
                "error": "TOKEN_REVOKED"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.secret_key, 
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        
        email = payload.get("sub")
        if not email:
            raise auth_exception()

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise auth_exception()

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Token has expired",
                "error": "TOKEN_EXPIRED"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    except (JWTError, Exception):
        raise auth_exception()


def require_module(module: str):
    """Dependency factory: 403 if the user's role lacks permission for the module."""
    from app.services.permission_service import PermissionService

    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        # Admins always have full access
        if current_user.role != "admin" and not PermissionService.has_module(
            db, current_user.role, module
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "message": "You do not have permission to access this module",
                    "error": "FORBIDDEN"
                }
            )
        return current_user

    return checker