from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_module
from app.db.db import get_db
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate
from app.services.prescription_service import PrescriptionService

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


def _serialize(p):
    return {
        "id": p.id,
        "prescription_no": p.prescription_no,
        "patient_name": p.patient_name,
        "patient_age": p.patient_age,
        "doctor_name": p.doctor_name,
        "notes": p.notes,
        "status": p.status,
        "total_amount": round(float(p.total_amount), 2),
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "dispensed_at": p.dispensed_at.isoformat() if p.dispensed_at else None,
        "sale_id": p.sale_id,
        "items": [
            {
                "id": i.id,
                "medicine_id": i.medicine_id,
                "medicine_name": i.medicine_name,
                "quantity": i.quantity,
                "price": round(float(i.price), 2),
            }
            for i in p.items
        ],
    }


@router.post("/create")
def create_prescription(
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("prescriptions"))
):
    prescription, error = PrescriptionService.create_prescription(db, payload, user=current_user)
    if error:
        return {
            "success": False,
            "message": error,
            "error": "CREATE_FAILED"
        }
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="prescriptions",
        details=f"Prescription {prescription.prescription_no} for {prescription.patient_name}",
        user=current_user
    )
    return {
        "success": True,
        "message": "Prescription created",
        "data": _serialize(prescription)
    }


@router.get("/")
def list_prescriptions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("prescriptions"))
):
    paginated = PrescriptionService.list_prescriptions(
        db, page=page, limit=limit, status=status, search=search
    )
    return {
        "success": True,
        "message": "Prescriptions fetched",
        "data": {
            "items": [_serialize(p) for p in paginated["items"]],
            "pagination": paginated["pagination"]
        }
    }


@router.get("/{prescription_id}")
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("prescriptions"))
):
    prescription = PrescriptionService.get_prescription(db, prescription_id)
    if not prescription:
        return {"success": False, "message": "Prescription not found", "error": "NOT_FOUND"}
    return {"success": True, "message": "Prescription fetched", "data": _serialize(prescription)}


@router.post("/{prescription_id}/dispense")
def dispense_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("prescriptions"))
):
    prescription, error = PrescriptionService.dispense_prescription(db, prescription_id, user=current_user)
    if error:
        return {"success": False, "message": error, "error": "DISPENSE_FAILED"}
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DISPENSE", module="prescriptions",
        details=f"Dispensed {prescription.prescription_no} for {prescription.patient_name} "
                f"(total {prescription.total_amount})",
        user=current_user
    )
    return {"success": True, "message": "Prescription dispensed", "data": _serialize(prescription)}


@router.post("/{prescription_id}/cancel")
def cancel_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("prescriptions"))
):
    prescription, error = PrescriptionService.cancel_prescription(db, prescription_id, user=current_user)
    if error:
        return {"success": False, "message": error, "error": "CANCEL_FAILED"}
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CANCEL", module="prescriptions",
        details=f"Cancelled {prescription.prescription_no} for {prescription.patient_name}",
        user=current_user
    )
    return {"success": True, "message": "Prescription cancelled", "data": _serialize(prescription)}


@router.put("/{prescription_id}")
def update_prescription(
    prescription_id: int,
    payload: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("prescriptions"))
):
    prescription, error = PrescriptionService.update_prescription(db, prescription_id, payload, user=current_user)
    if error:
        return {"success": False, "message": error, "error": "UPDATE_FAILED"}
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="prescriptions",
        details=f"Updated {prescription.prescription_no}",
        user=current_user
    )
    return {"success": True, "message": "Prescription updated", "data": _serialize(prescription)}


@router.delete("/{prescription_id}")
def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_module("prescriptions"))
):
    prescription, error = PrescriptionService.delete_prescription(db, prescription_id, user=current_user)
    if error:
        return {"success": False, "message": error, "error": "DELETE_FAILED"}
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DELETE", module="prescriptions",
        details=f"Deleted prescription #{prescription_id}",
        user=current_user
    )
    return {"success": True, "message": "Prescription deleted"}