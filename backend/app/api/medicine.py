from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.medicine import MedicineCreateSchema, MedicineUpdateSchema, MedicineAISuggestSchema
from typing import List
from app.services.medicine_service import MedicineService
from app.services.medicine_ai_service import MedicineAIService
from app.core.deps import get_current_user
from app.db.db import get_db
from app.utils.pagination import Paginator
from app.models.medicine import Medicine
from app.models.batch import Batch
from sqlalchemy import func


router = APIRouter(prefix="/medicines", tags=["Medicines"])


# AI Medicine Suggestion
@router.post("/ai-suggest")
def ai_suggest_medicine(
    payload: MedicineAISuggestSchema,
    current_user = Depends(get_current_user)
):
    """Suggest medicine details (generic, category, form, unit, strength) from a name."""
    suggestion = MedicineAIService.suggest(
        payload.name, payload.strength, payload.category, payload.generic_name
    )
    return {"success": True, "message": "Suggestion generated", "data": suggestion}


# Create Medicine
@router.post("/")
def create_medicine(
    payload: MedicineCreateSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    med, error = MedicineService.create(db, payload)

    if error == "MEDICINE_EXISTS":
        return {
            "success": False,
            "message": "Medicine name already exists",
            "error": "MEDICINE_EXISTS"
        }

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="medicines",
        details=f"Medicine: {med.name}",
        user=current_user
    )

    return {
        "success": True,
        "message": "Medicine created successfully",
        "data": {
            "id": med.id,
            "name": med.name,
            "generic_name": med.generic_name,
            "brand": med.brand,
            "category": med.category,
            "form": med.form,
            "unit": med.unit,
            "strength": med.strength,
            "barcode": med.barcode,
            "image_url": med.image_url
        }
    }


# Bulk Create Medicines
@router.post("/bulk-create")
def bulk_create_medicines(
    medicines: List[MedicineCreateSchema],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    created_medicines = []
    errors = []
    
    for i, medicine_data in enumerate(medicines):
        med, error = MedicineService.create(db, medicine_data)
        
        if error:
            errors.append({
                "index": i,
                "name": medicine_data.name,
                "error": error
            })
        else:
            created_medicines.append({
                "id": med.id,
                "name": med.name,
                "generic_name": med.generic_name,
                "brand": med.brand,
                "category": med.category,
                "form": med.form,
                "unit": med.unit,
                "strength": med.strength,
                "barcode": med.barcode,
                "image_url": med.image_url
            })
    
    return {
        "success": True,
        "message": f"Bulk operation completed. {len(created_medicines)} created, {len(errors)} failed.",
        "data": {
            "created": created_medicines,
            "errors": errors,
            "summary": {
                "total": len(medicines),
                "created": len(created_medicines),
                "failed": len(errors)
            }
        }
    }


# Get Medicine Detail
@router.get("/{medicine_id}")
def get_medicine_detail(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    
    if not medicine:
        return {
            "success": False,
            "message": "Medicine not found",
            "error": "NOT_FOUND"
        }
    
    return {
        "success": True,
        "message": "Medicine details fetched successfully",
        "data": {
            "id": medicine.id,
            "name": medicine.name,
            "generic_name": medicine.generic_name,
            "brand": medicine.brand,
            "category": medicine.category,
            "form": medicine.form,
            "unit": medicine.unit,
            "strength": medicine.strength,
            "barcode": medicine.barcode,
            "image_url": medicine.image_url
        }
    }

# List Medicines
@router.get("/")
def list_medicines(
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Subquery to get the single latest batch for each medicine
    # (tie-break: smallest batch id) to avoid duplicate rows per medicine
    best_batch = db.query(
        Batch.medicine_id.label("medicine_id"),
        Batch.id.label("batch_id"),
        func.row_number().over(
            partition_by=Batch.medicine_id,
            order_by=(Batch.expiry_date.desc(), Batch.id.asc())
        ).label("rn")
    ).subquery()

    query = db.query(Medicine, Batch.selling_price, Batch.expiry_date).outerjoin(
        best_batch,
        (best_batch.c.medicine_id == Medicine.id) & (best_batch.c.rn == 1)
    ).outerjoin(
        Batch, Batch.id == best_batch.c.batch_id
    )

    if search:
        s = f"%{search}%"
        query = query.filter(
            (Medicine.name.ilike(s)) |
            (Medicine.generic_name.ilike(s))
        )

    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Medicines fetched successfully",
        "data": {
            "items": [
                {
                    "id": item[0].id,
                    "name": item[0].name,
                    "generic_name": item[0].generic_name,
                    "brand": item[0].brand,
                    "category": item[0].category,
                    "form": item[0].form,
                    "unit": item[0].unit,
                    "strength": item[0].strength,
                    "barcode": item[0].barcode,
                    "image_url": item[0].image_url,
                    "price": item[1] if len(item) > 1 and item[1] else None,
                    "expiry_date": item[2].isoformat() if len(item) > 2 and item[2] else None
                }
                for item in paginated["items"]
            ],
            "pagination": paginated["pagination"]
        }
    }

# Update Medicine
@router.put("/{medicine_id}")
def update_medicine(
    medicine_id: int,
    payload: MedicineUpdateSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    med, error = MedicineService.update(db, medicine_id, payload)

    if error == "NOT_FOUND":
        return {
            "success": False,
            "message": "Medicine not found",
            "error": "NOT_FOUND"
        }

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="medicines",
        details=f"Medicine: {med.name}",
        user=current_user
    )

    return {
        "success": True,
        "message": "Medicine updated successfully",
        "data": {
            "id": med.id,
            "name": med.name,
            "generic_name": med.generic_name,
            "brand": med.brand,
            "category": med.category,
            "form": med.form,
            "unit": med.unit,
            "strength": med.strength,
            "barcode": med.barcode,
            "image_url": med.image_url
        }
    }


# Delete Medicine
@router.delete("/{medicine_id}")
def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # Optional: only admins can delete
    if current_user.role != "admin":
        return {
            "success": False,
            "message": "Permission denied",
            "error": "FORBIDDEN"
        }

    error = MedicineService.delete(db, medicine_id)

    if error == "NOT_FOUND":
        return {
            "success": False,
            "message": "Medicine not found",
            "error": "NOT_FOUND"
        }

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DELETE", module="medicines",
        details=f"Medicine id: {medicine_id}",
        user=current_user
    )

    return {
        "success": True,
        "message": "Medicine deleted successfully",
        "data": {}
    }
