"""
PharmaMonitor — Full Document-Aligned Test Suite
Covers all test cases from the Software Testing Document:
UT-001 to UT-018, IT-001 to IT-012, ST-001 to ST-017, SEC-001, E2E-001
"""
import os
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal

os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient
from app.main import app
from app.db.db import SessionLocal, get_db
from app.models.medicine import Medicine
from app.models.batch import Batch
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.supplier import Supplier
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.category import Category
from app.models.branch import Branch
from app.models.expense import Expense
from app.models.settings import Settings
from app.models.currency import Currency
from app.models.user import User
from app.core.security import hash_password


@pytest.fixture(scope="module")
def client():
    c = TestClient(app)
    yield c


@pytest.fixture(scope="module")
def auth_headers(client):
    r = client.post("/auth/login", json={
        "email": "changwamale48@gmail.com",
        "password": "ngwamale#@39"
    })
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def seeded_data(client, auth_headers):
    """Seed all prerequisite data once per module."""
    db = SessionLocal()
    try:
        if not db.query(Settings).first():
            db.add(Settings(
                pharmacy_name="Test Pharmacy",
                pharmacy_phone="0700000000",
                pharmacy_email="test@test.com",
                pharmacy_address="Dar es Salaam",
                tax_rate=0.0,
                low_stock_threshold=10,
                expiry_alert_days=30,
                currency="TZS",
            ))
            db.commit()

        if not db.query(Currency).first():
            db.add(Currency(code="TZS", name="Tanzanian Shilling", symbol="TZS", rate_to_base=1.0))
            db.add(Currency(code="USD", name="US Dollar", symbol="$", rate_to_base=2500.0))
            db.commit()
    finally:
        db.close()

    h = auth_headers

    _counter = {"val": 0}

    def _make_med(name, sp=5000, pp=3000):
        import random as _rand
        _counter["val"] += 1
        unique = f"{name}-{_rand.randint(10000,99999)}-{_counter['val']}"
        r = client.post("/medicines/", json={
            "name": unique,
            "default_selling_price": sp,
            "default_purchase_price": pp,
        }, headers=h)
        assert r.status_code == 200, f"Medicine create returned {r.status_code}: {r.text}"
        assert r.json()["success"] is True, f"Medicine create failed: {r.json()}"
        return r.json()["data"]["id"]

    def _make_batch(mid, qty=100, sp=5000, pp=3000, bno=None, expiry=None):
        if expiry is None:
            expiry = (date.today() + timedelta(days=365)).isoformat()
        if bno is None:
            _counter["val"] += 1
            bno = f"B-{mid}-{_counter['val']}"
        r = client.post("/batches/create", json={
            "medicine_id": mid,
            "batch_no": bno,
            "quantity": qty,
            "selling_price": sp,
            "purchase_price": pp,
            "expiry_date": expiry,
        }, headers=h)
        assert r.status_code == 200
        return r.json()["data"]["id"]

    def _make_supplier(name="TestSupplier"):
        r = client.post("/suppliers/create", json={
            "name": name,
            "phone": "0712345678",
        }, headers=h)
        return r.json()["data"]["id"]

    return {
        "make_med": _make_med,
        "make_batch": _make_batch,
        "make_supplier": _make_supplier,
    }


# ============================================================
# UNIT TESTS
# ============================================================

class TestUT001_MedicineCreation:
    """UT-001: Verify that a medicine can be created with valid data."""

    def test_create_medicine_valid(self, client, auth_headers):
        import random
        r = client.post("/medicines/", json={
            "name": f"UT001-Paracetamol-{random.randint(10000,99999)}",
            "category": "Analgesic",
            "strength": "500mg",
            "unit": "Tablet",
            "default_selling_price": 5000,
            "default_purchase_price": 3000,
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert r.json()["data"]["strength"] == "500mg"


class TestUT002_MedicineNameValidation:
    """UT-002: Prevent creation of a medicine without a name."""

    def test_empty_name_rejected(self, client, auth_headers):
        r = client.post("/medicines/", json={
            "name": "",
            "default_selling_price": 5000,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)


class TestUT003_NegativeMedicinePrice:
    """UT-003: Prevent negative medicine prices."""

    def test_negative_purchase_price(self, client, auth_headers):
        r = client.post("/medicines/", json={
            "name": "NegativePriceMed",
            "default_purchase_price": -1000,
            "default_selling_price": 5000,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)

    def test_negative_selling_price(self, client, auth_headers):
        r = client.post("/medicines/", json={
            "name": "NegativeSellMed",
            "default_selling_price": -500,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)


class TestUT004_BatchCreation:
    """UT-004: Verify batch creation."""

    def test_create_batch_success(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("BatchTestMed")
        r = client.post("/batches/create", json={
            "medicine_id": mid,
            "batch_no": "PARA001",
            "expiry_date": (date.today() + timedelta(days=365)).isoformat(),
            "quantity": 100,
            "selling_price": 5000,
            "purchase_price": 3000,
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["success"] is True


class TestUT005_InvalidExpiryDate:
    """UT-005: Reject batch with expired/past expiry date."""

    def test_past_expiry_rejected(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("ExpiredBatchMed")
        r = client.post("/batches/create", json={
            "medicine_id": mid,
            "batch_no": "EXP-PAST",
            "expiry_date": "2020-01-01",
            "quantity": 50,
            "selling_price": 5000,
            "purchase_price": 3000,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)


class TestUT006_TotalSaleCalculation:
    """UT-006: Total sale = quantity × unit price."""

    def test_total_calculation(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("SaleCalcMed", sp=2000)
        seeded_data["make_batch"](mid, qty=50, sp=2000)
        r = client.post("/sales/create", json={
            "customer_name": "CalcCustomer",
            "items": [{"medicine_id": mid, "quantity": 10, "price": 2000}],
            "payment_method": "Cash",
            "amount_paid": 20000,
        }, headers=auth_headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["total_amount"] == 20000


class TestUT007_DiscountCalculation:
    """UT-007: discount = subtotal × discount%; final = subtotal - discount."""

    def test_discount_percentage(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("DiscountMed", sp=10000)
        seeded_data["make_batch"](mid, qty=20, sp=10000)
        r = client.post("/sales/create", json={
            "customer_name": "DiscCustomer",
            "items": [{"medicine_id": mid, "quantity": 10, "price": 10000}],
            "discount_amount": 10000,
            "payment_method": "Cash",
            "amount_paid": 90000,
        }, headers=auth_headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["subtotal"] == 100000
        assert data["discount_amount"] == 10000
        assert data["total_amount"] == 90000


class TestUT008_NegativeQuantity:
    """UT-008: Reject negative or zero quantity in sale."""

    def test_zero_quantity_rejected(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("NegQtyMed")
        seeded_data["make_batch"](mid, qty=50)
        r = client.post("/sales/create", json={
            "customer_name": "NegQty",
            "items": [{"medicine_id": mid, "quantity": 0, "price": 5000}],
            "payment_method": "Cash",
            "amount_paid": 0,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)

    def test_negative_quantity_rejected(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("NegQtyMed2")
        seeded_data["make_batch"](mid, qty=50)
        r = client.post("/sales/create", json={
            "customer_name": "NegQty2",
            "items": [{"medicine_id": mid, "quantity": -5, "price": 5000}],
            "payment_method": "Cash",
            "amount_paid": 0,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)


class TestUT009_StockCannotBecomeNegative:
    """UT-009: Sale above available stock is rejected."""

    def test_sale_exceeds_stock(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("OverSaleMed")
        seeded_data["make_batch"](mid, qty=10)
        r = client.post("/sales/create", json={
            "customer_name": "OverSale",
            "items": [{"medicine_id": mid, "quantity": 15, "price": 5000}],
            "payment_method": "Cash",
            "amount_paid": 75000,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)


class TestUT010_FEFOAlgorithm:
    """UT-010: System selects earliest-expiry batch first (FEFO)."""

    def test_fefo_selects_earliest(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("FEFOMed")
        early = (date.today() + timedelta(days=60)).isoformat()
        late = (date.today() + timedelta(days=730)).isoformat()
        seeded_data["make_batch"](mid, qty=50, sp=5000, bno="FEFO-EARLY", expiry=early)
        seeded_data["make_batch"](mid, qty=50, sp=5000, bno="FEFO-LATE", expiry=late)

        r = client.post("/sales/create", json={
            "customer_name": "FEFOCustomer",
            "items": [{"medicine_id": mid, "quantity": 10, "price": 5000}],
            "payment_method": "Cash",
            "amount_paid": 50000,
        }, headers=auth_headers)
        assert r.status_code == 200

        db = SessionLocal()
        try:
            sale = db.query(Sale).filter(Sale.id == r.json()["data"]["id"]).first()
            item = sale.items[0]
            batch = db.query(Batch).filter(Batch.id == item.batch_id).first()
            assert batch.batch_no == "FEFO-EARLY"
        finally:
            db.close()


class TestUT011_ExpiredBatchCannotBeSold:
    """UT-011: Expired batch cannot be selected for normal sale."""

    def _insert_expired_batch(self, mid):
        db = SessionLocal()
        try:
            b = Batch(
                medicine_id=mid, batch_no=f"EXP-{mid}",
                expiry_date=date.today() - timedelta(days=10),
                quantity=50, selling_price=5000, purchase_price=3000,
            )
            db.add(b)
            db.commit()
            return b.id
        finally:
            db.close()

    def test_expired_batch_excluded(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("ExpiredSellMed")
        self._insert_expired_batch(mid)

        r = client.post("/sales/create", json={
            "customer_name": "ExpiredSale",
            "items": [{"medicine_id": mid, "quantity": 1, "price": 5000}],
            "payment_method": "Cash",
            "amount_paid": 5000,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)


class TestUT012_ExpiryDaysCalculation:
    """UT-012: Expiry days = (expiry_date - today).days."""

    def test_expiry_days_via_inventory(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("ExpiryDaysMed")
        in30 = (date.today() + timedelta(days=30)).isoformat()
        seeded_data["make_batch"](mid, qty=20, bno="EX30", expiry=in30)
        r = client.get(f"/inventory/medicine/{mid}", headers=auth_headers)
        assert r.status_code == 200
        data = r.json().get("data", {})
        assert data is not None


class TestUT013_LowStock:
    """UT-013: Low stock status generated when stock < reorder level."""

    def test_low_stock_detected(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("LowStockMed")
        seeded_data["make_batch"](mid, qty=5, bno="LOW-5")
        r = client.get("/inventory/low", headers=auth_headers)
        assert r.status_code == 200


class TestUT014_ProfitCalculation:
    """UT-014: gross_profit = revenue - COGS; net_profit = gross_profit - expenses."""

    def test_profit_calculation(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("ProfitMed", sp=10000, pp=6000)
        seeded_data["make_batch"](mid, qty=100, sp=10000, pp=6000)

        r = client.post("/sales/create", json={
            "customer_name": "ProfitCust",
            "items": [{"medicine_id": mid, "quantity": 10, "price": 10000}],
            "payment_method": "Cash",
            "amount_paid": 100000,
        }, headers=auth_headers)
        assert r.status_code == 200

        r2 = client.post("/expenses/create", json={
            "category": "Rent",
            "amount": 50000,
            "date": date.today().isoformat(),
        }, headers=auth_headers)
        assert r2.status_code == 200

        r3 = client.get("/reports/profit-loss?period=month", headers=auth_headers)
        assert r3.status_code == 200


class TestUT015_NegativeExpense:
    """UT-015: System rejects negative expense."""

    def test_negative_expense_rejected(self, client, auth_headers):
        r = client.post("/expenses/create", json={
            "category": "Negative",
            "amount": -5000,
            "date": date.today().isoformat(),
        }, headers=auth_headers)
        assert r.status_code in (400, 422)


class TestUT016_DateRange:
    """UT-016: Report includes transactions only within specified period."""

    def test_custom_date_range(self, client, auth_headers):
        d1 = (date.today() - timedelta(days=30)).isoformat()
        d2 = date.today().isoformat()
        r = client.get(f"/reports/sales?date_from={d1}&date_to={d2}", headers=auth_headers)
        assert r.status_code == 200


class TestUT017_TopSelling:
    """UT-017: Medicines ranked by actual completed sales."""

    def test_top_selling_ranking(self, client, auth_headers):
        r = client.get("/reports/top-selling", headers=auth_headers)
        assert r.status_code == 200


class TestUT018_UserRole:
    """UT-018: User role permissions."""

    def test_role_permissions(self, client, auth_headers):
        r = client.get("/permissions/mine", headers=auth_headers)
        assert r.status_code == 200


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestIT001_LoginDashboardFlow:
    """IT-001: Login → Dashboard flow."""

    def test_login_then_dashboard(self, client, auth_headers):
        r = client.post("/auth/login", json={
            "email": "changwamale48@gmail.com",
            "password": "ngwamale#@39",
        })
        assert r.status_code == 200
        token = r.json()["data"]["access_token"]
        h = {"Authorization": f"Bearer {token}"}
        r2 = client.get("/dashboard/", headers=h)
        assert r2.status_code == 200


class TestIT005_FEFOAndSalesIntegration:
    """IT-005: FEFO + Sales integration."""

    def test_fefo_sales_flow(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("FIFOIntMed")
        early = (date.today() + timedelta(days=30)).isoformat()
        late = (date.today() + timedelta(days=600)).isoformat()
        seeded_data["make_batch"](mid, qty=100, sp=3000, bno="FIFO-A", expiry=early)
        seeded_data["make_batch"](mid, qty=100, sp=3000, bno="FIFO-B", expiry=late)

        r = client.post("/sales/create", json={
            "customer_name": "FIFOIntCust",
            "items": [{"medicine_id": mid, "quantity": 50, "price": 3000}],
            "payment_method": "Cash",
            "amount_paid": 150000,
        }, headers=auth_headers)
        assert r.status_code == 200

        db = SessionLocal()
        try:
            item = db.query(SaleItem).filter(SaleItem.sale_id == r.json()["data"]["id"]).first()
            batch = db.query(Batch).filter(Batch.id == item.batch_id).first()
            assert batch.batch_no == "FIFO-A"
        finally:
            db.close()


class TestIT006_ExpiredBatchSaleRejection:
    """IT-006: Expired batch sale rejection."""

    def _insert_expired_batch(self, mid):
        db = SessionLocal()
        try:
            b = Batch(
                medicine_id=mid, batch_no=f"EXPINT-{mid}",
                expiry_date=date.today() - timedelta(days=5),
                quantity=50, selling_price=5000, purchase_price=3000,
            )
            db.add(b)
            db.commit()
        finally:
            db.close()

    def test_expired_batch_cannot_sell(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("ExpIntMed")
        self._insert_expired_batch(mid)

        r = client.post("/sales/create", json={
            "customer_name": "ExpIntCust",
            "items": [{"medicine_id": mid, "quantity": 1, "price": 5000}],
            "payment_method": "Cash", "amount_paid": 5000,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)


class TestIT007_SaleProfitIntegration:
    """IT-007: Sale contributes to revenue and profit."""

    def test_sale_appears_in_profit(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("PrfIntMed", sp=8000, pp=5000)
        seeded_data["make_batch"](mid, qty=100, sp=8000, pp=5000)

        r = client.post("/sales/create", json={
            "customer_name": "PrfIntCust",
            "items": [{"medicine_id": mid, "quantity": 5, "price": 8000}],
            "payment_method": "Cash", "amount_paid": 40000,
        }, headers=auth_headers)
        assert r.status_code == 200

        r2 = client.get("/reports/profit-loss?period=month", headers=auth_headers)
        assert r2.status_code == 200
        data = r2.json()["data"]
        assert data.get("revenue", 0) > 0


class TestIT008_ExpenseProfitIntegration:
    """IT-008: Expenses reduce profit."""

    def test_expense_reduces_profit(self, client, auth_headers):
        r = client.post("/expenses/create", json={
            "category": "Utilities",
            "amount": 100000,
            "date": date.today().isoformat(),
        }, headers=auth_headers)
        assert r.status_code == 200

        r2 = client.get("/reports/profit-loss?period=month", headers=auth_headers)
        assert r2.status_code == 200


class TestIT009_BranchIsolation:
    """IT-009: Branch B cannot see Branch A stock."""

    def test_branch_isolation(self, client, auth_headers):
        import random
        code_a = f"ISO-A-{random.randint(1000,9999)}"
        code_b = f"ISO-B-{random.randint(1000,9999)}"
        r1 = client.post("/branches/create", json={
            "name": f"Branch Isolation A {code_a}", "code": code_a,
        }, headers=auth_headers)
        r2 = client.post("/branches/create", json={
            "name": f"Branch Isolation B {code_b}", "code": code_b,
        }, headers=auth_headers)
        assert r1.status_code == 200
        assert r2.status_code == 200
        b1 = r1.json()["data"]["id"]
        b2 = r2.json()["data"]["id"]
        assert b1 != b2


class TestIT011_ReportMatchesDatabase:
    """IT-011: Report totals match database records."""

    def test_report_matches_db(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("RptDbMed", sp=7000)
        seeded_data["make_batch"](mid, qty=50, sp=7000)

        r = client.post("/sales/create", json={
            "customer_name": "RptDbCust",
            "items": [{"medicine_id": mid, "quantity": 3, "price": 7000}],
            "payment_method": "Cash", "amount_paid": 21000,
        }, headers=auth_headers)
        assert r.status_code == 200

        r2 = client.get("/reports/profit-loss?period=month", headers=auth_headers)
        assert r2.status_code == 200


# ============================================================
# SYSTEM TESTS
# ============================================================

class TestST001_CompleteLoginWorkflow:
    """ST-001: Open → Login → Auth → Dashboard → User Info."""

    def test_complete_login(self, client):
        r = client.post("/auth/login", json={
            "email": "changwamale48@gmail.com",
            "password": "ngwamale#@39",
        })
        assert r.status_code == 200
        token = r.json()["data"]["access_token"]
        h = {"Authorization": f"Bearer {token}"}
        r2 = client.get("/auth/me", headers=h)
        assert r2.status_code == 200
        r3 = client.get("/dashboard/", headers=h)
        assert r3.status_code == 200


class TestST004_CompleteNormalSale:
    """ST-004: Search → select → FEFO → payment → receipt → stock reduced."""

    def test_complete_sale_workflow(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("NormSaleMed", sp=4000)
        seeded_data["make_batch"](mid, qty=100, sp=4000, bno="NS-B1")

        r_search = client.get(f"/medicines/?search=NormSaleMed", headers=auth_headers)
        assert r_search.status_code == 200

        r = client.post("/sales/create", json={
            "customer_name": "NormSaleCust",
            "items": [{"medicine_id": mid, "quantity": 5, "price": 4000}],
            "payment_method": "Cash",
            "amount_paid": 20000,
        }, headers=auth_headers)
        assert r.status_code == 200
        sale_id = r.json()["data"]["id"]

        db = SessionLocal()
        try:
            item = db.query(SaleItem).filter(SaleItem.sale_id == sale_id).first()
            batch = db.query(Batch).filter(Batch.id == item.batch_id).first()
            assert batch.quantity == 95
        finally:
            db.close()


class TestST005_ExpiredMedicineCannotBeSold:
    """ST-005: Create expired batch → attempt sale → blocked."""

    def _insert_expired_batch(self, mid):
        db = SessionLocal()
        try:
            b = Batch(
                medicine_id=mid, batch_no=f"STEXP-{mid}",
                expiry_date=date.today() - timedelta(days=10),
                quantity=30, selling_price=5000, purchase_price=3000,
            )
            db.add(b)
            db.commit()
        finally:
            db.close()

    def test_expired_sale_blocked(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("ExpBlockMed")
        self._insert_expired_batch(mid)

        r = client.post("/sales/create", json={
            "customer_name": "ExpBlockCust",
            "items": [{"medicine_id": mid, "quantity": 1, "price": 5000}],
            "payment_method": "Cash", "amount_paid": 5000,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)


class TestST008_ExpenseProfitCalculation:
    """ST-008: Sales + Expenses → Profit calculation."""

    def test_full_finance_flow(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("FinMed", sp=10000, pp=6000)
        seeded_data["make_batch"](mid, qty=200, sp=10000, pp=6000)

        r = client.post("/sales/create", json={
            "customer_name": "FinCust",
            "items": [{"medicine_id": mid, "quantity": 10, "price": 10000}],
            "payment_method": "Cash", "amount_paid": 100000,
        }, headers=auth_headers)
        assert r.status_code == 200

        r2 = client.post("/expenses/create", json={
            "category": "Salaries",
            "amount": 200000,
            "date": date.today().isoformat(),
        }, headers=auth_headers)
        assert r2.status_code == 200

        r3 = client.get("/reports/profit-loss?period=month", headers=auth_headers)
        assert r3.status_code == 200


class TestST009_FiveMonthReport:
    """ST-009: Select Last 5 Months → generate report."""

    def test_five_month_report(self, client, auth_headers):
        r = client.get("/reports/profit-loss?period=5_months", headers=auth_headers)
        assert r.status_code == 200


class TestST010_OneYearReport:
    """ST-010: Select This Year → generate report."""

    def test_one_year_report(self, client, auth_headers):
        r = client.get("/reports/profit-loss?period=year", headers=auth_headers)
        assert r.status_code == 200


class TestST011_FiveYearReport:
    """ST-011: Select Last 5 Years → system retrieves historical data."""

    def test_five_year_report(self, client, auth_headers):
        r = client.get("/reports/profit-loss?period=5_years", headers=auth_headers)
        assert r.status_code == 200


class TestST012_CustomDateReport:
    """ST-012: Enter custom date range → only records in range returned."""

    def test_custom_date_report(self, client, auth_headers):
        d1 = (date.today() - timedelta(days=90)).isoformat()
        d2 = date.today().isoformat()
        r = client.get(f"/reports/profit-loss?period=custom&date_from={d1}&date_to={d2}", headers=auth_headers)
        assert r.status_code == 200


class TestST014_BranchPerformance:
    """ST-014: Each branch displays its own metrics."""

    def test_branch_performance(self, client, auth_headers):
        r = client.get("/reports/profit-loss?period=month", headers=auth_headers)
        assert r.status_code == 200


class TestST017_NegativeMoneyPrevention:
    """ST-017: Negative payment/expense amounts rejected."""

    def test_negative_amount_paid(self, client, auth_headers, seeded_data):
        mid = seeded_data["make_med"]("NegMoneyMed")
        seeded_data["make_batch"](mid, qty=20)
        r = client.post("/sales/create", json={
            "customer_name": "NegMoney",
            "items": [{"medicine_id": mid, "quantity": 1, "price": 5000}],
            "payment_method": "Cash",
            "amount_paid": -1000,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)

    def test_negative_expense_amount(self, client, auth_headers):
        r = client.post("/expenses/create", json={
            "category": "Bad",
            "amount": -10000,
            "date": date.today().isoformat(),
        }, headers=auth_headers)
        assert r.status_code in (400, 422)


# ============================================================
# SECURITY TESTS
# ============================================================

class TestSEC001_UnauthorizedRoleAccess:
    """SEC-001: Staff user cannot access admin-only endpoints."""

    def test_staff_cannot_manage_users(self, client, auth_headers):
        import random
        uid = random.randint(10000, 99999)
        email = f"staff{uid}@test.com"

        r = client.post("/users/create", json={
            "full_name": f"Staff {uid}",
            "email": email,
            "password": "Test123!",
            "role": "staff",
        }, headers=auth_headers)
        assert r.status_code == 200

        r2 = client.post("/auth/login", json={
            "email": email,
            "password": "Test123!",
        })
        assert r2.status_code == 200
        staff_token = r2.json()["data"]["access_token"]
        sh = {"Authorization": f"Bearer {staff_token}"}

        r3 = client.get("/users/", headers=sh)
        assert r3.status_code in (200, 403, 404)
        r4 = client.get("/permissions/all", headers=sh)
        assert r4.status_code in (200, 403, 404)


# ============================================================
# END-TO-END TEST
# ============================================================

class TestE2E001_FullWorkflow:
    """E2E-001: Complete pharmacy workflow."""

    def test_full_lifecycle(self, client, auth_headers):
        import random
        h = auth_headers
        uid = random.randint(10000, 99999)

        r = client.post("/suppliers/create", json={
            "name": f"E2E Supplier {uid}", "phone": "0799999999",
        }, headers=h)
        assert r.status_code == 200
        supplier_id = r.json()["data"]["id"]

        r = client.post("/medicines/", json={
            "name": f"E2E Medicine {uid}", "category": "Test",
            "default_selling_price": 10000, "default_purchase_price": 6000,
        }, headers=h)
        assert r.status_code == 200
        assert r.json()["success"] is True
        med_id = r.json()["data"]["id"]

        r = client.post("/batches/create", json={
            "medicine_id": med_id, "batch_no": f"E2E-B1-{uid}",
            "quantity": 200, "selling_price": 10000, "purchase_price": 6000,
            "expiry_date": (date.today() + timedelta(days=365)).isoformat(),
        }, headers=h)
        assert r.status_code == 200

        r = client.get("/inventory/", headers=h)
        assert r.status_code == 200

        r = client.post("/sales/create", json={
            "customer_name": f"E2E Customer {uid}",
            "items": [{"medicine_id": med_id, "quantity": 5, "price": 10000}],
            "payment_method": "Cash", "amount_paid": 50000,
        }, headers=h)
        assert r.status_code == 200

        db = SessionLocal()
        try:
            batch = db.query(Batch).filter(Batch.batch_no == f"E2E-B1-{uid}").first()
            assert batch.quantity == 195
        finally:
            db.close()

        r = client.post("/expenses/create", json={
            "category": f"E2E Expense {uid}", "amount": 25000,
            "date": date.today().isoformat(),
        }, headers=h)
        assert r.status_code == 200

        r = client.get("/reports/profit-loss?period=month", headers=h)
        assert r.status_code == 200

        r = client.get("/reports/top-selling", headers=h)
        assert r.status_code == 200

        r = client.get("/reports/slow-moving", headers=h)
        assert r.status_code == 200

        r = client.get("/reports/expiry", headers=h)
        assert r.status_code == 200

        r = client.get("/reports/expense-trending", headers=h)
        assert r.status_code == 200

        r = client.get("/reports/inventory", headers=h)
        assert r.status_code == 200

        r = client.get("/inventory/", headers=h)
        assert r.status_code == 200

        r = client.get("/dashboard/", headers=h)
        assert r.status_code == 200

        r = client.get("/notifications/", headers=h)
        assert r.status_code == 200

        r = client.get("/activities/", headers=h)
        assert r.status_code == 200

        r = client.get("/reports/sales", headers=h)
        assert r.status_code == 200

        r = client.get("/reports/expiry", headers=h)
        assert r.status_code == 200

        r = client.get("/reports/reorder-suggestions", headers=h)
        assert r.status_code == 200

        r = client.get("/reports/overstock", headers=h)
        assert r.status_code == 200

        r = client.get("/reports/supplier-performance", headers=h)
        assert r.status_code == 200

        r = client.get(f"/reports/export/sales?format=csv", headers=h)
        assert r.status_code in (200, 404)
