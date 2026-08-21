from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, datetime
from app.models.expired_medicine_action import ExpiredMedicineAction
from app.models.batch import Batch
from app.utils.pagination import Paginator


class ExpiredMedicineService:

    @staticmethod
    def record_action(db: Session, payload, user=None):
        action = ExpiredMedicineAction(
            action_type=payload.action_type,
            medicine_id=payload.medicine_id,
            medicine_name=payload.medicine_name,
            batch_no=payload.batch_no,
            batch_id=payload.batch_id,
            quantity=payload.quantity,
            expiry_date=payload.expiry_date,
            reason=payload.reason,
            responsible_person=payload.responsible_person,
            notes=payload.notes,
            created_at=datetime.now()
        )
        db.add(action)
        # update batch status
        if payload.batch_id:
            batch = db.query(Batch).filter(Batch.id == payload.batch_id).first()
            if batch:
                if payload.action_type == "quarantine":
                    batch.status = "quarantined"
                elif payload.action_type == "dispose":
                    batch.status = "disposed"
                    batch.quantity = 0
                elif payload.action_type == "return":
                    batch.status = "returned"
                    batch.quantity = 0
        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def list_actions(db: Session, page=1, limit=20):
        query = db.query(ExpiredMedicineAction).order_by(desc(ExpiredMedicineAction.created_at))
        return Paginator.paginate(query, page, limit)

    @staticmethod
    def get_expiry_data(db: Session, warning_days=30, critical_days=7):
        """Return expiry status breakdown for all batches with quantity > 0."""
        batches = db.query(Batch).filter(Batch.quantity > 0).all()
        today = date.today()
        result = {
            "expired": [],
            "critical": [],
            "expiring_soon": [],
            "safe": [],
            "total_expired_value": 0.0,
            "total_expiring_soon_value": 0.0,
            "counts": {"expired": 0, "critical": 0, "expiring_soon": 0, "safe": 0}
        }
        for b in batches:
            if not b.expiry_date:
                continue
            days = (b.expiry_date - today).days
            stock_value = b.purchase_price * b.quantity
            entry = {
                "batch_id": b.id,
                "batch_no": b.batch_no,
                "medicine_id": b.medicine_id,
                "medicine_name": b.medicine.name if b.medicine else None,
                "quantity": b.quantity,
                "expiry_date": str(b.expiry_date),
                "days_remaining": days,
                "purchase_price": b.purchase_price,
                "selling_price": b.selling_price,
                "stock_value": stock_value,
                "status": b.status
            }
            if b.expiry_date < today:
                result["expired"].append(entry)
                result["counts"]["expired"] += 1
                result["total_expired_value"] += stock_value
            elif days <= critical_days:
                result["critical"].append(entry)
                result["counts"]["critical"] += 1
                result["total_expiring_soon_value"] += stock_value
            elif days <= warning_days:
                result["expiring_soon"].append(entry)
                result["counts"]["expiring_soon"] += 1
                result["total_expiring_soon_value"] += stock_value
            else:
                result["safe"].append(entry)
                result["counts"]["safe"] += 1
        return result

    @staticmethod
    def dashboard(db: Session, warning_days=30, critical_days=7):
        data = ExpiredMedicineService.get_expiry_data(db, warning_days, critical_days)
        return {
            "success": True,
            "message": "Expiry dashboard",
            "data": {
                "counts": data["counts"],
                "total_expired_value": round(data["total_expired_value"], 2),
                "total_expiring_soon_value": round(data["total_expiring_soon_value"], 2),
                "expired": data["expired"][:10],
                "critical": data["critical"][:10],
                "expiring_soon": data["expiring_soon"][:10]
            }
        }
