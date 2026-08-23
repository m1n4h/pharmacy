from sqlalchemy.orm import Session
from datetime import datetime
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.batch import Batch
from app.services.currency_service import CurrencyService


class PurchaseService:

    @staticmethod
    def create_purchase(db: Session, data):
        try:
            # 1) Create parent purchase
            # create a unique invoice number (microseconds to avoid collisions)
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

            currency_code = (data.currency_code or "TZS").upper()
            currency_rate = CurrencyService.get_rate(db, currency_code)

            purchase = Purchase(
                invoice_number=invoice_number,
                supplier_name=data.supplier_name,
                purchase_date=data.purchase_date,
                total_amount=0,
                currency_code=currency_code,
                currency_rate=currency_rate,
                currency_amount=0,
                created_at=datetime.now()
            )

            db.add(purchase)
            db.flush()

            if not data.items:
                raise ValueError("Purchase must contain at least one item")

            total_amount = 0
            raw_total = 0

            # 2) Loop through purchase items
            for item in data.items:
                if item.quantity <= 0:
                    raise ValueError(
                        f"Invalid quantity for medicine_id: {item.medicine_id}. Quantity must be positive"
                    )
                if item.purchase_price < 0 or item.selling_price < 0:
                    raise ValueError("Prices cannot be negative")

                # Convert foreign currency purchase prices to TZS for stock valuation
                purchase_price_tzs = CurrencyService.convert_to_tzs(db, item.purchase_price, currency_code)

                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,
                    medicine_id=item.medicine_id,
                    batch_no=item.batch_no,
                    expiry_date=item.expiry_date,
                    purchase_price=purchase_price_tzs,
                    selling_price=item.selling_price,
                    quantity=item.quantity
                )
                db.add(purchase_item)

                # Calculate amount (unit cost × quantity)
                total_amount += purchase_price_tzs * item.quantity
                raw_total += item.purchase_price * item.quantity

                # 3) Create batch immediately
                batch = Batch(
                    batch_no=item.batch_no,
                    expiry_date=item.expiry_date,
                    purchase_price=purchase_price_tzs,
                    selling_price=item.selling_price,
                    quantity=item.quantity,
                    medicine_id=item.medicine_id
                )

                db.add(batch)

            # 4) Update total amount
            purchase.total_amount = total_amount
            purchase.currency_amount = raw_total

            db.commit()
            db.refresh(purchase)

            return purchase

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def update_purchase(db: Session, purchase_id: int, data):
        purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
        if not purchase:
            return None
        for field, value in data.dict(exclude_unset=True).items():
            setattr(purchase, field, value)
        db.commit()
        db.refresh(purchase)
        return purchase

    @staticmethod
    def delete_purchase(db: Session, purchase_id: int):
        purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
        if not purchase:
            return None
        # Restore stock for each purchase item
        for item in purchase.items:
            batch = db.query(Batch).filter(
                Batch.batch_no == item.batch_no,
                Batch.medicine_id == item.medicine_id
            ).first()
            if batch:
                batch.quantity -= item.quantity
                if batch.quantity <= 0:
                    db.delete(batch)
        db.delete(purchase)
        db.commit()
        return purchase
