from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.user import User
from app.models.token import RefreshToken, BlockedToken
from app.core.security import verify_password
from app.core.jwt import create_access_token, create_refresh_token
from app.core.config import get_settings
from app.core.security_utils import SecurityUtils
import logging
import time

settings = get_settings()
logger = logging.getLogger(__name__)

class AuthService:

    @staticmethod
    def login(db: Session, email: str, password: str, ip_address: str = None):
        # Add small delay to prevent timing attacks
        start_time = time.time()
        
        # Sanitize email input
        email = SecurityUtils.sanitize_input(email, max_length=255)
        
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # Constant time delay to prevent user enumeration
            time.sleep(max(0, 0.5 - (time.time() - start_time)))
            logger.warning(f"Failed login attempt for non-existent user: {email} from IP: {ip_address}")
            return None, None, None, None, "INVALID_CREDENTIALS"

        if not verify_password(password, user.hashed_password):
            # Constant time delay
            time.sleep(max(0, 0.5 - (time.time() - start_time)))
            logger.warning(f"Failed login attempt for user: {email} from IP: {ip_address}")
            return None, None, None, None, "INVALID_CREDENTIALS"

        if user.is_active != 1:
            # Constant time delay
            time.sleep(max(0, 0.5 - (time.time() - start_time)))
            logger.warning(f"Disabled account login attempt for user: {email} from IP: {ip_address}")
            return None, None, None, None, "ACCOUNT_DISABLED"
        
        logger.info(f"Successful login for user: {email} from IP: {ip_address}")

        access_token, expires_in = create_access_token({"sub": user.email})
        refresh_token = create_refresh_token()
        
        # Store refresh token (hashed - never store raw tokens)
        refresh_expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        db_refresh_token = RefreshToken(
            token=SecurityUtils.hash_token(refresh_token),
            user_id=user.id,
            expires_at=refresh_expires
        )
        db.add(db_refresh_token)
        db.commit()

        return access_token, refresh_token, expires_in, user, None

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str):
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == SecurityUtils.hash_token(refresh_token),
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not db_token:
            return None, None, "INVALID_REFRESH_TOKEN"
            
        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            return None, None, "USER_NOT_FOUND"
            
        access_token, expires_in = create_access_token({"sub": user.email})
        return access_token, expires_in, None

    @staticmethod
    def logout(db: Session, access_token: str, refresh_token: str = None):
        # Cleanup: remove blocked tokens that can no longer be used (they expire with the access token)
        cleanup_before = datetime.utcnow() - timedelta(minutes=settings.access_token_expire_minutes)
        db.query(BlockedToken).filter(
            BlockedToken.blocked_at < cleanup_before
        ).delete(synchronize_session=False)
        
        # Block access token
        blocked_token = BlockedToken(token=access_token)
        db.add(blocked_token)
        
        # Remove refresh token if provided (token is stored hashed)
        if refresh_token:
            db.query(RefreshToken).filter(
                RefreshToken.token == SecurityUtils.hash_token(refresh_token)
            ).delete(synchronize_session=False)
            
        db.commit()
        return True

    @staticmethod
    def is_token_blocked(db: Session, token: str) -> bool:
        return db.query(BlockedToken).filter(BlockedToken.token == token).first() is not None
