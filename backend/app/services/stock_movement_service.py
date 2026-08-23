from sqlalchemy.orm import Session
from app.models.stock_movement import StockMovement


class StockMovementService:

    @staticmethod
    def log(db: Session, medicine_id, batch_id, branch_id, movement_type, quantity,
            reference_type=None, reference_id=None, notes=None, created_by=None):
        movement = StockMovement(
            medicine_id=medicine_id,
            batch_id=batch_id,
            branch_id=branch_id,
            movement_type=movement_type,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            created_by=created_by
        )
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement

    @staticmethod
    def get_movements(db: Session, medicine_id=None, batch_id=None,
                      branch_id=None, movement_type=None, limit=100):
        query = db.query(StockMovement)
        if medicine_id:
            query = query.filter(StockMovement.medicine_id == medicine_id)
        if batch_id:
            query = query.filter(StockMovement.batch_id == batch_id)
        if branch_id:
            query = query.filter(StockMovement.branch_id == branch_id)
        if movement_type:
            query = query.filter(StockMovement.movement_type == movement_type)
        return query.order_by(StockMovement.created_at.desc()).limit(limit).all()
