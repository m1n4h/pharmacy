import io
import csv
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from app.core.deps import get_current_user
from app.db.db import get_db
from app.services.report_service import ReportService
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/reports", tags=["Reports"])


def _csv_response(rows, filename):
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    else:
        output.write("No data")
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
    )


@router.get("/profit-loss")
def profit_loss(
    period: str = "month",
    date_from: date = None,
    date_to: date = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = ReportService.profit_loss(db, period, date_from, date_to)
    return {"success": True, "message": "Profit & Loss", "data": data}


@router.get("/sales")
def sales_report(
    period: str = "month",
    date_from: date = None,
    date_to: date = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return {"success": True, "message": "Sales report", "data": ReportService.sales_report(db, period, date_from, date_to)}


@router.get("/inventory")
def inventory_report(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return {"success": True, "message": "Inventory report", "data": ReportService.inventory_report(db)}


@router.get("/purchases")
def purchases_report(
    period: str = "month",
    date_from: date = None,
    date_to: date = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return {"success": True, "message": "Purchases report", "data": ReportService.purchases_report(db, period, date_from, date_to)}


@router.get("/expiry")
def expiry_report(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    s = SettingsService.get_settings(db)
    wd = (getattr(s, "expiry_warning_days", None) if s else None) or 30
    return {"success": True, "message": "Expiry report", "data": ReportService.expiry_report(db, wd, 7)}


@router.get("/export/{report_type}")
def export_report(
    report_type: str,
    period: str = "month",
    date_from: date = None,
    date_to: date = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if report_type == "sales":
        d = ReportService.sales_report(db, period, date_from, date_to)
        rows = [
            {"date": r["date"], "invoices": r["invoices"], "revenue": r["revenue"]}
            for r in d["daily"]
        ]
    elif report_type == "inventory":
        d = ReportService.inventory_report(db)
        rows = [
            {"medicine": r["name"], "category": r["category"], "quantity": r["quantity"]}
            for r in (d["low_stock"] + d["dead_stock"])
        ]
    elif report_type == "purchases":
        d = ReportService.purchases_report(db, period, date_from, date_to)
        rows = [
            {"supplier": r["supplier"], "purchases": r["purchases"], "amount": r["amount"]}
            for r in d["by_supplier"]
        ]
    elif report_type == "expiry":
        s = SettingsService.get_settings(db)
        wd = (s.get("expiry_warning_days") if s else None) or 30
        d = ReportService.expiry_report(db, wd, 7)
        rows = [
            {
                "batch_no": r["batch_no"], "quantity": r["quantity"],
                "expiry_date": r["expiry_date"], "days_remaining": r["days_remaining"],
                "stock_value": round(r["stock_value"], 2)
            }
            for r in d["items"]
        ]
    else:
        rows = []
    return _csv_response(rows, f"{report_type}_report")
