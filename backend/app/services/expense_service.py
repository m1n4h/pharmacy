from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime
from app.models.expense import Expense
from app.utils.pagination import Paginator
from app.utils.helpers import to_dict, get_attr


class ExpenseService:

    @staticmethod
    def create_expense(db: Session, data):
        d = to_dict(data)
        expense = Expense(
            category=d.get("category"),
            description=d.get("description"),
            amount=d.get("amount"),
            date=d.get("date"),
            payment_method=d.get("payment_method"),
            reference=d.get("reference"),
            notes=d.get("notes"),
            created_at=datetime.now()
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense

    @staticmethod
    def list_expenses(db: Session, search=None, category=None, date_from=None, date_to=None, page=1, limit=20):
        query = db.query(Expense)
        if search:
            s = f"%{search}%"
            query = query.filter(
                (Expense.description.ilike(s)) | (Expense.reference.ilike(s)) | (Expense.category.ilike(s))
            )
        if category:
            query = query.filter(Expense.category == category)
        if date_from:
            query = query.filter(Expense.date >= date_from)
        if date_to:
            query = query.filter(Expense.date <= date_to)
        query = query.order_by(Expense.date.desc())
        return Paginator.paginate(query, page, limit)

    @staticmethod
    def get_expense(db: Session, expense_id: int):
        return db.query(Expense).filter(Expense.id == expense_id).first()

    @staticmethod
    def delete_expense(db: Session, expense_id: int):
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return None
        db.delete(expense)
        db.commit()
        return expense

    @staticmethod
    def update_expense(db: Session, expense_id: int, data):
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return None
        d = to_dict(data)
        for field, value in d.items():
            if value is not None:
                setattr(expense, field, value)
        db.commit()
        db.refresh(expense)
        return expense

    @staticmethod
    def summary(db: Session, date_from=None, date_to=None):
        query = db.query(Expense)
        if date_from:
            query = query.filter(Expense.date >= date_from)
        if date_to:
            query = query.filter(Expense.date <= date_to)
        expenses = query.all()
        total = sum(e.amount for e in expenses)
        by_category = {}
        for e in expenses:
            by_category[e.category] = by_category.get(e.category, 0) + e.amount
        return {"total": total, "by_category": by_category, "count": len(expenses)}

    @staticmethod
    def total_for_period(db: Session, date_from, date_to):
        total = db.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
            and_(Expense.date >= date_from, Expense.date <= date_to)
        ).scalar()
        return float(total)
