from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.db.db import get_db
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
def list_notifications(
    unread_only: bool = False,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = NotificationService.list_notifications(db, unread_only, page, limit)
    return {
        "success": True,
        "message": "Notifications fetched",
        "data": {
            "items": [
                {
                    "id": n.id,
                    "type": n.type,
                    "title": n.title,
                    "message": n.message,
                    "module": n.module,
                    "reference_id": n.reference_id,
                    "is_read": n.is_read,
                    "created_at": str(n.created_at)
                }
                for n in result["items"]
            ],
            "pagination": result["pagination"],
            "unread_count": NotificationService.unread_count(db)
        }
    }


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    NotificationService.mark_read(db, notification_id)
    return {"success": True, "message": "Marked as read"}


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    NotificationService.mark_all_read(db)
    return {"success": True, "message": "All marked as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    NotificationService.delete_notification(db, notification_id)
    return {"success": True, "message": "Notification deleted"}
