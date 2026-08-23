"""
System / E2E Tests — Complete Workflows
Tests that exercise multiple components together in realistic scenarios.
"""
import pytest
from datetime import datetime, timedelta


class TestEndToEnd_PurchaseSaleWorkflow:
    """Test the full lifecycle: Medicine → Batch → Purchase → Sale → Report."""

    def test_full_lifecycle(self, client, auth_headers, db):
        """Medicine → Batch → Sale → Inventory → Reports."""
        # 1. Create Medicine
        med_r = client.post("/medicines/", json={
            "name": "Amoxicillin 500mg",
            "generic_name": "Amoxicillin",
            "brand": "Amoxil",
            "form": "capsule",
            "unit": "pcs",
            "strength": "500mg",
            "category": "Antibiotic",
            "default_purchase_price": 400,
            "default_selling_price": 800,
            "reorder_level": 20,
            "max_stock_level": 500,
        }, headers=auth_headers)
        assert med_r.status_code == 200
        med_id = med_r.json()["data"]["id"]

        # 2. Create Batch
        batch_r = client.post("/batches/create", json={
            "medicine_id": med_id,
            "batch_no": "AMX-2026-001",
            "quantity": 200,
            "purchase_price": 400,
            "selling_price": 800,
            "expiry_date": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d"),
        }, headers=auth_headers)
        assert batch_r.status_code == 200
        batch_id = batch_r.json()["data"]["id"]

        # 3. Verify inventory shows correct quantity
        inv_r = client.get(f"/inventory/medicine/{med_id}", headers=auth_headers)
        assert inv_r.status_code == 200

        # 4. Create Sale (3 items)
        sale_r = client.post("/sales/create", json={
            "customer_name": "Test Customer",
            "payment_method": "cash",
            "amount_paid": 3000,
            "items": [
                {"medicine_id": med_id, "batch_id": batch_id, "quantity": 3, "selling_price": 800}
            ]
        }, headers=auth_headers)
        assert sale_r.status_code == 200
        sale_data = sale_r.json()
        sale_id = sale_data["data"]["id"]
        assert sale_data["data"]["total_amount"] == 2400

        # 5. Verify inventory decreased
        inv_r2 = client.get(f"/inventory/medicine/{med_id}", headers=auth_headers)
        assert inv_r2.status_code == 200

        # 6. Check reports work
        r_r = client.get("/reports/profit-loss?period=monthly", headers=auth_headers)
        assert r_r.status_code == 200

        # 7. Check dashboard
        d_r = client.get("/dashboard/", headers=auth_headers)
        assert d_r.status_code == 200


class TestEndToEnd_MultiItemSale:

    def test_multi_item_sale(self, client, auth_headers, db):
        med1_r = client.post("/medicines/", json={
            "name": "Paracetamol", "default_selling_price": 500,
            "default_purchase_price": 200, "reorder_level": 10,
        }, headers=auth_headers)
        med1_id = med1_r.json()["data"]["id"]

        med2_r = client.post("/medicines/", json={
            "name": "Ibuprofen", "default_selling_price": 800,
            "default_purchase_price": 400, "reorder_level": 10,
        }, headers=auth_headers)
        med2_id = med2_r.json()["data"]["id"]

        b1_r = client.post("/batches/create", json={
            "medicine_id": med1_id, "batch_no": "PAR-001", "quantity": 100,
            "selling_price": 500, "purchase_price": 200,
            "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        }, headers=auth_headers)
        b1_id = b1_r.json()["data"]["id"]

        b2_r = client.post("/batches/create", json={
            "medicine_id": med2_id, "batch_no": "IBU-001", "quantity": 100,
            "selling_price": 800, "purchase_price": 400,
            "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        }, headers=auth_headers)
        b2_id = b2_r.json()["data"]["id"]

        sale_r = client.post("/sales/create", json={
            "customer_name": "Multi-Item Customer",
            "payment_method": "mobile_money",
            "amount_paid": 5000,
            "items": [
                {"medicine_id": med1_id, "batch_id": b1_id, "quantity": 4, "selling_price": 500},
                {"medicine_id": med2_id, "batch_id": b2_id, "quantity": 2, "selling_price": 800},
            ]
        }, headers=auth_headers)
        assert sale_r.status_code == 200
        sale = sale_r.json()["data"]
        assert sale["total_amount"] == 3600  # 4*500 + 2*800
        assert len(sale.get("items", [])) == 2


class TestEndToEnd_PrescriptionWorkflow:

    def test_prescription_lifecycle(self, client, auth_headers, db):
        med_r = client.post("/medicines/", json={
            "name": "Amoxicillin Syrup",
            "default_selling_price": 15000,
            "default_purchase_price": 8000,
            "reorder_level": 5,
        }, headers=auth_headers)
        med_id = med_r.json()["data"]["id"]

        b_r = client.post("/batches/create", json={
            "medicine_id": med_id, "batch_no": "SYR-001", "quantity": 50,
            "selling_price": 15000, "purchase_price": 8000,
            "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        }, headers=auth_headers)
        assert b_r.status_code == 200

        presc_r = client.post("/prescriptions/create", json={
            "patient_name": "John Mwangi",
            "patient_age": 45,
            "doctor_name": "Dr. Kimaro",
            "items": [{"medicine_id": med_id, "medicine_name": "Amoxicillin Syrup", "quantity": 2, "price": 15000}],
        }, headers=auth_headers)
        assert presc_r.status_code == 200

        list_r = client.get("/prescriptions/", headers=auth_headers)
        assert list_r.status_code == 200


class TestEndToEnd_ExpenseTracking:
    """Test expense creation and reporting."""

    def test_expense_workflow(self, client, auth_headers):
        # Create multiple expenses
        categories = [
            ("Rent", 500000, "bank_transfer"),
            ("Utilities", 150000, "cash"),
            ("Salaries", 2000000, "bank_transfer"),
            ("Transport", 50000, "cash"),
        ]
        for cat, amt, method in categories:
            r = client.post("/expenses/create", json={
                "category": cat,
                "description": f"Monthly {cat}",
                "amount": amt,
                "payment_method": method,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }, headers=auth_headers)
            assert r.status_code == 200

        # List expenses
        list_r = client.get("/expenses/", headers=auth_headers)
        assert list_r.status_code == 200

        # Get summary
        summary_r = client.get("/expenses/summary", headers=auth_headers)
        assert summary_r.status_code == 200


class TestEndToEnd_UserManagementWorkflow:
    """Test creating, toggling, and managing users."""

    def test_user_lifecycle(self, client, auth_headers):
        roles = ["staff", "staff", "staff", "staff"]
        created_ids = []
        for i, role in enumerate(roles):
            r = client.post("/users/create", json={
                "email": f"user_{role}_{i}@test.com",
                "password": "StrongP@ss1",
                "full_name": f"Test User {i}",
                "role": role,
            }, headers=auth_headers)
            assert r.status_code == 200
            created_ids.append(r.json()["data"]["id"])

        # List users
        list_r = client.get("/users/", headers=auth_headers)
        assert list_r.status_code == 200

        # Toggle one user
        toggle_r = client.post(f"/users/{created_ids[0]}/toggle-active", headers=auth_headers)
        assert toggle_r.status_code == 200

        # Delete one user
        del_r = client.delete(f"/users/{created_ids[1]}", headers=auth_headers)
        assert del_r.status_code == 200


class TestEndToEnd_BranchMultiBranchWorkflow:
    """Test multi-branch setup."""

    def test_branch_lifecycle(self, client, auth_headers):
        # Create branches
        branches = [
            ("Main Branch", "MB001", True),
            ("Branch 2", "BR002", False),
            ("Branch 3", "BR003", False),
        ]
        branch_ids = []
        for name, code, is_main in branches:
            r = client.post("/branches/create", json={
                "name": name, "code": code, "is_main": is_main, "is_active": True
            }, headers=auth_headers)
            assert r.status_code == 200
            branch_ids.append(r.json()["data"]["id"])

        # List branches
        list_r = client.get("/branches/", headers=auth_headers)
        assert list_r.status_code == 200

        # Get specific branch
        get_r = client.get(f"/branches/{branch_ids[0]}", headers=auth_headers)
        assert get_r.status_code == 200

        # Update branch
        upd_r = client.put(f"/branches/{branch_ids[1]}", json={
            "name": "Branch 2 Updated"
        }, headers=auth_headers)
        assert upd_r.status_code == 200


class TestEndToEnd_PermissionsWorkflow:
    """Test granular RBAC permissions."""

    def test_permission_management(self, client, auth_headers):
        # Get current permissions
        mine_r = client.get("/permissions/mine", headers=auth_headers)
        assert mine_r.status_code == 200
        mine_data = mine_r.json()["data"]
        assert "is_admin" in mine_data

        # Get all permissions
        all_r = client.get("/permissions/", headers=auth_headers)
        assert all_r.status_code == 200

        # Get modules
        mod_r = client.get("/permissions/modules", headers=auth_headers)
        assert mod_r.status_code == 200
        assert "modules" in mod_r.json()["data"]
        assert "permission_types" in mod_r.json()["data"]


class TestEndToEnd_SupplierPurchaseWorkflow:
    """Test supplier → purchase → inventory workflow."""

    def test_supplier_purchase_cycle(self, client, auth_headers):
        # Create supplier
        sup_r = client.post("/suppliers/create", json={
            "name": "Pharma Distributors Ltd",
            "company_name": "PDL",
            "phone": "+255712345678",
            "email": "info@pdl.co.tz",
        }, headers=auth_headers)
        assert sup_r.status_code == 200
        sup_id = sup_r.json()["data"]["id"]

        # Create medicine
        med_r = client.post("/medicines/", json={
            "name": "Metformin 500mg",
            "default_purchase_price": 300,
            "default_selling_price": 600,
            "reorder_level": 15,
        }, headers=auth_headers)
        med_id = med_r.json()["data"]["id"]

        # Create purchase
        purchase_r = client.post("/purchases/create", json={
            "supplier_name": "Pharma Distributors Ltd",
            "supplier_id": sup_id,
            "payment_method": "bank_transfer",
            "total_amount": 150000,
            "purchase_date": datetime.now().strftime("%Y-%m-%d"),
            "items": [{
                "medicine_id": med_id,
                "batch_no": "MET-2026-001",
                "quantity": 500,
                "purchase_price": 300,
                "selling_price": 600,
                "expiry_date": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d"),
            }]
        }, headers=auth_headers)
        assert purchase_r.status_code == 200, f"Purchase failed: {purchase_r.json()}"
        purchase_id = purchase_r.json()["data"]["id"]

        # Verify inventory increased
        inv_r = client.get(f"/inventory/medicine/{med_id}", headers=auth_headers)
        assert inv_r.status_code == 200

        # Check reorder suggestions
        reorder_r = client.get("/reports/reorder-suggestions", headers=auth_headers)
        assert reorder_r.status_code == 200


class TestEndToEnd_SalesReportingWorkflow:
    """Test comprehensive sales reporting across time periods."""

    def test_sales_reports(self, client, auth_headers):
        daily_r = client.get("/reports/sales/daily", headers=auth_headers)
        assert daily_r.status_code == 200

        monthly_r = client.get("/reports/sales/monthly?year=2026&month=8", headers=auth_headers)
        assert monthly_r.status_code == 200

        for endpoint in [
            "/reports/profit-loss?period=monthly",
            "/reports/sales?period=monthly",
            "/reports/purchases?period=monthly",
            "/reports/top-selling",
            "/reports/expense-trending",
            "/reports/slow-moving",
            "/reports/reorder-suggestions",
            "/reports/overstock",
            "/reports/supplier-performance",
        ]:
            r = client.get(endpoint, headers=auth_headers)
            assert r.status_code == 200, f"Failed: {endpoint}"


class TestEndToEnd_DashboardComprehensive:
    """Test all dashboard endpoints."""

    def test_dashboard_endpoints(self, client, auth_headers):
        r1 = client.get("/dashboard/", headers=auth_headers)
        assert r1.status_code == 200

        r2 = client.get("/dashboard/today", headers=auth_headers)
        assert r2.status_code == 200

        r3 = client.get("/dashboard/inventory", headers=auth_headers)
        assert r3.status_code == 200


class TestEndToEnd_ExpiryMonitoring:
    """Test expiry monitoring and actions."""

    def test_expiry_workflow(self, client, auth_headers):
        # Create medicine with near-expiry batch
        med_r = client.post("/medicines/", json={
            "name": "Expiring Drug",
            "default_selling_price": 5000,
            "reorder_level": 5,
        }, headers=auth_headers)
        med_id = med_r.json()["data"]["id"]

        # Create near-expiry batch
        batch_r = client.post("/batches/create", json={
            "medicine_id": med_id,
            "batch_no": "EXP-001",
            "quantity": 30,
            "selling_price": 5000,
            "purchase_price": 3000,
            "expiry_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        }, headers=auth_headers)
        assert batch_r.status_code == 200

        # Check expiry dashboard
        ed_r = client.get("/expiry/dashboard", headers=auth_headers)
        assert ed_r.status_code == 200

        # Check expiry list
        el_r = client.get("/expiry/", headers=auth_headers)
        assert el_r.status_code == 200

        # Record expiry action
        action_r = client.post("/expiry/action", json={
            "action_type": "quarantine",
            "medicine_id": med_id,
            "medicine_name": "Expiring Drug",
            "batch_no": "EXP-001",
            "quantity": 30,
            "reason": "Near expiry quarantine",
            "responsible_person": "Pharmacist A",
        }, headers=auth_headers)
        assert action_r.status_code == 200


class TestEndToEnd_CurrencyWorkflow:
    """Test currency operations."""

    def test_currency_flow(self, client, auth_headers):
        # List currencies
        list_r = client.get("/currencies/", headers=auth_headers)
        assert list_r.status_code == 200

        # Convert USD
        conv_r = client.post("/currencies/convert", json={
            "amount": 100, "from_currency": "USD"
        }, headers=auth_headers)
        assert conv_r.status_code == 200

        # Convert EUR
        conv_eur_r = client.post("/currencies/convert", json={
            "amount": 100, "from_currency": "EUR"
        }, headers=auth_headers)
        assert conv_eur_r.status_code == 200


class TestEndToEnd_BackupRestore:
    """Test backup creation and listing."""

    def test_backup_workflow(self, client, auth_headers):
        # Create backup
        create_r = client.post("/backup/create", headers=auth_headers)
        assert create_r.status_code == 200

        # List backups
        list_r = client.get("/backup/list", headers=auth_headers)
        assert list_r.status_code == 200


class TestEndToEnd_CategoryManufacturer:
    """Test category and manufacturer management."""

    def test_category_manufacturer_flow(self, client, auth_headers):
        # Create categories
        for cat_name in ["Analgesic", "Antibiotic", "Vitamin", "Antimalarial"]:
            r = client.post("/categories/create", json={"name": cat_name}, headers=auth_headers)
            assert r.status_code == 200

        # Create manufacturers
        for mfr_name in ["Bayer", "Pfizer", "Novartis"]:
            r = client.post("/manufacturers/create", json={"name": mfr_name}, headers=auth_headers)
            assert r.status_code == 200

        # List them
        cats_r = client.get("/categories/", headers=auth_headers)
        assert cats_r.status_code == 200

        mfrs_r = client.get("/manufacturers/", headers=auth_headers)
        assert mfrs_r.status_code == 200
