"""
Unit Tests — All Services
"""
import pytest
from datetime import datetime, timedelta


# ---- User Service ----

class TestUserService:

    def test_create_user(self, db):
        from app.services.user_service import UserService
        user, err = UserService.create_user(db, "u1@test.com", "Pass@1234", "User One", "staff")
        assert user is not None
        assert user.email == "u1@test.com"
        assert user.role == "staff"
        assert err is None

    def test_create_duplicate_user(self, db):
        from app.services.user_service import UserService
        UserService.create_user(db, "dup@test.com", "Pass@1234", "Dup", "staff")
        user2, err = UserService.create_user(db, "dup@test.com", "Pass@1234", "Dup2", "staff")
        assert user2 is None
        assert err is not None

    def test_get_user_by_email(self, db):
        from app.services.user_service import UserService
        UserService.create_user(db, "find@test.com", "Pass@1234", "Find", "staff")
        found = UserService.get_user_by_email(db, "find@test.com")
        assert found is not None
        assert found.email == "find@test.com"

    def test_get_user_by_id(self, db):
        from app.services.user_service import UserService
        user, _ = UserService.create_user(db, "id@test.com", "Pass@1234", "ID", "staff")
        found = UserService.get_user_by_id(db, user.id)
        assert found is not None

    def test_list_users(self, db):
        from app.services.user_service import UserService
        UserService.create_user(db, "list1@test.com", "Pass@1234", "L1", "staff")
        users = UserService.list_users(db)
        assert len(users) >= 1

    def test_toggle_active(self, db):
        from app.services.user_service import UserService
        user, _ = UserService.create_user(db, "toggle@test.com", "Pass@1234", "Toggle", "staff")
        original = user.is_active
        toggled, err = UserService.toggle_active(db, user.id)
        assert toggled is not None
        assert toggled.is_active != original

    def test_delete_user(self, db):
        from app.services.user_service import UserService
        user, _ = UserService.create_user(db, "del@test.com", "Pass@1234", "Del", "staff")
        deleted, err = UserService.delete_user(db, user.id)
        assert deleted is not None

    def test_count_active_admins(self, db):
        from app.services.user_service import UserService
        count = UserService.count_active_admins(db)
        assert isinstance(count, int)
        assert count >= 0


# ---- Medicine Service ----

class TestMedicineService:

    def test_create_medicine(self, db):
        from app.services.medicine_service import MedicineService
        med, err = MedicineService.create(db, {
            "name": "Paracetamol",
            "generic_name": "Paracetamol",
            "brand": "Panadol",
            "form": "tablet",
            "unit": "pcs",
            "strength": "500mg",
            "category": "Analgesic",
            "default_purchase_price": 500,
            "default_selling_price": 800,
            "reorder_level": 10,
            "max_stock_level": 100,
        })
        assert med is not None
        assert med.name == "Paracetamol"
        assert med.default_selling_price == 800

    def test_get_all_medicines(self, db):
        from app.services.medicine_service import MedicineService
        MedicineService.create(db, {"name": "M1", "default_selling_price": 100})
        all_meds = MedicineService.get_all(db)
        assert len(all_meds) >= 1

    def test_get_medicine_by_id(self, db):
        from app.services.medicine_service import MedicineService
        med, _ = MedicineService.create(db, {"name": "MFind", "default_selling_price": 100})
        found = MedicineService.get_by_id(db, med.id)
        assert found is not None

    def test_update_medicine(self, db):
        from app.services.medicine_service import MedicineService
        med, _ = MedicineService.create(db, {"name": "MUpd", "default_selling_price": 100})
        updated, err = MedicineService.update(db, med.id, {"name": "MUpdated"})
        assert updated is not None
        assert updated.name == "MUpdated"

    def test_delete_medicine(self, db):
        from app.services.medicine_service import MedicineService
        med, _ = MedicineService.create(db, {"name": "MDel", "default_selling_price": 100})
        err = MedicineService.delete(db, med.id)
        assert err is None
        assert MedicineService.get_by_id(db, med.id) is None


# ---- Category Service ----

class TestCategoryService:

    def test_create_category(self, db):
        from app.services.category_service import CategoryService
        cat = CategoryService.create(db, {"name": "Analgesics"})
        assert cat is not None
        assert cat.name == "Analgesics"

    def test_get_all_categories(self, db):
        from app.services.category_service import CategoryService
        CategoryService.create(db, {"name": "Antibiotics"})
        cats = CategoryService.get_all(db)
        assert len(cats) >= 1

    def test_update_category(self, db):
        from app.services.category_service import CategoryService
        cat = CategoryService.create(db, {"name": "UpdCat"})
        updated = CategoryService.update(db, cat.id, {"name": "UpdCatNew"})
        assert updated is not None

    def test_delete_category(self, db):
        from app.services.category_service import CategoryService
        cat = CategoryService.create(db, {"name": "DelCat"})
        result = CategoryService.delete(db, cat.id)
        assert result is not None


# ---- Branch Service ----

class TestBranchService:

    def test_create_branch(self, db):
        from app.services.branch_service import BranchService
        br = BranchService.create(db, {"name": "Main Branch", "code": "MB001"})
        assert br is not None
        assert br.name == "Main Branch"

    def test_get_all_branches(self, db):
        from app.services.branch_service import BranchService
        BranchService.create(db, {"name": "B1", "code": "B1"})
        branches = BranchService.get_all(db)
        assert len(branches) >= 1

    def test_get_branch_by_id(self, db):
        from app.services.branch_service import BranchService
        br = BranchService.create(db, {"name": "BF", "code": "BF"})
        found = BranchService.get_by_id(db, br.id)
        assert found is not None

    def test_update_branch(self, db):
        from app.services.branch_service import BranchService
        br = BranchService.create(db, {"name": "BU", "code": "BU"})
        updated = BranchService.update(db, br.id, {"name": "BUUpdated"})
        assert updated is not None

    def test_delete_branch(self, db):
        from app.services.branch_service import BranchService
        br = BranchService.create(db, {"name": "BD", "code": "BD"})
        result = BranchService.delete(db, br.id)
        assert result is not None


# ---- Manufacturer Service ----

class TestManufacturerService:

    def test_create_manufacturer(self, db):
        from app.services.manufacturer_service import ManufacturerService
        mfr = ManufacturerService.create(db, {"name": "PharmaCorp", "country": "Tanzania"})
        assert mfr is not None

    def test_get_all_manufacturers(self, db):
        from app.services.manufacturer_service import ManufacturerService
        ManufacturerService.create(db, {"name": "Mfr1"})
        all_m = ManufacturerService.get_all(db)
        assert len(all_m) >= 1

    def test_update_manufacturer(self, db):
        from app.services.manufacturer_service import ManufacturerService
        mfr = ManufacturerService.create(db, {"name": "MUpd"})
        updated = ManufacturerService.update(db, mfr.id, {"name": "MUpdNew"})
        assert updated is not None

    def test_delete_manufacturer(self, db):
        from app.services.manufacturer_service import ManufacturerService
        mfr = ManufacturerService.create(db, {"name": "MDel"})
        result = ManufacturerService.delete(db, mfr.id)
        assert result is not None


# ---- Customer Service ----

class TestCustomerService:

    def test_create_customer(self, db):
        from app.services.customer_service import CustomerService
        cust = CustomerService.create(db, {"name": "John Doe", "phone": "0712345678"})
        assert cust is not None

    def test_get_all_customers(self, db):
        from app.services.customer_service import CustomerService
        CustomerService.create(db, {"name": "C1"})
        custs = CustomerService.get_all(db)
        assert len(custs) >= 1

    def test_get_customer_by_id(self, db):
        from app.services.customer_service import CustomerService
        cust = CustomerService.create(db, {"name": "CFind"})
        found = CustomerService.get_by_id(db, cust.id)
        assert found is not None

    def test_update_customer(self, db):
        from app.services.customer_service import CustomerService
        cust = CustomerService.create(db, {"name": "CUpd"})
        updated = CustomerService.update(db, cust.id, {"name": "CUpdNew"})
        assert updated is not None

    def test_delete_customer(self, db):
        from app.services.customer_service import CustomerService
        cust = CustomerService.create(db, {"name": "CDel"})
        result = CustomerService.delete(db, cust.id)
        assert result is not None


# ---- Supplier Service ----

class TestSupplierService:

    def test_create_supplier(self, db):
        from app.services.supplier_service import SupplierService
        sup = SupplierService.create_supplier(db, {"name": "SupOne", "company_name": "Co1"})
        assert sup is not None

    def test_update_supplier(self, db):
        from app.services.supplier_service import SupplierService
        sup = SupplierService.create_supplier(db, {"name": "SupUpd"})
        updated = SupplierService.update_supplier(db, sup.id, {"name": "SupUpdNew"})
        assert updated is not None

    def test_delete_supplier(self, db):
        from app.services.supplier_service import SupplierService
        sup = SupplierService.create_supplier(db, {"name": "SupDel"})
        result = SupplierService.delete_supplier(db, sup.id)
        assert result is not None


# ---- Permission Service ----

class TestPermissionService:

    def test_initialize(self, db):
        from app.services.permission_service import PermissionService
        PermissionService.initialize(db)  # should not raise
        from app.models.permission import RolePermission
        count = db.query(RolePermission).count()
        assert count > 0

    def test_get_modules_for_role(self, db):
        from app.services.permission_service import PermissionService
        modules = PermissionService.get_modules_for_role(db, "admin")
        assert isinstance(modules, list)
        assert "dashboard" in modules

    def test_get_all_permissions(self, db):
        from app.services.permission_service import PermissionService
        all_perms = PermissionService.get_all_permissions(db)
        assert "admin" in all_perms
        assert "staff" in all_perms

    def test_has_module_admin(self, db):
        from app.services.permission_service import PermissionService
        assert PermissionService.has_module(db, "admin", "medicines") is True

    def test_has_module_staff(self, db):
        from app.services.permission_service import PermissionService
        assert PermissionService.has_module(db, "staff", "medicines") is True

    def test_has_permission_admin_read(self, db):
        from app.services.permission_service import PermissionService
        assert PermissionService.has_permission(db, "admin", "medicines", "read") is True

    def test_has_permission_admin_delete(self, db):
        from app.services.permission_service import PermissionService
        assert PermissionService.has_permission(db, "admin", "medicines", "delete") is True

    def test_update_role(self, db):
        from app.services.permission_service import PermissionService
        updated = PermissionService.update_role(db, "pharmacist", {"medicines": "read", "sales": "*"})
        assert "medicines" in updated
        assert updated["medicines"] == "read"


# ---- Currency Service ----

class TestCurrencyService:

    def test_get_all_currencies(self, db):
        from app.services.currency_service import CurrencyService
        currencies = CurrencyService.get_all(db)
        assert len(currencies) >= 1

    def test_get_by_code(self, db):
        from app.services.currency_service import CurrencyService
        c = CurrencyService.get_by_code(db, "TZS")
        assert c is not None
        assert c.code == "TZS"

    def test_format_tzs(self):
        from app.services.currency_service import format_tzs
        result = format_tzs(1234567)
        assert "TZS" in result or "1" in result


# ---- Expense Service ----

class TestExpenseService:

    def test_create_expense(self, db):
        from app.services.expense_service import ExpenseService
        exp = ExpenseService.create_expense(db, {
            "category": "Rent",
            "description": "Monthly rent",
            "amount": 500000,
            "payment_method": "bank_transfer",
            "date": datetime.now().isoformat(),
        })
        assert exp is not None

    def test_list_expenses(self, db):
        from app.services.expense_service import ExpenseService
        ExpenseService.create_expense(db, {
            "category": "Utilities",
            "amount": 50000,
            "date": datetime.now().isoformat(),
        })
        result = ExpenseService.list_expenses(db)
        assert isinstance(result, dict)

    def test_summary(self, db):
        from app.services.expense_service import ExpenseService
        result = ExpenseService.summary(db)
        assert isinstance(result, dict)


# ---- Notification Service ----

class TestNotificationService:

    def test_create_notification(self, db):
        from app.services.notification_service import NotificationService
        notif = NotificationService.create_notification(
            db, "low_stock", "Low Stock Alert", "Paracetamol is low", "medicines", 1
        )
        assert notif is not None

    def test_list_notifications(self, db):
        from app.services.notification_service import NotificationService
        NotificationService.create_notification(db, "info", "Test", "msg", "medicines", 1)
        items = NotificationService.list_notifications(db)
        assert isinstance(items, dict)

    def test_unread_count(self, db):
        from app.services.notification_service import NotificationService
        NotificationService.create_notification(db, "info", "Test", "msg", "medicines", 1)
        count = NotificationService.unread_count(db)
        assert isinstance(count, int)
        assert count >= 1

    def test_mark_read(self, db):
        from app.services.notification_service import NotificationService
        notif = NotificationService.create_notification(db, "info", "Test", "msg", "medicines", 1)
        result = NotificationService.mark_read(db, notif.id)
        assert result is not None  # returns the notification object

    def test_mark_all_read(self, db):
        from app.services.notification_service import NotificationService
        NotificationService.create_notification(db, "info", "T1", "m1", "medicines", 1)
        NotificationService.create_notification(db, "info", "T2", "m2", "medicines", 2)
        result = NotificationService.mark_all_read(db)
        assert result is True


# ---- Activity Service ----

class TestActivityService:

    def test_log_activity(self, db):
        from app.services.activity_service import ActivityService
        ActivityService.log(db, "create", "medicines", "Created medicine", "test@test.com", "127.0.0.1")
        # log() is safe, never raises — verify it didn't crash

    def test_list_activities(self, db):
        from app.services.activity_service import ActivityService
        ActivityService.log(db, "test", "medicines", "Test", "test@test.com", "127.0.0.1")
        result = ActivityService.list_activities(db)
        assert isinstance(result, dict)


# ---- Settings Service ----

class TestSettingsService:

    def test_get_settings(self, db):
        from app.services.settings_service import SettingsService
        s = SettingsService.get_settings(db)
        assert s is not None

    def test_update_settings(self, db):
        from app.services.settings_service import SettingsService
        updated = SettingsService.update_settings(db, {
            "pharmacy_name": "Test Pharmacy Updated",
            "address": "123 Test St",
            "tax_rate": 18.0,
            "region": "Dar es Salaam",
            "district": "Temeke",
        })
        assert updated is not None


# ---- Batch Service ----

class TestBatchService:

    def _make_medicine(self, db):
        from app.services.medicine_service import MedicineService
        med, _ = MedicineService.create(db, {"name": "BatchMed", "default_selling_price": 1000})
        return med

    def test_create_batch(self, db):
        from app.services.batch_service import BatchService
        med = self._make_medicine(db)
        batch, err = BatchService.create(db, {
            "medicine_id": med.id,
            "batch_no": "BAT001",
            "quantity": 100,
            "purchase_price": 500,
            "selling_price": 800,
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
        })
        assert batch is not None

    def test_get_batch_by_medicine(self, db):
        from app.services.batch_service import BatchService
        med = self._make_medicine(db)
        BatchService.create(db, {
            "medicine_id": med.id, "batch_no": "BAT002", "quantity": 50,
            "purchase_price": 300, "selling_price": 500,
            "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        })
        batches = BatchService.get_by_medicine(db, med.id)
        assert len(batches) >= 1


# ---- Stock Movement Service ----

class TestStockMovementService:

    def test_log_movement(self, db):
        from app.services.stock_movement_service import StockMovementService
        from app.services.medicine_service import MedicineService
        from app.services.batch_service import BatchService
        med, _ = MedicineService.create(db, {"name": "SM_Med", "default_selling_price": 100})
        batch, _ = BatchService.create(db, {
            "medicine_id": med.id, "batch_no": "SM-B01", "quantity": 100,
            "purchase_price": 300, "selling_price": 500,
            "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        })
        log = StockMovementService.log(
            db, medicine_id=med.id, batch_id=batch.id, branch_id=None,
            movement_type="in", quantity=100, reference_type="purchase",
            reference_id=1, notes="Test stock in", created_by=None
        )
        assert log is not None

    def test_get_movements(self, db):
        from app.services.stock_movement_service import StockMovementService
        from app.services.medicine_service import MedicineService
        from app.services.batch_service import BatchService
        med, _ = MedicineService.create(db, {"name": "SM_Med2", "default_selling_price": 100})
        batch, _ = BatchService.create(db, {
            "medicine_id": med.id, "batch_no": "SM-B02", "quantity": 50,
            "purchase_price": 300, "selling_price": 500,
            "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        })
        StockMovementService.log(db, medicine_id=med.id, batch_id=batch.id, branch_id=None, movement_type="in", quantity=50)
        result = StockMovementService.get_movements(db, medicine_id=med.id)
        assert isinstance(result, list)


# ---- Disposal Service ----

class TestDisposalService:

    def test_generate_disposal_number(self, db):
        from app.services.disposal_service import DisposalService
        num = DisposalService.generate_disposal_number(db)
        assert num.startswith("DIS-")
        assert len(num) > 10

    def test_get_disposals_empty(self, db):
        from app.services.disposal_service import DisposalService
        items = DisposalService.get_disposals(db)
        assert isinstance(items, list)


# ---- PDF Service ----

class TestPDFService:

    def test_generate_invoice(self, db):
        from app.services.pdf_service import PDFService
        # Create a mock sale object
        class MockSale:
            id = 1
            invoice_number = "INV-TEST-001"
            customer_name = "Test Customer"
            sale_date = datetime.now()
            subtotal = 10000
            discount_amount = 0
            total_amount = 10000
            amount_paid = 10000
            change_amount = 0
            due_amount = 0
            payment_method = "cash"
            items = []

        pdf = PDFService.generate_sale_invoice(MockSale())
        assert pdf is not None
        assert hasattr(pdf, 'read')
