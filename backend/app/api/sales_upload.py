"""
Sales Document Upload API
Allows admins to upload sales documents (PDF, DOCX, CSV, Excel, Images).
Extracts data, validates, and creates sale records.
"""
import os
import json
from datetime import datetime, date
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_current_user
from app.db.db import get_db
from app.models.medicine import Medicine
from app.models.batch import Batch
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.upload_log import SalesUploadLog
from app.services.document_parser import DocumentParser
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = "/tmp/pharma_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-document")
async def upload_sales_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ("admin", "superadmin"):
        return JSONResponse(
            status_code=403,
            content={"success": False, "message": "Only administrators can upload documents"}
        )

    ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in DocumentParser.ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": f"File type '{ext}' not supported"}
        )

    content = await file.read()
    if len(content) > DocumentParser.MAX_FILE_SIZE:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "File too large. Maximum 10MB."}
        )

    log = SalesUploadLog(
        user_id=current_user.id,
        filename=file.filename,
        file_type=ext,
        file_size=len(content),
        status="processing"
    )
    db.add(log)
    db.flush()

    result = DocumentParser.parse(content, file.filename)

    if not result.get("success"):
        log.status = "failed"
        log.errors = result.get("error", "Unknown error")
        db.commit()
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": result.get("error", "Parse failed")}
        )

    extracted = result.get("data", [])
    log.rows_extracted = len(extracted)

    for rec in extracted:
        for item in rec.get("items", []):
            med = _find_medicine(db, item.get("medicine_name", ""))
            if med:
                item["medicine_id"] = med.id
                item["matched_name"] = med.name
                batch = _find_batch(db, med.id)
                if batch:
                    item["batch_id"] = batch.id
                    item["available_stock"] = batch.quantity
                    item["selling_price"] = float(batch.selling_price) if batch.selling_price else 0
                    item["stock_status"] = "ok"
                    if item.get("quantity", 1) > batch.quantity:
                        item["stock_status"] = "insufficient"
                        item["stock_note"] = f"Requested {item['quantity']}, only {batch.quantity} available"
                else:
                    item["stock_status"] = "out_of_stock"
                    item["stock_note"] = "No active batch with stock"
            else:
                item["stock_status"] = "not_found"
                item["stock_note"] = f"Medicine '{item.get('medicine_name')}' not found in system"

    log.errors = json.dumps(extracted)
    db.commit()

    return {
        "success": True,
        "message": f"File parsed. Found {len(extracted)} sale record(s).",
        "data": {
            "upload_id": log.id,
            "filename": file.filename,
            "records": extracted,
            "row_count": result.get("row_count", len(extracted))
        }
    }


@router.post("/process-upload/{upload_id}")
def process_uploaded_sales(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role not in ("admin", "superadmin"):
        return JSONResponse(
            status_code=403,
            content={"success": False, "message": "Only administrators can process uploads"}
        )

    log = db.query(SalesUploadLog).filter(SalesUploadLog.id == upload_id).first()
    if not log:
        return JSONResponse(status_code=404, content={"success": False, "message": "Upload not found"})

    if log.status == "processed":
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "This upload was already processed"}
        )

    sales_data = _get_pending_data(log)
    if not sales_data:
        log.status = "failed"
        log.errors = json.dumps({"error": "No pending data to process"})
        db.commit()
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "No data to process"}
        )

    created = 0
    errors = []

    for idx, sale_record in enumerate(sales_data):
        try:
            items_data = []
            for item in sale_record.get("items", []):
                if item.get("stock_status") in ("not_found", "out_of_stock"):
                    errors.append(f"Row {idx+1}: {item.get('stock_note', 'Medicine not available')}")
                    continue
                if item.get("stock_status") == "insufficient":
                    qty = item.get("available_stock", item.get("quantity", 1))
                else:
                    qty = item.get("quantity", 1)
                if qty <= 0:
                    continue
                items_data.append({
                    "medicine_id": item["medicine_id"],
                    "medicine_name": item.get("matched_name", item.get("medicine_name")),
                    "batch_id": item.get("batch_id"),
                    "quantity": qty,
                    "price": item.get("selling_price", 0)
                })

            if not items_data:
                continue

            sale_obj = Sale(
                invoice_number=f"UP-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                customer_name=sale_record.get("customer_name", "Walk-in Customer"),
                sale_date=_parse_date(sale_record.get("sale_date", date.today().isoformat())),
                subtotal=sum(i["quantity"] * i["price"] for i in items_data),
                discount_amount=0,
                total_amount=sum(i["quantity"] * i["price"] for i in items_data),
                created_at=datetime.now()
            )
            db.add(sale_obj)
            db.flush()

            for item in items_data:
                si = SaleItem(
                    sale_id=sale_obj.id,
                    medicine_id=item["medicine_id"],
                    batch_id=item.get("batch_id"),
                    quantity=item["quantity"],
                    selling_price=item["price"]
                )
                db.add(si)

                if item.get("batch_id"):
                    batch = db.query(Batch).filter(Batch.id == item["batch_id"]).first()
                    if batch:
                        batch.quantity -= item["quantity"]

            created += 1
        except Exception as e:
            errors.append(f"Row {idx+1}: {str(e)}")

    log.status = "processed" if created > 0 else "failed"
    log.sales_created = created
    log.errors = json.dumps(errors) if errors else None
    db.commit()

    ActivityService.log(
        db, action="UPLOAD", module="sales",
        details=f"Uploaded {log.filename}: {created} sale(s) created, {len(errors)} error(s)",
        user=current_user
    )

    return {
        "success": True,
        "message": f"Processed: {created} sale(s) created, {len(errors)} error(s)",
        "data": {
            "upload_id": log.id,
            "sales_created": created,
            "errors": errors
        }
    }


@router.get("/upload-logs")
def list_upload_logs(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(SalesUploadLog).order_by(SalesUploadLog.created_at.desc())
    total = query.count()
    logs = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "success": True,
        "data": {
            "items": [
                {
                    "id": l.id,
                    "filename": l.filename,
                    "file_type": l.file_type,
                    "file_size": l.file_size,
                    "rows_extracted": l.rows_extracted,
                    "sales_created": l.sales_created,
                    "status": l.status,
                    "errors": l.errors,
                    "created_at": l.created_at.isoformat() if l.created_at else None,
                }
                for l in logs
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    }


def _find_medicine(db: Session, name: str):
    name = name.strip()
    med = db.query(Medicine).filter(func.lower(Medicine.name) == name.lower()).first()
    if med:
        return med
    med = db.query(Medicine).filter(Medicine.name.ilike(f"%{name}%")).first()
    return med


def _find_batch(db: Session, medicine_id: int):
    return db.query(Batch).filter(
        Batch.medicine_id == medicine_id,
        Batch.expiry_date >= date.today(),
        Batch.quantity > 0
    ).order_by(Batch.expiry_date.asc()).first()


def _parse_date(date_str: str) -> date:
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except (ValueError, TypeError):
            continue
    return date.today()


def _get_pending_data(log: SalesUploadLog) -> list:
    if log.errors:
        try:
            return json.loads(log.errors)
        except (json.JSONDecodeError, TypeError):
            return []
    return []
