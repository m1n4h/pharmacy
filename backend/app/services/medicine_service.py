from sqlalchemy.orm import Session
from app.models.medicine import Medicine
from app.utils.helpers import to_dict


class MedicineService:

    @staticmethod
    def create(db: Session, data):
        d = to_dict(data)
        existing = db.query(Medicine).filter(Medicine.name == d.get("name")).first()
        if existing:
            return None, "MEDICINE_EXISTS"

        med = Medicine(**d)
        db.add(med)
        db.commit()
        db.refresh(med)
        return med, None

    @staticmethod
    def get_all(db: Session):
        return db.query(Medicine).order_by(Medicine.id.desc()).all()

    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(Medicine).filter(Medicine.id == id).first()

    @staticmethod
    def update(db: Session, id: int, data):
        med = db.query(Medicine).filter(Medicine.id == id).first()
        if not med:
            return None, "NOT_FOUND"

        d = to_dict(data)
        for field, value in d.items():
            setattr(med, field, value)

        db.commit()
        db.refresh(med)
        return med, None

    @staticmethod
    def delete(db: Session, id: int):
        med = db.query(Medicine).filter(Medicine.id == id).first()
        if not med:
            return "NOT_FOUND"

        from sqlalchemy import text
        batch_ids = [b.id for b in med.batches]
        if batch_ids:
            placeholders = ",".join([f":b{i}" for i in range(len(batch_ids))])
            params = {f"b{i}": bid for i, bid in enumerate(batch_ids)}
            db.execute(text(f"DELETE FROM sale_items WHERE batch_id IN ({placeholders})"), params)

        db.delete(med)
        db.commit()
        return None
