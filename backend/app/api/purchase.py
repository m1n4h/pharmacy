from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.purchase import Purchase
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from typing import List
from app.services.purchase_service import PurchaseService
from app.core.deps import get_current_user
from app.db.db import get_db
from app.utils.pagination import Paginator
from app.models.purchase import Purchase


router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.post("/create")
def create_purchase(
    payload: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # Create purchase + items + batches
    purchase = PurchaseService.create_purchase(db, payload)

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="purchases",
        details=f"Purchase {purchase.invoice_number} from {purchase.supplier_name} "
                f"(total {purchase.total_amount})",
        user=current_user
    )

    # Format response
    return {
        "success": True,
        "message": "Purchase created successfully",
        "data": {
            "id": purchase.id,
            "invoice_number": purchase.invoice_number,
            "supplier_name": purchase.supplier_name,
            "purchase_date": purchase.purchase_date,
            "total_amount": purchase.total_amount,
            "currency_code": purchase.currency_code,
            "currency_amount": purchase.currency_amount,
            "currency_rate": purchase.currency_rate,
            "created_at": purchase.created_at,
            "items": [
                {
                    "id": item.id,
                    "medicine_id": item.medicine_id,
                    "batch_no": item.batch_no,
                    "expiry_date": item.expiry_date,
                    "purchase_price": item.purchase_price,
                    "selling_price": item.selling_price,
                    "quantity": item.quantity
                }
                for item in purchase.items
            ]
        }
    }

@router.post("/bulk-create")
def create_multiple_purchases(
    purchases: List[PurchaseCreate],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    created_purchases = []
    errors = []
    
    for i, purchase_data in enumerate(purchases):
        try:
            purchase = PurchaseService.create_purchase(db, purchase_data)
            created_purchases.append({
                "id": purchase.id,
                "invoice_number": purchase.invoice_number,
                "supplier_name": purchase.supplier_name,
                "purchase_date": purchase.purchase_date,
                "total_amount": purchase.total_amount
            })
        except Exception as e:
            errors.append({
                "index": i,
                "invoice_number": purchase_data.invoice_number,
                "error": str(e)
            })
    
    return {
        "success": len(errors) == 0,
        "message": f"Created {len(created_purchases)} purchases" + (f", {len(errors)} failed" if errors else ""),
        "data": {
            "created": created_purchases,
            "errors": errors,
            "summary": {
                "total_requested": len(purchases),
                "created_count": len(created_purchases),
                "error_count": len(errors)
            }
        }
    }

# List purchases
@router.get("/")
def list_purchases(
    search: str | None = None,    # invoice or supplier
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    query = db.query(Purchase)

    if search:
        s = f"%{search}%"
        query = query.filter(
            (Purchase.invoice_number.ilike(s)) |
            (Purchase.supplier_name.ilike(s))
        )

    query = query.order_by(Purchase.created_at.desc())
    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Purchases fetched",
        "data": {
            "items": [
                {
                    "id": p.id,
                    "invoice_number": p.invoice_number,
                    "supplier_name": p.supplier_name,
                    "purchase_date": p.purchase_date,
                    "total_amount": p.total_amount,
                    "currency_code": p.currency_code,
                    "currency_amount": p.currency_amount,
                    "currency_rate": p.currency_rate,
                    "created_at": p.created_at,
                    "items": [
                        {
                            "id": it.id,
                            "medicine_id": it.medicine_id,
                            "batch_no": it.batch_no,
                            "expiry_date": it.expiry_date,
                            "purchase_price": it.purchase_price,
                            "selling_price": it.selling_price,
                            "quantity": it.quantity
                        }
                        for it in p.items
                    ]
                }
                for p in paginated["items"]
            ],
            "pagination": paginated["pagination"]
        }
    }


# Get purchase by ID
@router.get("/{purchase_id}")
def get_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()

    if not purchase:
        return {
            "success": False,
            "message": "Purchase not found",
            "error": "NOT_FOUND"
        }

    return {
        "success": True,
        "message": "Purchase details fetched",
        "data": {
            "id": purchase.id,
            "invoice_number": purchase.invoice_number,
            "supplier_name": purchase.supplier_name,
            "purchase_date": purchase.purchase_date,
            "total_amount": purchase.total_amount,
            "currency_code": purchase.currency_code,
            "currency_amount": purchase.currency_amount,
            "currency_rate": purchase.currency_rate,
            "created_at": purchase.created_at,
            "items": [
                {
                    "id": item.id,
                    "medicine_id": item.medicine_id,
                    "batch_no": item.batch_no,
                    "expiry_date": item.expiry_date,
                    "purchase_price": item.purchase_price,
                    "selling_price": item.selling_price,
                    "quantity": item.quantity
                }
                for item in purchase.items
            ]
        }
    }
