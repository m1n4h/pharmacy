from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.db import get_db
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.services.supplier_service import SupplierService
from app.utils.pagination import Paginator
from app.models.supplier import Supplier


router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("/create")
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    supplier = SupplierService.create_supplier(db, payload)
    if not supplier:
        return JSONResponse(status_code=400, content={"success": False, "message": "Supplier already exists", "error": "DUPLICATE"})

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="suppliers",
        details=f"Supplier: {supplier.name}",
        user=current_user
    )

    return {
        "success": True,
        "message": "Supplier created successfully",
        "data": supplier
    }


@router.get("/")
def list_suppliers(
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Supplier)

    if search:
        s = f"%{search}%"
        query = query.filter(
            Supplier.name.ilike(s) |
            Supplier.company_name.ilike(s)
        )

    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Suppliers fetched successfully",
        "data": {
            "items": paginated["items"],
            "pagination": paginated["pagination"]
        }
    }


@router.put("/{supplier_id}")
def update_supplier(
    supplier_id: int,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    supplier = SupplierService.update_supplier(db, supplier_id, payload)

    if not supplier:
        return {"success": False, "message": "Supplier not found", "error": "NOT_FOUND"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="suppliers",
        details=f"Updated supplier #{supplier_id} ({supplier.name})",
        user=current_user
    )

    return {
        "success": True,
        "message": "Supplier updated successfully",
        "data": supplier
    }


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    supplier = SupplierService.delete_supplier(db, supplier_id)

    if not supplier:
        return {"success": False, "message": "Supplier not found", "error": "NOT_FOUND"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DELETE", module="suppliers",
        details=f"Deleted supplier #{supplier_id} ({supplier.name})",
        user=current_user
    )

    return {"success": True, "message": "Supplier deleted successfully"}
