from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.db import get_db
from app.models.manufacturer import Manufacturer
from app.schemas.manufacturer import ManufacturerCreate, ManufacturerUpdate
from app.services.manufacturer_service import ManufacturerService
from app.utils.pagination import Paginator


router = APIRouter(prefix="/manufacturers", tags=["Manufacturers"])


@router.post("/create")
def create_manufacturer(
    payload: ManufacturerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    manufacturer = ManufacturerService.create(db, payload)

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="manufacturers",
        details=f"Manufacturer: {manufacturer.name}",
        user=current_user
    )

    return {
        "success": True,
        "message": "Manufacturer created successfully",
        "data": manufacturer
    }


@router.get("/")
def list_manufacturers(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Manufacturer).order_by(Manufacturer.name)
    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Manufacturers fetched successfully",
        "data": {
            "items": paginated["items"],
            "pagination": paginated["pagination"]
        }
    }


@router.put("/{manufacturer_id}")
def update_manufacturer(
    manufacturer_id: int,
    payload: ManufacturerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    manufacturer = ManufacturerService.update(db, manufacturer_id, payload)

    if not manufacturer:
        return {"success": False, "message": "Manufacturer not found", "error": "NOT_FOUND"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="manufacturers",
        details=f"Updated manufacturer #{manufacturer_id} ({manufacturer.name})",
        user=current_user
    )

    return {
        "success": True,
        "message": "Manufacturer updated successfully",
        "data": manufacturer
    }


@router.delete("/{manufacturer_id}")
def delete_manufacturer(
    manufacturer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    manufacturer = ManufacturerService.delete(db, manufacturer_id)

    if not manufacturer:
        return {"success": False, "message": "Manufacturer not found", "error": "NOT_FOUND"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DELETE", module="manufacturers",
        details=f"Deleted manufacturer #{manufacturer_id} ({manufacturer.name})",
        user=current_user
    )

    return {"success": True, "message": "Manufacturer deleted successfully"}
