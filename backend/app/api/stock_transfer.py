from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import get_current_user
from app.db.db import get_db
from app.models.stock_transfer import StockTransfer
from app.models.batch import Batch
from app.models.stock_movement import StockMovement
from app.schemas.stock_transfer import StockTransferCreate
from app.utils.pagination import Paginator


router = APIRouter(prefix="/stock-transfers", tags=["Stock Transfers"])


@router.post("/create")
def create_transfer(
    payload: StockTransferCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    source_batch = db.query(Batch).filter(Batch.id == payload.batch_id).first()
    if not source_batch:
        return {"success": False, "message": "Source batch not found", "error": "NOT_FOUND"}

    if source_batch.quantity < payload.quantity:
        return {"success": False, "message": "Insufficient stock in source batch", "error": "INSUFFICIENT_STOCK"}

    transfer = StockTransfer(
        medicine_id=payload.medicine_id,
        batch_id=payload.batch_id,
        from_branch_id=payload.from_branch_id,
        to_branch_id=payload.to_branch_id,
        quantity=payload.quantity,
        notes=payload.notes,
        status="pending",
        requested_by=current_user.id
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="stock_transfers",
        details=f"Transfer request: batch #{payload.batch_id} ({payload.quantity} units)",
        user=current_user
    )

    return {
        "success": True,
        "message": "Transfer request created successfully",
        "data": transfer
    }


@router.get("/")
def list_transfers(
    status: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(StockTransfer)

    if status:
        query = query.filter(StockTransfer.status == status)

    query = query.order_by(StockTransfer.created_at.desc())
    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Stock transfers fetched successfully",
        "data": {
            "items": paginated["items"],
            "pagination": paginated["pagination"]
        }
    }


@router.post("/{transfer_id}/approve")
def approve_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    transfer = db.query(StockTransfer).filter(StockTransfer.id == transfer_id).first()
    if not transfer:
        return {"success": False, "message": "Transfer not found", "error": "NOT_FOUND"}

    if transfer.status != "pending":
        return {"success": False, "message": "Transfer is not pending", "error": "INVALID_STATUS"}

    source_batch = db.query(Batch).filter(Batch.id == transfer.batch_id).first()
    if not source_batch:
        return {"success": False, "message": "Source batch not found", "error": "NOT_FOUND"}

    if source_batch.quantity < transfer.quantity:
        return {"success": False, "message": "Insufficient stock in source batch", "error": "INSUFFICIENT_STOCK"}

    # Deduct from source batch
    source_batch.quantity -= transfer.quantity

    # Find or create destination batch
    dest_batch = db.query(Batch).filter(
        Batch.medicine_id == transfer.medicine_id,
        Batch.batch_no == source_batch.batch_no,
        Batch.branch_id == transfer.to_branch_id
    ).first()

    if dest_batch:
        dest_batch.quantity += transfer.quantity
    else:
        dest_batch = Batch(
            batch_no=source_batch.batch_no,
            manufacturing_date=source_batch.manufacturing_date,
            expiry_date=source_batch.expiry_date,
            purchase_price=source_batch.purchase_price,
            selling_price=source_batch.selling_price,
            quantity=transfer.quantity,
            medicine_id=transfer.medicine_id,
            branch_id=transfer.to_branch_id
        )
        db.add(dest_batch)

    # Create stock movements
    out_movement = StockMovement(
        medicine_id=transfer.medicine_id,
        batch_id=transfer.batch_id,
        branch_id=transfer.from_branch_id,
        movement_type="transfer_out",
        quantity=-transfer.quantity,
        reference_type="stock_transfer",
        reference_id=transfer.id,
        notes=f"Transfer to branch #{transfer.to_branch_id}",
        created_by=current_user.id
    )
    db.add(out_movement)

    in_movement = StockMovement(
        medicine_id=transfer.medicine_id,
        batch_id=transfer.batch_id,
        branch_id=transfer.to_branch_id,
        movement_type="transfer_in",
        quantity=transfer.quantity,
        reference_type="stock_transfer",
        reference_id=transfer.id,
        notes=f"Transfer from branch #{transfer.from_branch_id}",
        created_by=current_user.id
    )
    db.add(in_movement)

    transfer.status = "completed"
    transfer.approved_by = current_user.id
    transfer.completed_at = datetime.now()
    db.commit()
    db.refresh(transfer)

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="APPROVE", module="stock_transfers",
        details=f"Approved transfer #{transfer_id} ({transfer.quantity} units)",
        user=current_user
    )

    return {
        "success": True,
        "message": "Transfer approved and executed successfully",
        "data": transfer
    }


@router.post("/{transfer_id}/reject")
def reject_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    transfer = db.query(StockTransfer).filter(StockTransfer.id == transfer_id).first()
    if not transfer:
        return {"success": False, "message": "Transfer not found", "error": "NOT_FOUND"}

    if transfer.status != "pending":
        return {"success": False, "message": "Transfer is not pending", "error": "INVALID_STATUS"}

    transfer.status = "rejected"
    transfer.approved_by = current_user.id
    db.commit()
    db.refresh(transfer)

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="REJECT", module="stock_transfers",
        details=f"Rejected transfer #{transfer_id}",
        user=current_user
    )

    return {
        "success": True,
        "message": "Transfer rejected",
        "data": transfer
    }
