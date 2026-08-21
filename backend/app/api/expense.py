from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.core.deps import get_current_user
from app.db.db import get_db
from app.schemas.expense import ExpenseCreate, ExpenseUpdate  # noqa
from app.services.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/create")
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    expense = ExpenseService.create_expense(db, payload)
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="CREATE", module="expenses",
        details=f"Expense: {expense.category} {expense.amount}",
        user=current_user
    )
    return {
        "success": True,
        "message": "Expense recorded",
        "data": {
            "id": expense.id,
            "category": expense.category,
            "amount": expense.amount,
            "date": expense.date
        }
    }


@router.get("/")
def list_expenses(
    search: str = None,
    category: str = None,
    date_from: date = None,
    date_to: date = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = ExpenseService.list_expenses(db, search, category, date_from, date_to, page, limit)
    return {
        "success": True,
        "message": "Expenses fetched",
        "data": {
            "items": [
                {
                    "id": e.id,
                    "category": e.category,
                    "description": e.description,
                    "amount": e.amount,
                    "date": e.date,
                    "payment_method": e.payment_method,
                    "reference": e.reference,
                    "notes": e.notes
                }
                for e in result["items"]
            ],
            "pagination": result["pagination"]
        }
    }


@router.get("/summary")
def expense_summary(
    date_from: date = None,
    date_to: date = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = ExpenseService.summary(db, date_from, date_to)
    return {"success": True, "message": "Summary fetched", "data": result}


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    expense = ExpenseService.delete_expense(db, expense_id)
    if not expense:
        return {"success": False, "message": "Expense not found", "error": "NOT_FOUND"}
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="DELETE", module="expenses",
        details=f"Deleted expense #{expense_id} ({expense.category})",
        user=current_user
    )
    return {"success": True, "message": "Expense deleted"}


@router.put("/{expense_id}")
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    expense = ExpenseService.update_expense(db, expense_id, payload)
    if not expense:
        return {"success": False, "message": "Expense not found", "error": "NOT_FOUND"}
    from app.services.activity_service import ActivityService
    ActivityService.log(
        db, action="UPDATE", module="expenses",
        details=f"Updated expense #{expense_id} ({expense.category})",
        user=current_user
    )
    return {
        "success": True,
        "message": "Expense updated",
        "data": {
            "id": expense.id,
            "category": expense.category,
            "amount": expense.amount,
            "date": expense.date
        }
    }
