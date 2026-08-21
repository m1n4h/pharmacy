from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.notification import Notification
from app.utils.pagination import Paginator


class NotificationService:

    @staticmethod
    def create_notification(db: Session, type, title, message=None, module=None, reference_id=None):
        n = Notification(
            type=type, title=title, message=message,
            module=module, reference_id=reference_id, is_read=False
        )
        db.add(n)
        db.commit()
        db.refresh(n)
        return n

    @staticmethod
    def list_notifications(db: Session, only_unread=False, page=1, limit=20):
        query = db.query(Notification)
        if only_unread:
            query = query.filter(Notification.is_read == False)
        query = query.order_by(desc(Notification.created_at))
        return Paginator.paginate(query, page, limit)

    @staticmethod
    def unread_count(db: Session):
        return db.query(func.count(Notification.id)).filter(Notification.is_read == False).scalar()

    @staticmethod
    def mark_read(db: Session, notification_id: int):
        n = db.query(Notification).filter(Notification.id == notification_id).first()
        if n:
            n.is_read = True
            db.commit()
        return n

    @staticmethod
    def mark_all_read(db: Session):
        db.query(Notification).filter(Notification.is_read == False).update({"is_read": True})
        db.commit()
        return True

    @staticmethod
    def delete_notification(db: Session, notification_id: int):
        n = db.query(Notification).filter(Notification.id == notification_id).first()
        if n:
            db.delete(n)
            db.commit()
        return n
