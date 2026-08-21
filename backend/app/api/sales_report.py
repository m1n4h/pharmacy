from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.core.deps import get_current_user
from app.db.db import get_db
from app.services.sales_report_service import SalesReportService
from app.services.dashboard_service import DashboardService
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.utils.pagination import Paginator

router = APIRouter(prefix="/reports/sales", tags=["Sales Reports"])

# Get daily sales report
@router.get("/daily")
def get_daily_sales(
    day: date = date.today(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = SalesReportService.daily_sales(db, day)

    return {
        "success": True,
        "message": "Daily sales report generated",
        "data": data
    }

# Get monthly sales report
@router.get("/monthly")
def get_monthly_sales(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    data = SalesReportService.monthly_sales(db, year, month)

    return {
        "success": True,
        "message": "Monthly sales report generated",
        "data": data
    }

# Get sales report for a specific medicine
@router.get("/medicine/{medicine_id}")
def get_sales_by_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    data, error = SalesReportService.sales_by_medicine(db, medicine_id)

    if error == "NOT_FOUND":
        return {
            "success": False,
            "message": "Medicine not found",
            "error": "NOT_FOUND"
        }

    return {
        "success": True,
        "message": "Sales report generated for medicine",
        "data": data
    }

# Get last 7 days sales summary
@router.get("/sales-7-days")
def get_last_7_days_sales(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = DashboardService.last_7_days_sales(db)
    return {
        "success": True,
        "message": "Last 7 days sales fetched",
        "data": data
    }

# NOTE: bare "/reports/sales" is served by app/api/report.py (period-based report).
# This router keeps /daily, /monthly, /medicine/{id}, /sales-7-days.


