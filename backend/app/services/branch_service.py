from sqlalchemy.orm import Session
from app.models.branch import Branch
from app.utils.helpers import to_dict


class BranchService:

    @staticmethod
    def create(db: Session, data):
        d = to_dict(data)
        code = d.get("code")
        if code:
            existing = db.query(Branch).filter(Branch.code == code).first()
            if existing:
                return None
        branch = Branch(**d)
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch

    @staticmethod
    def get_all(db: Session):
        return db.query(Branch).order_by(Branch.name).all()

    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(Branch).filter(Branch.id == id).first()

    @staticmethod
    def update(db: Session, id: int, data):
        branch = db.query(Branch).filter(Branch.id == id).first()
        if not branch:
            return None

        d = to_dict(data)
        for field, value in d.items():
            setattr(branch, field, value)

        db.commit()
        db.refresh(branch)
        return branch

    @staticmethod
    def delete(db: Session, id: int):
        branch = db.query(Branch).filter(Branch.id == id).first()
        if not branch:
            return None

        db.delete(branch)
        db.commit()
        return branch
