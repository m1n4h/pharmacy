from sqlalchemy.orm import Session
from datetime import datetime
from app.models.disposal import Disposal
from app.models.batch import Batch


class DisposalService:

    @staticmethod
    def generate_disposal_number(db: Session) -> str:
        today = datetime.now().strftime("%Y%m%d")
        count = db.query(Disposal).filter(Disposal.disposal_number.like(f"DIS-{today}-%")).count()
        return f"DIS-{today}-{count + 1:03d}"

    @staticmethod
    def create_disposal(db: Session, data: dict, user_id: int) -> dict:
        disposal_number = DisposalService.generate_disposal_number(db)
        disposal = Disposal(
            disposal_number=disposal_number,
            medicine_id=data["medicine_id"],
            batch_id=data["batch_id"],
            quantity=data["quantity"],
            disposal_method=data.get("disposal_method", "incineration"),
            reason=data.get("reason"),
            estimated_value=data.get("estimated_value", 0),
            witness_name=data.get("witness_name"),
            witness_title=data.get("witness_title"),
            certificate_number=data.get("certificate_number"),
            tmda_reference=data.get("tmda_reference"),
            disposal_date=data.get("disposal_date"),
            notes=data.get("notes"),
            disposed_by=user_id,
        )
        db.add(disposal)
        db.commit()
        db.refresh(disposal)
        return {
            "id": disposal.id,
            "disposal_number": disposal.disposal_number,
            "status": disposal.status,
        }

    @staticmethod
    def get_disposals(db: Session, limit: int = 100):
        items = db.query(Disposal).order_by(Disposal.created_at.desc()).limit(limit).all()
        return [
            {
                "id": d.id,
                "disposal_number": d.disposal_number,
                "medicine_id": d.medicine_id,
                "batch_id": d.batch_id,
                "quantity": d.quantity,
                "disposal_method": d.disposal_method,
                "reason": d.reason,
                "estimated_value": d.estimated_value,
                "witness_name": d.witness_name,
                "certificate_number": d.certificate_number,
                "tmda_reference": d.tmda_reference,
                "status": d.status,
                "disposal_date": str(d.disposal_date) if d.disposal_date else None,
                "created_at": str(d.created_at) if d.created_at else None,
            }
            for d in items
        ]

    @staticmethod
    def approve_disposal(db: Session, disposal_id: int, approved_by: int) -> dict:
        disposal = db.query(Disposal).filter(Disposal.id == disposal_id).first()
        if not disposal:
            raise ValueError("Disposal not found")
        disposal.status = "approved"
        disposal.approved_by = approved_by
        # Zero out the batch quantity
        batch = db.query(Batch).filter(Batch.id == disposal.batch_id).first()
        if batch:
            batch.status = "disposed"
            batch.quantity = 0
        db.commit()
        return {"id": disposal.id, "status": disposal.status}

    @staticmethod
    def dispose(db: Session, disposal_id: int) -> dict:
        disposal = db.query(Disposal).filter(Disposal.id == disposal_id).first()
        if not disposal:
            raise ValueError("Disposal not found")
        disposal.status = "disposed"
        disposal.disposal_date = datetime.now()
        db.commit()
        return {"id": disposal.id, "status": disposal.status}
