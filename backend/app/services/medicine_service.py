from sqlalchemy.orm import Session
from app.models.medicine import Medicine


class MedicineService:

    @staticmethod
    def create(db: Session, data):
        # Check duplicate medicine by name
        existing = db.query(Medicine).filter(Medicine.name == data.name).first()
        if existing:
            return None, "MEDICINE_EXISTS"

        med = Medicine(**data.dict())
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

        for field, value in data.dict(exclude_unset=True).items():
            setattr(med, field, value)

        db.commit()
        db.refresh(med)
        return med, None

    @staticmethod
    def delete(db: Session, id: int):
        med = db.query(Medicine).filter(Medicine.id == id).first()
        if not med:
            return "NOT_FOUND"

        db.delete(med)
        db.commit()
        return None
