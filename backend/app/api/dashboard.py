from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_current_user
from app.db.db import get_db
from app.services.dashboard_service import DashboardService
from app.models.medicine import Medicine
from app.models.supplier import Supplier
from app.models.sale import Sale
from app.models.sale_item import SaleItem


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Get grand total statistics (all time)
@router.get("/")
def get_dashboard_grand_totals(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = DashboardService.grand_total_summary(db)
    return {
        "success": True,
        "message": "Grand total statistics fetched successfully",
        "data": data
    }

# Get today's summary
@router.get("/today")
def get_dashboard_today(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = DashboardService.today_summary(db)
    return {
        "success": True,
        "message": "Today's summary fetched",
        "data": data
    }

# Get inventory summary
@router.get("/inventory")
def dashboard_inventory(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    data = DashboardService.inventory_summary(db)
    return {
        "success": True,
        "message": "Inventory summary fetched",
        "data": data
    }


