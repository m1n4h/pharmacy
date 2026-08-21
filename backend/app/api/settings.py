from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.db import get_db
from app.schemas.settings import SettingsUpdate
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/")
def get_settings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    settings = SettingsService.get_settings(db)
    return {
        "success": True,
        "message": "Settings fetched successfully",
        "data": settings
    }


@router.put("/")
def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    settings = SettingsService.update_settings(db, payload)
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="settings",
        details=f"Settings updated (pharmacy: {settings.pharmacy_name})",
        user=current_user
    )
    return {
        "success": True,
        "message": "Settings updated successfully",
        "data": settings
    }
