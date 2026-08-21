from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_user
from app.db.db import get_db
from app.services.sale_service import SaleService
from app.models.sale import Sale
from app.models.medicine import Medicine
from app.models.batch import Batch
from app.schemas.sale import SaleCreate, SaleResponse, SaleUpdate
from app.utils.pagination import Paginator


router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("/pos/medicines")
def get_pos_medicines(
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all medicines with available stock for POS system
    """
    from sqlalchemy import func
    from datetime import date

    # Earliest-expiry (FIFO) batch per medicine -> gives the price that will actually be charged
    fifo_batch = db.query(
        Batch.medicine_id.label("medicine_id"),
        Batch.selling_price.label("price"),
        Batch.expiry_date.label("expiry_date"),
        func.row_number().over(
            partition_by=Batch.medicine_id,
            order_by=(Batch.expiry_date.asc(), Batch.id.asc())
        ).label("rn")
    ).filter(
        Batch.quantity > 0,
        Batch.expiry_date >= date.today()
    ).subquery()

    query = (
        db.query(
            Medicine.id,
            Medicine.name,
            Medicine.generic_name,
            Medicine.brand,
            Medicine.category,
            Medicine.strength,
            Medicine.barcode,
            fifo_batch.c.expiry_date,
            fifo_batch.c.price,
            func.sum(Batch.quantity).label("total_quantity")
        )
        .join(Batch, Medicine.id == Batch.medicine_id)
        .join(fifo_batch, (fifo_batch.c.medicine_id == Medicine.id) & (fifo_batch.c.rn == 1))
        .filter(
            Batch.quantity > 0,
            Batch.expiry_date >= date.today()
        )
        .group_by(
            Medicine.id,
            Medicine.name,
            Medicine.generic_name,
            Medicine.brand,
            Medicine.category,
            Medicine.strength,
            Medicine.barcode,
            fifo_batch.c.expiry_date,
            fifo_batch.c.price
        )
        .having(func.sum(Batch.quantity) > 0)
    )
    
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Medicine.name.ilike(s)) |
            (Medicine.generic_name.ilike(s))
        )
    
    query = query.order_by(Medicine.name)
    
    paginated = Paginator.paginate(query, page, limit)
    
    medicines_list = [
        {
            "id": m.id,
            "name": m.name,
            "generic_name": m.generic_name,
            "brand": m.brand,
            "category": m.category,
            "strength": m.strength,
            "price": float(m.price),
            "expiry_date": str(m.expiry_date),
            "barcode": m.barcode,
            "quantity": int(m.total_quantity)
        }
        for m in paginated["items"]
    ]
    
    return {
        "success": True,
        "message": "POS medicines fetched successfully",
        "data": {
            "items": medicines_list,
            "pagination": paginated["pagination"]
        }
    }


@router.post("/create")
def create_sale(
    payload: SaleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a sale. Request schema should match app/schemas/sale.SaleCreate.
    Business errors are returned with consistent JSON format.
    """
    try:
        sale = SaleService.create_sale(db, payload)
    except Exception as exc:
        # Known business error strings from service or Python exceptions are returned cleanly
        message = str(exc)
        # If it's a stock / batch problem, return 400 with structured error
        return {
            "success": False,
            "message": message,
            "error": "BUSINESS_ERROR"
        }

    # format response
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="sales",
        details=f"Sale {sale.invoice_number} for {sale.customer_name} "
                f"(total {sale.total_amount})",
        user=current_user
    )

    return {
        "success": True,
        "message": "Sale created successfully",
        "data": {
            "id": sale.id,
            "invoice_number": sale.invoice_number,
            "customer_name": sale.customer_name,
            "sale_date": sale.sale_date,
            "subtotal": sale.subtotal,
            "discount_amount": sale.discount_amount,
            "total_amount": sale.total_amount,
            "created_at": sale.created_at,
            "items": [
                {
                    "id": it.id,
                    "medicine_id": it.medicine_id,
                    "batch_id": it.batch_id,
                    "quantity": it.quantity,
                    "selling_price": it.selling_price
                }
                for it in sale.items
            ]
        }
    }

@router.post("/bulk-create")
def create_multiple_sales(
    sales: List[SaleCreate],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    created_sales = []
    errors = []
    
    for i, sale_data in enumerate(sales):
        try:
            sale = SaleService.create_sale(db, sale_data)
            created_sales.append({
                "id": sale.id,
                "invoice_number": sale.invoice_number,
                "customer_name": sale.customer_name,
                "sale_date": sale.sale_date,
                "total_amount": sale.total_amount
            })
        except Exception as e:
            errors.append({
                "index": i,
                "invoice_number": getattr(sale_data, 'invoice_number', None),
                "error": str(e)
            })
    
    return {
        "success": len(errors) == 0,
        "message": f"Created {len(created_sales)} sales" + (f", {len(errors)} failed" if errors else ""),
        "data": {
            "created": created_sales,
            "errors": errors,
            "summary": {
                "total_requested": len(sales),
                "created_count": len(created_sales),
                "error_count": len(errors)
            }
        }
    }

@router.get("/")
def list_sales(
    search: str | None = None,    # invoice or customer
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Sale)

    if search:
        s = f"%{search}%"
        query = query.filter(
            (Sale.invoice_number.ilike(s)) |
            (Sale.customer_name.ilike(s))
        )

    query = query.order_by(Sale.created_at.desc())
    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Sales fetched",
        "data": {
            "items": [
                {
                    "id": s.id,
                    "invoice_number": s.invoice_number,
                    "customer_name": s.customer_name,
                    "sale_date": s.sale_date,
                    "subtotal": s.subtotal,
                    "discount_amount": s.discount_amount,
                    "total_amount": s.total_amount,
                    "created_at": s.created_at,
                    "items": [
                        {
                            "id": it.id,
                            "medicine_id": it.medicine_id,
                            "batch_id": it.batch_id,
                            "quantity": it.quantity,
                            "selling_price": it.selling_price
                        }
                        for it in s.items
                    ]
                }
                for s in paginated["items"]
            ],
            "pagination": paginated["pagination"]
        }
    }

@router.get("/{sale_id}")
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()

    if not sale:
        return {
            "success": False,
            "message": "Sale not found",
            "error": "NOT_FOUND"
        }

    # Get medicine details for each item
    items_with_medicine = []
    for item in sale.items:
        medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        items_with_medicine.append({
            "id": item.id,
            "medicine_id": item.medicine_id,
            "medicine_name": medicine.name if medicine else None,
            "medicine_strength": medicine.strength if medicine else None,
            "batch_id": item.batch_id,
            "quantity": item.quantity,
            "selling_price": item.selling_price
        })

    return {
        "success": True,
        "message": "Sale details fetched",
        "data": {
            "id": sale.id,
            "invoice_number": sale.invoice_number,
            "customer_name": sale.customer_name,
            "sale_date": sale.sale_date,
            "subtotal": sale.subtotal,
            "discount_amount": sale.discount_amount,
            "total_amount": sale.total_amount,
            "created_at": sale.created_at,
            "items": items_with_medicine
        }
    }


@router.put("/{sale_id}")
def update_sale(
    sale_id: int,
    payload: SaleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        sale = SaleService.update_sale(db, sale_id, payload)
    except Exception as exc:
        return {"success": False, "message": str(exc), "error": "UPDATE_FAILED"}
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="sales",
        details=f"Updated sale {sale.invoice_number}",
        user=current_user
    )
    return {"success": True, "message": "Sale updated", "data": {"id": sale.id, "total_amount": sale.total_amount}}


@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        SaleService.delete_sale(db, sale_id)
    except Exception as exc:
        return {"success": False, "message": str(exc), "error": "DELETE_FAILED"}
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DELETE", module="sales",
        details=f"Deleted sale #{sale_id} (stock restored)",
        user=current_user
    )
    return {"success": True, "message": "Sale deleted and stock restored"}
