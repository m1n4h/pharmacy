from sqlalchemy.orm import Session
from app.models.supplier import Supplier


class SupplierService:

    @staticmethod
    def create_supplier(db: Session, data):
        supplier = Supplier(**data.dict())
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        return supplier
