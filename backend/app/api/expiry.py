from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.core.deps import get_current_user
from app.db.db import get_db
from app.schemas.expired_action import ExpiredActionCreate
from app.services.expired_medicine_service import ExpiredMedicineService
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/expiry", tags=["Expiry"])


def _warning_days(db):
    s = SettingsService.get_settings(db)
    return (getattr(s, "expiry_warning_days", None) if s else None) or 30, 7


@router.get("/dashboard")
def expiry_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    wd, cd = _warning_days(db)
    return ExpiredMedicineService.dashboard(db, wd, cd)


@router.get("/")
def expiry_list(
    status_filter: str = None,  # expired, critical, expiring_soon, safe, all
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    wd, cd = _warning_days(db)
    data = ExpiredMedicineService.get_expiry_data(db, wd, cd)
    if status_filter and status_filter != "all":
        items = data.get(status_filter, [])
    else:
        items = data["expired"] + data["critical"] + data["expiring_soon"] + data["safe"]
    # sort by days_remaining ascending
    items.sort(key=lambda x: x["days_remaining"])
    start = (page - 1) * limit
    paged = items[start:start + limit]
    return {
        "success": True,
        "message": "Expiry list",
        "data": {
            "items": paged,
            "pagination": {
                "page": page, "limit": limit, "total": len(items),
                "pages": (len(items) + limit - 1) // limit
            },
            "counts": data["counts"]
        }
    }


@router.post("/action")
def expiry_action(
    payload: ExpiredActionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    action = ExpiredMedicineService.record_action(db, payload, current_user)
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="expiry",
        details=f"{payload.action_type} batch {payload.batch_no} ({payload.quantity})",
        user=current_user
    )
    return {
        "success": True,
        "message": f"Batch {payload.action_type} recorded",
        "data": {"id": action.id, "action_type": action.action_type}
    }


@router.get("/actions")
def list_actions(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = ExpiredMedicineService.list_actions(db, page, limit)
    return {
        "success": True,
        "message": "Actions fetched",
        "data": {
            "items": [
                {
                    "id": a.id,
                    "action_type": a.action_type,
                    "medicine_name": a.medicine_name,
                    "batch_no": a.batch_no,
                    "quantity": a.quantity,
                    "expiry_date": a.expiry_date,
                    "reason": a.reason,
                    "responsible_person": a.responsible_person,
                    "notes": a.notes,
                    "created_at": str(a.created_at)
                }
                for a in result["items"]
            ],
            "pagination": result["pagination"]
        }
    }
