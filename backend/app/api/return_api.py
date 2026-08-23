from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.db import get_db
from app.models.return_record import Return
from app.schemas.return_record import ReturnCreate
from app.services.return_service import ReturnService
from app.utils.pagination import Paginator


router = APIRouter(prefix="/returns", tags=["Returns"])


@router.post("/create")
def create_return(
    payload: ReturnCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    items_list = [item.dict() for item in payload.items]

    return_record = ReturnService.create_return(
        db, payload.sale_id, items_list, payload.reason, current_user.id
    )

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="returns",
        details=f"Return {return_record.return_number} (refund: {return_record.total_refund})",
        user=current_user
    )

    return {
        "success": True,
        "message": "Return processed successfully",
        "data": return_record
    }


@router.get("/")
def list_returns(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Return).order_by(Return.created_at.desc())
    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Returns fetched successfully",
        "data": {
            "items": paginated["items"],
            "pagination": paginated["pagination"]
        }
    }


@router.get("/{return_id}")
def get_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return_record = ReturnService.get_return(db, return_id)

    if not return_record:
        return {"success": False, "message": "Return not found", "error": "NOT_FOUND"}

    return {
        "success": True,
        "message": "Return fetched successfully",
        "data": {
            "id": return_record.id,
            "return_number": return_record.return_number,
            "sale_id": return_record.sale_id,
            "customer_id": return_record.customer_id,
            "reason": return_record.reason,
            "total_refund": return_record.total_refund,
            "status": return_record.status,
            "created_at": return_record.created_at,
            "items": [
                {
                    "id": item.id,
                    "sale_item_id": item.sale_item_id,
                    "medicine_id": item.medicine_id,
                    "batch_id": item.batch_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "refund_amount": item.refund_amount,
                    "condition": item.condition
                }
                for item in return_record.items
            ]
        }
    }
