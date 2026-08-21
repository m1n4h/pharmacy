from sqlalchemy.orm import Session
from datetime import datetime, date

from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.batch import Batch


class SaleService:

    @staticmethod
    def create_sale(db: Session, data):
        try:
            # 1) Create the parent sale
            # create a unique invoice number (microseconds to avoid collisions)
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            sale = Sale(
                invoice_number=invoice_number,
                customer_name=data.customer_name or "Walk-in Customer",
                sale_date=data.sale_date or date.today(),
                subtotal=0,
                discount_amount=data.discount_amount,
                total_amount=0,
                created_at=datetime.now()
            )
            db.add(sale)
            db.flush()

            if not data.items:
                raise ValueError("Sale must contain at least one item")

            if data.discount_amount < 0:
                raise ValueError("Discount amount cannot be negative")

            total_amount = 0

            # 2) Process sale items with FIFO batch deduction
            for item in data.items:
                if item.quantity <= 0:
                    raise ValueError(
                        f"Invalid quantity for medicine_id: {item.medicine_id}. Quantity must be positive"
                    )

                needed_qty = item.quantity

                # Get FIFO batches: earliest expiry first, skip expired
                fifo_batches = db.query(Batch).filter(
                    Batch.medicine_id == item.medicine_id,
                    Batch.expiry_date >= date.today(),
                    Batch.quantity > 0
                ).order_by(Batch.expiry_date.asc()).all()

                if not fifo_batches:
                    raise ValueError(f"No valid batches found for medicine_id: {item.medicine_id}")

                for batch in fifo_batches:
                    if needed_qty == 0:
                        break

                    if batch.quantity <= 0:
                        continue

                    # Deduct from this batch
                    deduct_qty = min(batch.quantity, needed_qty)

                    # Create sale item entry
                    sale_item = SaleItem(
                        sale_id=sale.id,
                        medicine_id=item.medicine_id,
                        batch_id=batch.id,
                        quantity=deduct_qty,
                        selling_price=batch.selling_price
                    )
                    db.add(sale_item)

                    # Update batch stock
                    batch.quantity -= deduct_qty

                    # Update running totals
                    total_amount += batch.selling_price * deduct_qty
                    needed_qty -= deduct_qty

                if needed_qty > 0:
                    raise ValueError(
                        f"Not enough stock for medicine_id {item.medicine_id}. Missing: {needed_qty}"
                    )

            if data.discount_amount > total_amount:
                raise ValueError("Discount cannot be greater than the sale subtotal")

            # 3) Update sale amounts
            sale.subtotal = total_amount
            sale.total_amount = total_amount - data.discount_amount

            db.commit()
            db.refresh(sale)

            return sale

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def update_sale(db: Session, sale_id: int, data):
        """Edit sale header (customer name + discount). Items unchanged (no stock rebalance)."""
        try:
            sale = db.query(Sale).filter(Sale.id == sale_id).first()
            if not sale:
                raise ValueError("SALE_NOT_FOUND")
            if data.customer_name is not None:
                sale.customer_name = data.customer_name
            if data.discount_amount is not None:
                if data.discount_amount < 0:
                    raise ValueError("Discount cannot be negative")
                if data.discount_amount > sale.subtotal:
                    raise ValueError("Discount cannot exceed subtotal")
                sale.discount_amount = data.discount_amount
                sale.total_amount = sale.subtotal - data.discount_amount
            db.commit()
            db.refresh(sale)
            return sale
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def delete_sale(db: Session, sale_id: int):
        """Delete a sale and restore its stock to the original batches."""
        try:
            sale = db.query(Sale).filter(Sale.id == sale_id).first()
            if not sale:
                raise ValueError("SALE_NOT_FOUND")
            for item in sale.items:
                batch = db.query(Batch).filter(Batch.id == item.batch_id).first()
                if batch:
                    batch.quantity += item.quantity
            db.delete(sale)  # cascade removes sale_items
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise
