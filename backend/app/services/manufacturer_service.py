from sqlalchemy.orm import Session
from app.models.manufacturer import Manufacturer
from app.utils.helpers import to_dict


class ManufacturerService:

    @staticmethod
    def create(db: Session, data):
        d = to_dict(data)
        manufacturer = Manufacturer(**d)
        db.add(manufacturer)
        db.commit()
        db.refresh(manufacturer)
        return manufacturer

    @staticmethod
    def get_all(db: Session):
        return db.query(Manufacturer).order_by(Manufacturer.name).all()

    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(Manufacturer).filter(Manufacturer.id == id).first()

    @staticmethod
    def update(db: Session, id: int, data):
        manufacturer = db.query(Manufacturer).filter(Manufacturer.id == id).first()
        if not manufacturer:
            return None

        d = to_dict(data)
        for field, value in d.items():
            setattr(manufacturer, field, value)

        db.commit()
        db.refresh(manufacturer)
        return manufacturer

    @staticmethod
    def delete(db: Session, id: int):
        manufacturer = db.query(Manufacturer).filter(Manufacturer.id == id).first()
        if not manufacturer:
            return None

        db.delete(manufacturer)
        db.commit()
        return manufacturer
