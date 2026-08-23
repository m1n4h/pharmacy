from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_module
from app.db.db import get_db
from app.services.disposal_service import DisposalService

router = APIRouter(prefix="/disposals", tags=["Disposals"])


@router.post("/create")
def create_disposal(
    payload: dict,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("expiry"))
):
    result = DisposalService.create_disposal(db, payload, current_user.id)
    return {"success": True, "message": "Disposal record created", "data": result}


@router.get("/")
def list_disposals(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("expiry"))
):
    items = DisposalService.get_disposals(db, limit)
    return {"success": True, "message": "Disposals fetched", "data": {"items": items}}


@router.post("/{disposal_id}/approve")
def approve_disposal(
    disposal_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("expiry"))
):
    result = DisposalService.approve_disposal(db, disposal_id, current_user.id)
    return {"success": True, "message": "Disposal approved", "data": result}


@router.post("/{disposal_id}/dispose")
def dispose(
    disposal_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("expiry"))
):
    result = DisposalService.dispose(db, disposal_id)
    return {"success": True, "message": "Disposal completed", "data": result}
