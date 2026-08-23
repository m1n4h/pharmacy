from sqlalchemy.orm import Session
from app.models.supplier import Supplier
from app.utils.helpers import to_dict


class SupplierService:

    @staticmethod
    def create_supplier(db: Session, data):
        d = to_dict(data)
        supplier = Supplier(**d)
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        return supplier

    @staticmethod
    def update_supplier(db: Session, supplier_id: int, data):
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return None
        d = to_dict(data)
        for field, value in d.items():
            setattr(supplier, field, value)
        db.commit()
        db.refresh(supplier)
        return supplier

    @staticmethod
    def delete_supplier(db: Session, supplier_id: int):
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return None
        db.delete(supplier)
        db.commit()
        return supplier
