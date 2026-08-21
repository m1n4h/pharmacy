from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.inventory_service import InventoryService
from app.core.deps import get_current_user
from app.db.db import get_db
from app.utils.pagination import Paginator
from app.models.medicine import Medicine
from app.models.batch import Batch

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/")
def inventory_list(
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = (
        db.query(
            Medicine.id.label("medicine_id"),
            Medicine.name.label("medicine_name"),
            func.sum(Batch.quantity).label("quantity")
        )
        .join(Batch)
        .group_by(Medicine.id, Medicine.name)
    )

    if search:
        s = f"%{search}%"
        query = query.having(Medicine.name.ilike(s))

    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Inventory fetched",
        "data": {
            "items": [
                {
                    "medicine_id": row.medicine_id,
                    "medicine_name": row.medicine_name,
                    "quantity": int(row.quantity)
                }
                for row in paginated["items"]
            ],
            "pagination": paginated["pagination"]
        }
    }


# Get stock for a specific medicine
@router.get("/medicine/{medicine_id}")
def get_medicine_stock(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = InventoryService.get_medicine_stock(db, medicine_id)

    return {
        "success": True,
        "message": "Stock fetched successfully",
        "data": data
    }

# Get low stock medicines
@router.get("/low")
def get_low_stock(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = InventoryService.get_low_stock(db, limit)

    return {
        "success": True,
        "message": "Low stock medicines fetched",
        "data": data
    }

# Get near expiry batches
@router.get("/near-expiry")
def get_near_expiry(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = InventoryService.get_near_expiry(db, days)

    return {
        "success": True,
        "message": "Near expiry batches fetched",
        "data": data
    }

# Get expired batches
@router.get("/expired")
def get_expired(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = InventoryService.get_expired(db)

    return {
        "success": True,
        "message": "Expired batches fetched",
        "data": data
    }
