from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, desc
from datetime import date, datetime, timedelta
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.purchase import Purchase
from app.models.batch import Batch
from app.models.medicine import Medicine
from app.models.supplier import Supplier
from app.models.expense import Expense
from app.services.currency_service import CurrencyService


class ReportService:

    @staticmethod
    def _period_bounds(period, date_from, date_to):
        today = date.today()
        if date_from and date_to:
            return date_from, date_to
        if period == "today":
            return today, today
        if period == "week":
            start = today - timedelta(days=today.weekday())
            return start, today
        if period == "month":
            return today.replace(day=1), today
        if period == "last_month":
            first = today.replace(day=1)
            last_month_end = first - timedelta(days=1)
            first_last = last_month_end.replace(day=1)
            return first_last, last_month_end
        if period == "3_months":
            start = today - timedelta(days=90)
            return start, today
        if period == "5_months":
            start = today - timedelta(days=150)
            return start, today
        if period == "6_months":
            start = today - timedelta(days=180)
            return start, today
        if period == "year":
            return today.replace(month=1, day=1), today
        if period == "5_years":
            start = today.replace(year=today.year - 5)
            return start, today
        if period == "custom" and date_from and date_to:
            return date_from, date_to
        # default: this month
        return today.replace(day=1), today

    @staticmethod
    def profit_loss(db: Session, period="month", date_from=None, date_to=None):
        df, dt = ReportService._period_bounds(period, date_from, date_to)

        revenue_rows = (
            db.query(Sale.sale_date, func.sum(Sale.total_amount), func.sum(Sale.discount_amount))
            .filter(and_(Sale.sale_date >= df, Sale.sale_date <= dt))
            .group_by(Sale.sale_date).order_by(Sale.sale_date).all()
        )
        revenue = sum(float(r[1]) or 0 for r in revenue_rows)
        discount = sum(float(r[2]) or 0 for r in revenue_rows)

        # COGS = sum(purchase_price * qty sold) for the period
        cogs = (
            db.query(
                func.sum(Batch.purchase_price * SaleItem.quantity)
            )
            .select_from(SaleItem)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .join(Batch, SaleItem.batch_id == Batch.id)
            .filter(and_(Sale.sale_date >= df, Sale.sale_date <= dt))
            .scalar()
        ) or 0.0

        expenses = ExpenseService_total(db, df, dt)

        gross_profit = revenue - cogs
        net_profit = gross_profit - expenses - discount
        margin = (net_profit / revenue * 100) if revenue > 0 else 0.0

        # monthly breakdown for chart
        monthly = {}
        for r in revenue_rows:
            key = str(r[0])[:7]
            monthly[key] = monthly.get(key, 0) + float(r[1])

        # monthly expenses breakdown
        expense_rows = (
            db.query(Expense.date, func.sum(Expense.amount))
            .filter(and_(Expense.date >= df, Expense.date <= dt))
            .group_by(Expense.date).order_by(Expense.date).all()
        )
        monthly_exp = {}
        for r in expense_rows:
            key = str(r[0])[:7]
            monthly_exp[key] = monthly_exp.get(key, 0) + float(r[1])

        return {
            "period": {"from": str(df), "to": str(dt)},
            "revenue": round(revenue, 2),
            "cogs": round(float(cogs), 2),
            "gross_profit": round(gross_profit, 2),
            "discount": round(float(discount), 2),
            "expenses": round(float(expenses), 2),
            "net_profit": round(net_profit, 2),
            "margin_percent": round(margin, 2),
            "monthly_revenue": [{"month": k, "amount": v} for k, v in sorted(monthly.items())],
            "monthly_expenses": [{"month": k, "amount": v} for k, v in sorted(monthly_exp.items())]
        }

    @staticmethod
    def sales_report(db: Session, period="month", date_from=None, date_to=None):
        df, dt = ReportService._period_bounds(period, date_from, date_to)
        rows = (
            db.query(
                Sale.sale_date,
                func.count(Sale.id),
                func.sum(Sale.total_amount)
            )
            .filter(and_(Sale.sale_date >= df, Sale.sale_date <= dt))
            .group_by(Sale.sale_date).order_by(Sale.sale_date).all()
        )
        return {
            "period": {"from": str(df), "to": str(dt)},
            "daily": [
                {"date": str(r[0]), "invoices": int(r[1]), "revenue": round(float(r[2]), 2)}
                for r in rows
            ],
            "total_revenue": round(sum(float(r[2]) for r in rows), 2),
            "total_invoices": sum(int(r[1]) for r in rows)
        }

    @staticmethod
    def inventory_report(db: Session):
        rows = (
            db.query(
                Medicine.id, Medicine.name, Medicine.category, func.coalesce(func.sum(Batch.quantity), 0)
            )
            .outerjoin(Batch, Medicine.id == Batch.medicine_id)
            .group_by(Medicine.id, Medicine.name, Medicine.category)
            .all()
        )
        low_stock = []
        dead_stock = []
        for r in rows:
            if r[3] == 0:
                dead_stock.append({"medicine_id": r[0], "name": r[1], "category": r[2], "quantity": 0})
            elif r[3] < 10:
                low_stock.append({"medicine_id": r[0], "name": r[1], "category": r[2], "quantity": int(r[3])})
        stock_value = db.query(func.sum(Batch.purchase_price * Batch.quantity)).scalar() or 0
        return {
            "low_stock": low_stock,
            "low_stock_count": len(low_stock),
            "dead_stock": dead_stock,
            "dead_stock_count": len(dead_stock),
            "total_stock_value": round(float(stock_value), 2)
        }

    @staticmethod
    def purchases_report(db: Session, period="month", date_from=None, date_to=None):
        df, dt = ReportService._period_bounds(period, date_from, date_to)
        rows = (
            db.query(
                Purchase.supplier_name, func.count(Purchase.id), func.sum(Purchase.total_amount)
            )
            .filter(and_(Purchase.purchase_date >= df, Purchase.purchase_date <= dt))
            .group_by(Purchase.supplier_name).all()
        )
        return {
            "period": {"from": str(df), "to": str(dt)},
            "by_supplier": [
                {"supplier": r[0] or "Unknown", "purchases": int(r[1]), "amount": round(float(r[2]), 2)}
                for r in rows
            ],
            "total": round(sum(float(r[2]) for r in rows), 2)
        }

    @staticmethod
    def expiry_report(db: Session, warning_days=30, critical_days=7):
        from app.services.expired_medicine_service import ExpiredMedicineService
        data = ExpiredMedicineService.get_expiry_data(db, warning_days, critical_days)
        return {
            "counts": data["counts"],
            "total_expired_value": round(data["total_expired_value"], 2),
            "total_expiring_soon_value": round(data["total_expiring_soon_value"], 2),
            "items": sorted(data["expired"] + data["critical"] + data["expiring_soon"], key=lambda x: x["days_remaining"])
        }

    @staticmethod
    def top_selling_medicines(db: Session, period="month", date_from=None, date_to=None, limit=10):
        df, dt = ReportService._period_bounds(period, date_from, date_to)
        rows = (
            db.query(
                Medicine.id,
                Medicine.name,
                Medicine.category,
                func.coalesce(func.sum(SaleItem.quantity), 0).label("qty_sold"),
                func.coalesce(func.sum(SaleItem.quantity * SaleItem.selling_price), 0).label("revenue"),
                func.count(func.distinct(SaleItem.sale_id)).label("transactions")
            )
            .join(SaleItem, Medicine.id == SaleItem.medicine_id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(and_(Sale.sale_date >= df, Sale.sale_date <= dt))
            .group_by(Medicine.id, Medicine.name, Medicine.category)
            .order_by(desc("qty_sold"))
            .limit(limit)
            .all()
        )
        return {
            "period": {"from": str(df), "to": str(dt)},
            "items": [
                {
                    "id": r.id, "name": r.name, "category": r.category,
                    "quantity_sold": int(r.qty_sold),
                    "revenue": round(float(r.revenue), 2),
                    "transactions": int(r.transactions)
                }
                for r in rows
            ]
        }

    @staticmethod
    def expense_trending(db: Session, period="month", date_from=None, date_to=None):
        df, dt = ReportService._period_bounds(period, date_from, date_to)
        total = ExpenseService_total(db, df, dt)
        rows = (
            db.query(
                Expense.category,
                func.coalesce(func.sum(Expense.amount), 0)
            )
            .filter(and_(Expense.date >= df, Expense.date <= dt))
            .group_by(Expense.category)
            .order_by(desc(func.sum(Expense.amount)))
            .all()
        )
        by_category = [
            {"category": r[0] or "Other", "amount": round(float(r[1]), 2)}
            for r in rows
        ]

        monthly = {}
        all_rows = (
            db.query(Expense.date, func.coalesce(func.sum(Expense.amount), 0))
            .filter(and_(Expense.date >= df, Expense.date <= dt))
            .group_by(Expense.date)
            .order_by(Expense.date)
            .all()
        )
        for r in all_rows:
            key = str(r[0])[:7]
            monthly[key] = round(monthly.get(key, 0) + float(r[1]), 2)

        return {
            "period": {"from": str(df), "to": str(dt)},
            "total": round(float(total), 2),
            "by_category": by_category,
            "monthly": [{"month": k, "amount": v} for k, v in sorted(monthly.items())]
        }

    @staticmethod
    def slow_moving_medicines(db, days_threshold=30):
        """Detect medicines that haven't sold in N days (slow-moving / sleeping stock)."""
        today = date.today()
        threshold_date = today - timedelta(days=days_threshold)

        # Get all medicines with total stock
        all_meds = (
            db.query(
                Medicine.id,
                Medicine.name,
                Medicine.category,
                Medicine.reorder_level,
                Medicine.max_stock_level,
                Medicine.last_sold_date,
                func.coalesce(func.sum(Batch.quantity), 0).label("total_stock")
            )
            .outerjoin(Batch, Medicine.id == Batch.medicine_id)
            .group_by(Medicine.id, Medicine.name, Medicine.category, Medicine.reorder_level, Medicine.max_stock_level, Medicine.last_sold_date)
            .all()
        )

        results = []
        for m in all_meds:
            last_sold = m.last_sold_date
            if last_sold:
                days_since = (today - last_sold).days
            else:
                days_since = 9999  # never sold

            if days_since >= days_threshold:
                if days_since >= 180:
                    status = "sleeping"
                elif days_since >= 91:
                    status = "very_slow"
                elif days_since >= 31:
                    status = "slow"
                else:
                    status = "normal"

                results.append({
                    "medicine_id": m.id,
                    "name": m.name,
                    "category": m.category,
                    "total_stock": int(m.total_stock),
                    "last_sold_date": str(last_sold) if last_sold else None,
                    "days_without_sale": days_since,
                    "status": status,
                    "reorder_level": m.reorder_level or 10,
                    "max_stock_level": m.max_stock_level or 100
                })

        results.sort(key=lambda x: x["days_without_sale"], reverse=True)
        return results

    @staticmethod
    def reorder_suggestions(db):
        """Generate reorder suggestions for medicines below reorder level."""
        today = date.today()
        meds = (
            db.query(
                Medicine.id,
                Medicine.name,
                Medicine.category,
                Medicine.reorder_level,
                Medicine.max_stock_level,
                func.coalesce(func.sum(Batch.quantity), 0).label("total_stock")
            )
            .outerjoin(Batch, Medicine.id == Batch.medicine_id)
            .group_by(Medicine.id, Medicine.name, Medicine.category, Medicine.reorder_level, Medicine.max_stock_level)
            .all()
        )

        suggestions = []
        for m in meds:
            reorder = m.reorder_level or 10
            max_stock = m.max_stock_level or 100
            stock = int(m.total_stock)

            if stock <= reorder:
                suggested_order = max_stock - stock
                status = "out_of_stock" if stock == 0 else "low_stock"
                suggestions.append({
                    "medicine_id": m.id,
                    "name": m.name,
                    "category": m.category,
                    "current_stock": stock,
                    "reorder_level": reorder,
                    "max_stock_level": max_stock,
                    "suggested_order": suggested_order,
                    "status": status
                })
            elif stock > max_stock:
                suggestions.append({
                    "medicine_id": m.id,
                    "name": m.name,
                    "category": m.category,
                    "current_stock": stock,
                    "reorder_level": reorder,
                    "max_stock_level": max_stock,
                    "suggested_order": 0,
                    "status": "overstock"
                })

        suggestions.sort(key=lambda x: x["current_stock"])
        return suggestions

    @staticmethod
    def overstock_report(db):
        """Detect overstocked medicines (quantity > max_stock_level)."""
        meds = (
            db.query(
                Medicine.id,
                Medicine.name,
                Medicine.category,
                Medicine.max_stock_level,
                func.coalesce(func.sum(Batch.quantity), 0).label("total_stock"),
                func.coalesce(func.sum(Batch.purchase_price * Batch.quantity), 0).label("stock_value")
            )
            .outerjoin(Batch, Medicine.id == Batch.medicine_id)
            .group_by(Medicine.id, Medicine.name, Medicine.category, Medicine.max_stock_level)
            .all()
        )

        overstocked = []
        for m in meds:
            max_stock = m.max_stock_level or 100
            stock = int(m.total_stock)
            if stock > max_stock:
                overstocked.append({
                    "medicine_id": m.id,
                    "name": m.name,
                    "category": m.category,
                    "current_stock": stock,
                    "max_stock_level": max_stock,
                    "excess": stock - max_stock,
                    "stock_value": round(float(m.stock_value), 2)
                })

        overstocked.sort(key=lambda x: x["excess"], reverse=True)
        return overstocked

    @staticmethod
    def supplier_performance(db, period="month", date_from=None, date_to=None):
        """Supplier performance report with delivery metrics."""
        df, dt = ReportService._period_bounds(period, date_from, date_to)

        # Group purchases by supplier
        rows = (
            db.query(
                Purchase.supplier_name,
                func.count(Purchase.id).label("total_orders"),
                func.sum(Purchase.total_amount).label("total_amount"),
                func.min(Purchase.purchase_date).label("first_order"),
                func.max(Purchase.purchase_date).label("last_order")
            )
            .filter(and_(Purchase.purchase_date >= df, Purchase.purchase_date <= dt))
            .group_by(Purchase.supplier_name)
            .all()
        )

        results = []
        for r in rows:
            results.append({
                "supplier": r.supplier_name or "Unknown",
                "total_orders": int(r.total_orders),
                "total_amount": round(float(r.total_amount), 2),
                "first_order": str(r.first_order),
                "last_order": str(r.last_order)
            })

        results.sort(key=lambda x: x["total_amount"], reverse=True)
        return {
            "period": {"from": str(df), "to": str(dt)},
            "suppliers": results
        }


def ExpenseService_total(db, df, dt):
    from app.services.expense_service import ExpenseService
    return ExpenseService.total_for_period(db, df, dt)
