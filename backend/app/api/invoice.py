from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import time
import random

from app.db.db import get_db
from app.core.deps import get_current_user
from app.models.sale import Sale
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/invoice", tags=["Invoice"])


@router.get("/sale/{sale_id}")
def download_sale_invoice(
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

    pdf_buffer = PDFService.generate_sale_invoice(sale)
    unique_id = f"{int(time.time())}{random.randint(100, 999)}"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{sale.invoice_number}_{unique_id}.pdf"
        }
    )
