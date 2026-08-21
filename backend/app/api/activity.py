from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_module
from app.db.db import get_db
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("/")
def list_activities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    module: str | None = None,
    action: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("activities"))
):
    paginated = ActivityService.list_activities(
        db, page=page, limit=limit, module=module, action=action, search=search
    )
    items = [
        {
            "id": a.id,
            "user_email": a.user_email or "system",
            "action": a.action,
            "module": a.module or "",
            "details": a.details or "",
            "ip_address": a.ip_address or "",
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in paginated["items"]
    ]
    return {
        "success": True,
        "message": "Activities fetched",
        "data": {
            "items": items,
            "pagination": paginated["pagination"]
        }
    }