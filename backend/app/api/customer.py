from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.db import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.customer_service import CustomerService
from app.utils.pagination import Paginator


router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/create")
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    customer = CustomerService.create(db, payload)

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="customers",
        details=f"Customer: {customer.name}",
        user=current_user
    )

    return {
        "success": True,
        "message": "Customer created successfully",
        "data": customer
    }


@router.get("/")
def list_customers(
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Customer)

    if search:
        s = f"%{search}%"
        query = query.filter(
            Customer.name.ilike(s) | Customer.phone.ilike(s)
        )

    query = query.order_by(Customer.name)
    paginated = Paginator.paginate(query, page, limit)

    return {
        "success": True,
        "message": "Customers fetched successfully",
        "data": {
            "items": paginated["items"],
            "pagination": paginated["pagination"]
        }
    }


@router.get("/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    customer = CustomerService.get_by_id(db, customer_id)

    if not customer:
        return {"success": False, "message": "Customer not found", "error": "NOT_FOUND"}

    from app.models.sale import Sale
    sales = db.query(Sale).filter(Sale.customer_id == customer_id).order_by(Sale.created_at.desc()).all()

    return {
        "success": True,
        "message": "Customer fetched successfully",
        "data": {
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "email": customer.email,
            "address": customer.address,
            "gender": customer.gender,
            "date_of_birth": customer.date_of_birth,
            "notes": customer.notes,
            "total_purchases": customer.total_purchases,
            "total_spent": customer.total_spent,
            "created_at": customer.created_at,
            "purchase_history": [
                {
                    "id": s.id,
                    "invoice_number": s.invoice_number,
                    "sale_date": s.sale_date,
                    "total_amount": s.total_amount,
                    "payment_method": s.payment_method
                }
                for s in sales
            ]
        }
    }


@router.put("/{customer_id}")
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    customer = CustomerService.update(db, customer_id, payload)

    if not customer:
        return {"success": False, "message": "Customer not found", "error": "NOT_FOUND"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="customers",
        details=f"Updated customer #{customer_id} ({customer.name})",
        user=current_user
    )

    return {
        "success": True,
        "message": "Customer updated successfully",
        "data": customer
    }


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    customer = CustomerService.delete(db, customer_id)

    if not customer:
        return {"success": False, "message": "Customer not found", "error": "NOT_FOUND"}

    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DELETE", module="customers",
        details=f"Deleted customer #{customer_id} ({customer.name})",
        user=current_user
    )

    return {"success": True, "message": "Customer deleted successfully"}
