from sqlalchemy.orm import Session
from datetime import datetime

from app.models.activity_log import ActivityLog
from app.utils.pagination import Paginator


class ActivityService:

    @staticmethod
    def log(db: Session, action: str, module: str = None, details: str = None,
            user=None, ip_address: str = None):
        """Record an activity. Safe to call - never raises."""
        try:
            entry = ActivityLog(
                user_id=getattr(user, "id", None),
                user_email=getattr(user, "email", None),
                action=action,
                module=module,
                details=details,
                ip_address=ip_address,
                created_at=datetime.utcnow()
            )
            db.add(entry)
            db.expire_on_commit = False
            db.commit()
        except Exception:
            db.rollback()

    @staticmethod
    def list_activities(db: Session, page: int = 1, limit: int = 20,
                        module: str = None, action: str = None, search: str = None):
        query = db.query(ActivityLog)

        if module:
            query = query.filter(ActivityLog.module == module)
        if action:
            query = query.filter(ActivityLog.action == action)
        if search:
            s = f"%{search}%"
            query = query.filter(
                (ActivityLog.user_email.ilike(s)) |
                (ActivityLog.details.ilike(s))
            )

        query = query.order_by(ActivityLog.created_at.desc())
        return Paginator.paginate(query, page, limit)