from sqlalchemy.orm import Session
from datetime import datetime, date

from app.models.return_record import Return, ReturnItem
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.batch import Batch
from app.models.stock_movement import StockMovement


class ReturnService:

    @staticmethod
    def generate_return_number(db: Session):
        today = date.today().strftime("%Y%m%d")
        prefix = f"RET-{today}-"
        last_return = db.query(Return).filter(
            Return.return_number.like(f"{prefix}%")
        ).order_by(Return.id.desc()).first()

        if last_return:
            last_seq = int(last_return.return_number.split("-")[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        return f"{prefix}{new_seq:03d}"

    @staticmethod
    def create_return(db: Session, sale_id, items_list, reason, processed_by):
        try:
            sale = db.query(Sale).filter(Sale.id == sale_id).first()
            if not sale:
                raise ValueError("SALE_NOT_FOUND")

            if not items_list:
                raise ValueError("Return must contain at least one item")

            return_number = ReturnService.generate_return_number(db)
            total_refund = 0

            return_record = Return(
                return_number=return_number,
                sale_id=sale_id,
                reason=reason,
                total_refund=0,
                status="pending",
                processed_by=processed_by
            )
            db.add(return_record)
            db.flush()

            for item in items_list:
                if item["quantity"] <= 0:
                    raise ValueError(f"Invalid return quantity for sale_item_id: {item.get('sale_item_id')}")

                refund_amount = item["unit_price"] * item["quantity"]
                total_refund += refund_amount

                return_item = ReturnItem(
                    return_id=return_record.id,
                    sale_item_id=item.get("sale_item_id"),
                    medicine_id=item["medicine_id"],
                    batch_id=item["batch_id"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    refund_amount=refund_amount,
                    condition=item.get("condition", "good")
                )
                db.add(return_item)

                batch = db.query(Batch).filter(Batch.id == item["batch_id"]).first()
                if batch:
                    batch.quantity += item["quantity"]

                movement = StockMovement(
                    medicine_id=item["medicine_id"],
                    batch_id=item["batch_id"],
                    branch_id=sale.branch_id,
                    movement_type="return",
                    quantity=item["quantity"],
                    reference_type="return",
                    reference_id=return_record.id,
                    notes=f"Return for sale {sale.invoice_number}",
                    created_by=processed_by
                )
                db.add(movement)

            return_record.total_refund = total_refund
            sale.status = "returned"

            db.commit()
            db.refresh(return_record)
            return return_record

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_returns(db: Session, limit=100):
        return db.query(Return).order_by(Return.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_return(db: Session, return_id: int):
        return db.query(Return).filter(Return.id == return_id).first()
