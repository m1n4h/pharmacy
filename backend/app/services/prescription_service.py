from sqlalchemy.orm import Session
from datetime import datetime, date

from app.models.prescription import Prescription, PrescriptionItem
from app.models.batch import Batch
from app.models.medicine import Medicine
from app.utils.pagination import Paginator


class PrescriptionService:

    @staticmethod
    def create_prescription(db: Session, data, user=None):
        try:
            prescription = Prescription(
                prescription_no=f"RX-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                patient_name=data.patient_name.strip(),
                patient_age=data.patient_age,
                doctor_name=data.doctor_name,
                notes=data.notes,
                status="pending",
                total_amount=0,
                created_at=datetime.utcnow(),
                created_by=getattr(user, "id", None)
            )
            db.add(prescription)
            db.flush()

            total = 0
            for item in data.items:
                if item.quantity <= 0:
                    raise ValueError(
                        f"Invalid quantity for medicine_id: {item.medicine_id}. Quantity must be positive"
                    )

                # Price = FIFO (earliest expiry, not expired, in stock) selling price
                fifo_batch = (
                    db.query(Batch)
                    .filter(
                        Batch.medicine_id == item.medicine_id,
                        Batch.expiry_date >= date.today(),
                        Batch.quantity > 0
                    )
                    .order_by(Batch.expiry_date.asc(), Batch.id.asc())
                    .first()
                )

                if not fifo_batch:
                    raise ValueError(f"No stock available for medicine_id: {item.medicine_id}")

                medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
                if not medicine:
                    raise ValueError(f"Medicine not found: {item.medicine_id}")

                price = fifo_batch.selling_price
                p_item = PrescriptionItem(
                    prescription_id=prescription.id,
                    medicine_id=item.medicine_id,
                    medicine_name=medicine.name,
                    quantity=item.quantity,
                    price=price
                )
                db.add(p_item)
                total += price * item.quantity

            prescription.total_amount = total
            db.commit()
            db.refresh(prescription)
            return prescription, None

        except Exception as exc:
            db.rollback()
            return None, str(exc)

    @staticmethod
    def list_prescriptions(db: Session, page: int = 1, limit: int = 10,
                           status: str = None, search: str = None):
        query = db.query(Prescription)
        if status:
            query = query.filter(Prescription.status == status)
        if search:
            s = f"%{search}%"
            query = query.filter(
                (Prescription.patient_name.ilike(s)) |
                (Prescription.prescription_no.ilike(s)) |
                (Prescription.doctor_name.ilike(s))
            )
        query = query.order_by(Prescription.created_at.desc())
        return Paginator.paginate(query, page, limit)

    @staticmethod
    def get_prescription(db: Session, prescription_id: int):
        return db.query(Prescription).filter(Prescription.id == prescription_id).first()

    @staticmethod
    def dispense_prescription(db: Session, prescription_id: int, user=None):
        """Dispense: creates a Sale (FIFO stock deduction) and marks dispensed."""
        try:
            prescription = db.query(Prescription).filter(
                Prescription.id == prescription_id
            ).first()
            if not prescription:
                return None, "PRESCRIPTION_NOT_FOUND"
            if prescription.status == "dispensed":
                return None, "ALREADY_DISPENSED"
            if prescription.status == "cancelled":
                return None, "PRESCRIPTION_CANCELLED"

            from app.services.sale_service import SaleService
            from app.schemas.sale import SaleCreate, SaleItemCreate

            sale_data = SaleCreate(
                customer_name=prescription.patient_name,
                sale_date=date.today(),
                discount_amount=0,
                items=[
                    SaleItemCreate(medicine_id=i.medicine_id, quantity=i.quantity)
                    for i in prescription.items
                ]
            )
            sale = SaleService.create_sale(db, sale_data)

            prescription.status = "dispensed"
            prescription.dispensed_at = datetime.utcnow()
            prescription.sale_id = sale.id
            db.commit()
            db.refresh(prescription)
            return prescription, None

        except Exception as exc:
            db.rollback()
            return None, str(exc)

    @staticmethod
    def update_prescription(db: Session, prescription_id: int, data, user=None):
        try:
            prescription = db.query(Prescription).filter(
                Prescription.id == prescription_id
            ).first()
            if not prescription:
                return None, "PRESCRIPTION_NOT_FOUND"
            if prescription.status != "pending":
                return None, "ONLY_PENDING_EDITABLE"

            prescription.patient_name = data.patient_name.strip()
            prescription.patient_age = data.patient_age
            prescription.doctor_name = data.doctor_name
            prescription.notes = data.notes

            # Rebuild items (only for pending, no stock movement)
            if data.items is not None:
                db.query(PrescriptionItem).filter(
                    PrescriptionItem.prescription_id == prescription.id
                ).delete()
                total = 0
                for item in data.items:
                    if item.quantity <= 0:
                        raise ValueError(f"Invalid quantity for medicine_id: {item.medicine_id}")
                    fifo_batch = (
                        db.query(Batch)
                        .filter(
                            Batch.medicine_id == item.medicine_id,
                            Batch.expiry_date >= date.today(),
                            Batch.quantity > 0
                        )
                        .order_by(Batch.expiry_date.asc(), Batch.id.asc())
                        .first()
                    )
                    medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
                    if not medicine:
                        raise ValueError(f"Medicine not found: {item.medicine_id}")
                    price = fifo_batch.selling_price if fifo_batch else 0
                    db.add(PrescriptionItem(
                        prescription_id=prescription.id,
                        medicine_id=item.medicine_id,
                        medicine_name=medicine.name,
                        quantity=item.quantity,
                        price=price
                    ))
                    total += price * item.quantity
                prescription.total_amount = total

            db.commit()
            db.refresh(prescription)
            return prescription, None
        except Exception as exc:
            db.rollback()
            return None, str(exc)

    @staticmethod
    def delete_prescription(db: Session, prescription_id: int, user=None):
        prescription = db.query(Prescription).filter(
            Prescription.id == prescription_id
        ).first()
        if not prescription:
            return None, "PRESCRIPTION_NOT_FOUND"
        if prescription.status == "dispensed":
            return None, "CANNOT_DELETE_DISPENSED"
        db.query(PrescriptionItem).filter(
            PrescriptionItem.prescription_id == prescription.id
        ).delete()
        db.delete(prescription)
        db.commit()
        return prescription, None

    @staticmethod
    def cancel_prescription(db: Session, prescription_id: int, user=None):
        prescription = db.query(Prescription).filter(
            Prescription.id == prescription_id
        ).first()
        if not prescription:
            return None, "PRESCRIPTION_NOT_FOUND"
        if prescription.status == "dispensed":
            return None, "ALREADY_DISPENSED"
        prescription.status = "cancelled"
        db.commit()
        db.refresh(prescription)
        return prescription, None