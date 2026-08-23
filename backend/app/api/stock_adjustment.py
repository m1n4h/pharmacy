from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import get_current_user
from app.db.db import get_db
from app.models.stock_adjustment import StockAdjustment
from app.models.batch import Batch
from app.models.stock_movement import StockMovement
from app.schemas.stock_adjustment import StockAdjustmentCreate
from app.utils.pagination import Paginator


router = APIRouter(prefix="/stock-adjustments", tags=["Stock Adjustments"])


@router.post("/create")
def create_adjustment(
    payload: StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    batch = db.query(Batch).filter(Batch.id == payload.batch_id).first()
    if not batch:
        return {"success": False, "message": "Batch not found", "error": "NOT_FOUND"}

    system_quantity = batch.quantity
    difference = payload.physical_quantity - system_quantity

    adjustment = StockAdjustment(
        medicine_id=payload.medicine_id,
        batch_id=payload.batch_id,
        system_quantity=system_quantity,
        physical_quantity=payload.physical_quantity,
        difference=difference,
        reason=payload.reason,
        notes=payload.notes,
        status="pending",
        adjusted_by=current_user.id
    )
    db.add(adjustment)
    db.commit()
    db.refresh(adjustment)

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="stock_adjustments",
        details=f"Stock adjustment created for batch #{payload.batch_id} (diff: {difference})",
        user=current_user
    )

    return {
        "success": True,
        "message": "Stock adjustment created successfully",
        "data": adjustment
    }


@router.get("/")
def list_adjustments(
    status: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(StockAdjustment)

    if status:
        query = query.filter(StockAdjustment.status == status)

    query = query.order_by(StockAdjustment.created_at.desc())
    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Stock adjustments fetched successfully",
        "data": {
            "items": paginated["items"],
            "pagination": paginated["pagination"]
        }
    }


@router.post("/{adjustment_id}/approve")
def approve_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    adjustment = db.query(StockAdjustment).filter(StockAdjustment.id == adjustment_id).first()
    if not adjustment:
        return {"success": False, "message": "Adjustment not found", "error": "NOT_FOUND"}

    if adjustment.status != "pending":
        return {"success": False, "message": "Adjustment is not pending", "error": "INVALID_STATUS"}

    batch = db.query(Batch).filter(Batch.id == adjustment.batch_id).first()
    if batch:
        batch.quantity = adjustment.physical_quantity

    adjustment.status = "approved"
    adjustment.approved_by = current_user.id
    adjustment.approved_at = datetime.now()

    movement = StockMovement(
        medicine_id=adjustment.medicine_id,
        batch_id=adjustment.batch_id,
        branch_id=adjustment.branch_id,
        movement_type="adjustment",
        quantity=adjustment.difference,
        reference_type="stock_adjustment",
        reference_id=adjustment.id,
        notes=adjustment.reason or f"Stock adjustment approved",
        created_by=current_user.id
    )
    db.add(movement)
    db.commit()
    db.refresh(adjustment)

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="APPROVE", module="stock_adjustments",
        details=f"Approved adjustment #{adjustment_id} (diff: {adjustment.difference})",
        user=current_user
    )

    return {
        "success": True,
        "message": "Adjustment approved successfully",
        "data": adjustment
    }


@router.post("/{adjustment_id}/reject")
def reject_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    adjustment = db.query(StockAdjustment).filter(StockAdjustment.id == adjustment_id).first()
    if not adjustment:
        return {"success": False, "message": "Adjustment not found", "error": "NOT_FOUND"}

    if adjustment.status != "pending":
        return {"success": False, "message": "Adjustment is not pending", "error": "INVALID_STATUS"}

    adjustment.status = "rejected"
    adjustment.approved_by = current_user.id
    adjustment.approved_at = datetime.now()
    db.commit()
    db.refresh(adjustment)

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="REJECT", module="stock_adjustments",
        details=f"Rejected adjustment #{adjustment_id}",
        user=current_user
    )

    return {
        "success": True,
        "message": "Adjustment rejected",
        "data": adjustment
    }
