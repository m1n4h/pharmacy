from sqlalchemy.orm import Session
from app.models.category import Category
from app.utils.helpers import to_dict


class CategoryService:

    @staticmethod
    def create(db: Session, data):
        d = to_dict(data)
        existing = db.query(Category).filter(Category.name == d.get("name")).first()
        if existing:
            return None
        category = Category(**d)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_all(db: Session):
        return db.query(Category).order_by(Category.name).all()

    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(Category).filter(Category.id == id).first()

    @staticmethod
    def update(db: Session, id: int, data):
        category = db.query(Category).filter(Category.id == id).first()
        if not category:
            return None

        d = to_dict(data)
        for field, value in d.items():
            setattr(category, field, value)

        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, id: int):
        category = db.query(Category).filter(Category.id == id).first()
        if not category:
            return None

        db.delete(category)
        db.commit()
        return category
