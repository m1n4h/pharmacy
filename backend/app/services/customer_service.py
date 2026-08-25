from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.utils.helpers import to_dict


class CustomerService:

    @staticmethod
    def create(db: Session, data):
        d = to_dict(data)
        existing = db.query(Customer).filter(Customer.name == d.get("name")).first()
        if existing:
            return None
        customer = Customer(**d)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def get_all(db: Session, search=None):
        query = db.query(Customer)
        if search:
            s = f"%{search}%"
            query = query.filter(
                (Customer.name.ilike(s)) | (Customer.phone.ilike(s))
            )
        return query.order_by(Customer.name).all()

    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(Customer).filter(Customer.id == id).first()

    @staticmethod
    def update(db: Session, id: int, data):
        customer = db.query(Customer).filter(Customer.id == id).first()
        if not customer:
            return None

        d = to_dict(data)
        for field, value in d.items():
            setattr(customer, field, value)

        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def delete(db: Session, id: int):
        customer = db.query(Customer).filter(Customer.id == id).first()
        if not customer:
            return None

        db.delete(customer)
        db.commit()
        return customer
