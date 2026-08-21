from sqlalchemy.orm import Session
from app.models.batch import Batch

class BatchService:

    @staticmethod
    def create(db: Session, data):
        batch = Batch(**data.dict())
        db.add(batch)
        db.commit()
        db.refresh(batch)
        return batch, None

    @staticmethod
    def get_by_id(db: Session, batch_id: int):
        return db.query(Batch).filter(Batch.id == batch_id).first()

    @staticmethod
    def get_by_medicine(db: Session, medicine_id: int):
        return db.query(Batch).filter(Batch.medicine_id == medicine_id).order_by(Batch.expiry_date).all()

    @staticmethod
    def update(db: Session, batch_id: int, data):
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            return None, "NOT_FOUND"

        for field, value in data.dict(exclude_unset=True).items():
            setattr(batch, field, value)

        db.commit()
        db.refresh(batch)
        return batch, None

    @staticmethod
    def delete(db: Session, batch_id: int):
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            return "NOT_FOUND"

        db.delete(batch)
        db.commit()
        return None
