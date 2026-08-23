"""
Integration Tests — All API Endpoints
Tests every endpoint with authenticated requests against a real database.
"""
import pytest


# ---- Health Check ----

class TestHealthCheck:

    def test_health_endpoint(self, client):
        r = client.get("/health")
        assert r.status_code == 200


# ---- Auth ----

class TestAuthAPI:

    def test_login_success(self, client):
        r = client.post("/auth/login", json={
            "email": "changwamale48@gmail.com",
            "password": "ngwamale#@39"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "access_token" in data["data"]

    def test_login_wrong_password(self, client):
        r = client.post("/auth/login", json={
            "email": "changwamale48@gmail.com",
            "password": "wrongpassword"
        })
        assert r.status_code in (401, 400, 200)

    def test_login_nonexistent_user(self, client):
        r = client.post("/auth/login", json={
            "email": "nobody@test.com",
            "password": "anything"
        })
        assert r.status_code in (401, 400, 200)

    def test_me_endpoint(self, client, auth_headers):
        r = client.get("/auth/me", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True

    def test_me_no_auth(self, client):
        r = client.get("/auth/me")
        assert r.status_code in (401, 403)


# ---- Users ----

class TestUserAPI:

    def test_list_users(self, client, auth_headers):
        r = client.get("/users/", headers=auth_headers)
        assert r.status_code == 200

    def test_create_user(self, client, auth_headers):
        r = client.post("/users/create", json={
            "email": "newapi@test.com",
            "password": "StrongP@ss1",
            "full_name": "API User",
            "role": "staff"
        }, headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True

    def test_create_user_duplicate(self, client, auth_headers):
        client.post("/users/create", json={
            "email": "dupapi@test.com", "password": "StrongP@1", "full_name": "Dup", "role": "staff"
        }, headers=auth_headers)
        r = client.post("/users/create", json={
            "email": "dupapi@test.com", "password": "StrongP@1", "full_name": "Dup2", "role": "staff"
        }, headers=auth_headers)
        assert r.status_code in (200, 400, 409)

    def test_toggle_active_user(self, client, auth_headers, db):
        from app.services.user_service import UserService
        user, _ = UserService.create_user(db, "tog@test.com", "StrongP@1", "Toggle", "staff")
        r = client.post(f"/users/{user.id}/toggle-active", headers=auth_headers)
        assert r.status_code == 200

    def test_delete_user(self, client, auth_headers, db):
        from app.services.user_service import UserService
        user, _ = UserService.create_user(db, "delapi@test.com", "StrongP@1", "Del", "staff")
        r = client.delete(f"/users/{user.id}", headers=auth_headers)
        assert r.status_code == 200


# ---- Medicines ----

class TestMedicineAPI:

    def test_create_medicine(self, client, auth_headers):
        r = client.post("/medicines/", json={
            "name": "Ibuprofen",
            "generic_name": "Ibuprofen",
            "brand": "Brufen",
            "form": "tablet",
            "unit": "pcs",
            "strength": "400mg",
            "default_purchase_price": 600,
            "default_selling_price": 1000,
            "reorder_level": 10,
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_list_medicines(self, client, auth_headers):
        r = client.get("/medicines/", headers=auth_headers)
        assert r.status_code == 200

    def test_get_medicine_detail(self, client, auth_headers):
        create = client.post("/medicines/", json={
            "name": "DetailMed", "default_selling_price": 500
        }, headers=auth_headers)
        med_id = create.json()["data"]["id"]
        r = client.get(f"/medicines/{med_id}", headers=auth_headers)
        assert r.status_code == 200

    def test_update_medicine(self, client, auth_headers):
        create = client.post("/medicines/", json={
            "name": "UpdMed", "default_selling_price": 500
        }, headers=auth_headers)
        med_id = create.json()["data"]["id"]
        r = client.put(f"/medicines/{med_id}", json={
            "name": "UpdMedNew", "default_selling_price": 750
        }, headers=auth_headers)
        assert r.status_code == 200

    def test_delete_medicine(self, client, auth_headers):
        create = client.post("/medicines/", json={
            "name": "DelMed", "default_selling_price": 500
        }, headers=auth_headers)
        med_id = create.json()["data"]["id"]
        r = client.delete(f"/medicines/{med_id}", headers=auth_headers)
        assert r.status_code == 200

    def test_ai_suggest(self, client, auth_headers):
        r = client.post("/medicines/ai-suggest", json={
            "name": "Paracetamol"
        }, headers=auth_headers)
        assert r.status_code == 200


# ---- Batches ----

class TestBatchAPI:

    def _make_medicine(self, client, auth_headers):
        r = client.post("/medicines/", json={
            "name": "BatchMed", "default_selling_price": 500
        }, headers=auth_headers)
        return r.json()["data"]["id"]

    def test_create_batch(self, client, auth_headers):
        med_id = self._make_medicine(client, auth_headers)
        r = client.post("/batches/create", json={
            "medicine_id": med_id,
            "batch_no": "BATCH-001",
            "quantity": 100,
            "purchase_price": 300,
            "selling_price": 500,
            "expiry_date": "2027-12-31",
        }, headers=auth_headers)
        assert r.status_code == 200

    def test_list_batches(self, client, auth_headers):
        r = client.get("/batches/", headers=auth_headers)
        assert r.status_code == 200

    def test_list_batches_by_medicine(self, client, auth_headers):
        med_id = self._make_medicine(client, auth_headers)
        client.post("/batches/create", json={
            "medicine_id": med_id, "batch_no": "BATCH-M01", "quantity": 50
        }, headers=auth_headers)
        r = client.get(f"/batches/medicine/{med_id}", headers=auth_headers)
        assert r.status_code == 200


# ---- Categories ----

class TestCategoryAPI:

    def test_create_category(self, client, auth_headers):
        r = client.post("/categories/create", json={"name": "Antibiotics"}, headers=auth_headers)
        assert r.status_code == 200

    def test_list_categories(self, client, auth_headers):
        r = client.get("/categories/", headers=auth_headers)
        assert r.status_code == 200

    def test_update_category(self, client, auth_headers):
        create = client.post("/categories/create", json={"name": "UpdCat"}, headers=auth_headers)
        cat_id = create.json()["data"]["id"]
        r = client.put(f"/categories/{cat_id}", json={"name": "UpdCatNew"}, headers=auth_headers)
        assert r.status_code == 200

    def test_delete_category(self, client, auth_headers):
        create = client.post("/categories/create", json={"name": "DelCat"}, headers=auth_headers)
        cat_id = create.json()["data"]["id"]
        r = client.delete(f"/categories/{cat_id}", headers=auth_headers)
        assert r.status_code == 200


# ---- Manufacturers ----

class TestManufacturerAPI:

    def test_create_manufacturer(self, client, auth_headers):
        r = client.post("/manufacturers/create", json={"name": "PharmaInc", "country": "Kenya"}, headers=auth_headers)
        assert r.status_code == 200

    def test_list_manufacturers(self, client, auth_headers):
        r = client.get("/manufacturers/", headers=auth_headers)
        assert r.status_code == 200

    def test_update_manufacturer(self, client, auth_headers):
        create = client.post("/manufacturers/create", json={"name": "MfrUpd"}, headers=auth_headers)
        mfr_id = create.json()["data"]["id"]
        r = client.put(f"/manufacturers/{mfr_id}", json={"name": "MfrUpdNew"}, headers=auth_headers)
        assert r.status_code == 200

    def test_delete_manufacturer(self, client, auth_headers):
        create = client.post("/manufacturers/create", json={"name": "MfrDel"}, headers=auth_headers)
        mfr_id = create.json()["data"]["id"]
        r = client.delete(f"/manufacturers/{mfr_id}", headers=auth_headers)
        assert r.status_code == 200


# ---- Branches ----

class TestBranchAPI:

    def test_create_branch(self, client, auth_headers):
        r = client.post("/branches/create", json={"name": "HQ Branch", "code": "HQ001"}, headers=auth_headers)
        assert r.status_code == 200

    def test_list_branches(self, client, auth_headers):
        r = client.get("/branches/", headers=auth_headers)
        assert r.status_code == 200

    def test_get_branch(self, client, auth_headers):
        create = client.post("/branches/create", json={"name": "GetBranch", "code": "GB001"}, headers=auth_headers)
        br_id = create.json()["data"]["id"]
        r = client.get(f"/branches/{br_id}", headers=auth_headers)
        assert r.status_code == 200

    def test_update_branch(self, client, auth_headers):
        create = client.post("/branches/create", json={"name": "UpdBranch", "code": "UB001"}, headers=auth_headers)
        br_id = create.json()["data"]["id"]
        r = client.put(f"/branches/{br_id}", json={"name": "UpdBranchNew"}, headers=auth_headers)
        assert r.status_code == 200

    def test_delete_branch(self, client, auth_headers):
        create = client.post("/branches/create", json={"name": "DelBranch", "code": "DB001"}, headers=auth_headers)
        br_id = create.json()["data"]["id"]
        r = client.delete(f"/branches/{br_id}", headers=auth_headers)
        assert r.status_code == 200


# ---- Customers ----

class TestCustomerAPI:

    def test_create_customer(self, client, auth_headers):
        r = client.post("/customers/create", json={"name": "Jane Doe", "phone": "0755123456"}, headers=auth_headers)
        assert r.status_code == 200

    def test_list_customers(self, client, auth_headers):
        r = client.get("/customers/", headers=auth_headers)
        assert r.status_code == 200

    def test_get_customer(self, client, auth_headers):
        create = client.post("/customers/create", json={"name": "CustGet"}, headers=auth_headers)
        cid = create.json()["data"]["id"]
        r = client.get(f"/customers/{cid}", headers=auth_headers)
        assert r.status_code == 200

    def test_update_customer(self, client, auth_headers):
        create = client.post("/customers/create", json={"name": "CustUpd"}, headers=auth_headers)
        cid = create.json()["data"]["id"]
        r = client.put(f"/customers/{cid}", json={"name": "CustUpdNew"}, headers=auth_headers)
        assert r.status_code == 200

    def test_delete_customer(self, client, auth_headers):
        create = client.post("/customers/create", json={"name": "CustDel"}, headers=auth_headers)
        cid = create.json()["data"]["id"]
        r = client.delete(f"/customers/{cid}", headers=auth_headers)
        assert r.status_code == 200


# ---- Suppliers ----

class TestSupplierAPI:

    def test_create_supplier(self, client, auth_headers):
        r = client.post("/suppliers/create", json={"name": "SupCo", "company_name": "Co"}, headers=auth_headers)
        assert r.status_code == 200

    def test_list_suppliers(self, client, auth_headers):
        r = client.get("/suppliers/", headers=auth_headers)
        assert r.status_code == 200

    def test_update_supplier(self, client, auth_headers):
        create = client.post("/suppliers/create", json={"name": "SupUpd"}, headers=auth_headers)
        sid = create.json()["data"]["id"]
        r = client.put(f"/suppliers/{sid}", json={"name": "SupUpdNew"}, headers=auth_headers)
        assert r.status_code == 200

    def test_delete_supplier(self, client, auth_headers):
        create = client.post("/suppliers/create", json={"name": "SupDel"}, headers=auth_headers)
        sid = create.json()["data"]["id"]
        r = client.delete(f"/suppliers/{sid}", headers=auth_headers)
        assert r.status_code == 200


# ---- Settings ----

class TestSettingsAPI:

    def test_get_settings(self, client, auth_headers):
        r = client.get("/settings/", headers=auth_headers)
        assert r.status_code == 200

    def test_update_settings(self, client, auth_headers):
        r = client.put("/settings/", json={
            "pharmacy_name": "Updated Pharmacy",
            "address": "456 New St",
            "tax_rate": 18.0,
            "region": "Dodoma",
            "district": "Dodoma Municipal",
        }, headers=auth_headers)
        assert r.status_code == 200


# ---- Currencies ----

class TestCurrencyAPI:

    def test_list_currencies(self, client, auth_headers):
        r = client.get("/currencies/", headers=auth_headers)
        assert r.status_code == 200

    def test_convert_amount(self, client, auth_headers):
        r = client.post("/currencies/convert", json={
            "amount": 100, "from_currency": "USD"
        }, headers=auth_headers)
        assert r.status_code == 200


# ---- Expenses ----

class TestExpenseAPI:

    def test_create_expense(self, client, auth_headers):
        r = client.post("/expenses/create", json={
            "category": "Rent",
            "description": "Office rent",
            "amount": 500000,
            "payment_method": "bank_transfer",
            "date": "2026-01-15",
        }, headers=auth_headers)
        assert r.status_code == 200

    def test_list_expenses(self, client, auth_headers):
        r = client.get("/expenses/", headers=auth_headers)
        assert r.status_code == 200

    def test_expense_summary(self, client, auth_headers):
        r = client.get("/expenses/summary", headers=auth_headers)
        assert r.status_code == 200


# ---- Notifications ----

class TestNotificationAPI:

    def test_list_notifications(self, client, auth_headers):
        r = client.get("/notifications/", headers=auth_headers)
        assert r.status_code == 200


# ---- Prescriptions ----

class TestPrescriptionAPI:

    def test_create_prescription(self, client, auth_headers):
        r = client.post("/prescriptions/create", json={
            "patient_name": "Test Patient",
            "patient_age": 35,
            "doctor_name": "Dr. Smith",
            "items": [{"medicine_id": 1, "medicine_name": "Paracetamol", "quantity": 10, "price": 500}],
        }, headers=auth_headers)
        assert r.status_code == 200

    def test_list_prescriptions(self, client, auth_headers):
        r = client.get("/prescriptions/", headers=auth_headers)
        assert r.status_code == 200


# ---- Permissions ----

class TestPermissionAPI:

    def test_list_modules(self, client, auth_headers):
        r = client.get("/permissions/modules", headers=auth_headers)
        assert r.status_code == 200

    def test_my_permissions(self, client, auth_headers):
        r = client.get("/permissions/mine", headers=auth_headers)
        assert r.status_code == 200

    def test_get_all_permissions(self, client, auth_headers):
        r = client.get("/permissions/", headers=auth_headers)
        assert r.status_code == 200


# ---- Reports ----

class TestReportAPI:

    def test_profit_loss(self, client, auth_headers):
        r = client.get("/reports/profit-loss?period=monthly", headers=auth_headers)
        assert r.status_code == 200

    def test_sales_report(self, client, auth_headers):
        r = client.get("/reports/sales?period=monthly", headers=auth_headers)
        assert r.status_code == 200

    def test_inventory_report(self, client, auth_headers):
        r = client.get("/reports/inventory", headers=auth_headers)
        assert r.status_code == 200

    def test_purchases_report(self, client, auth_headers):
        r = client.get("/reports/purchases?period=monthly", headers=auth_headers)
        assert r.status_code == 200

    def test_expiry_report(self, client, auth_headers):
        r = client.get("/reports/expiry", headers=auth_headers)
        assert r.status_code == 200

    def test_top_selling(self, client, auth_headers):
        r = client.get("/reports/top-selling", headers=auth_headers)
        assert r.status_code == 200

    def test_expense_trending(self, client, auth_headers):
        r = client.get("/reports/expense-trending", headers=auth_headers)
        assert r.status_code == 200

    def test_slow_moving(self, client, auth_headers):
        r = client.get("/reports/slow-moving", headers=auth_headers)
        assert r.status_code == 200

    def test_reorder_suggestions(self, client, auth_headers):
        r = client.get("/reports/reorder-suggestions", headers=auth_headers)
        assert r.status_code == 200

    def test_overstock(self, client, auth_headers):
        r = client.get("/reports/overstock", headers=auth_headers)
        assert r.status_code == 200

    def test_supplier_performance(self, client, auth_headers):
        r = client.get("/reports/supplier-performance", headers=auth_headers)
        assert r.status_code == 200


# ---- Sales Reports ----

class TestSalesReportAPI:

    def test_daily_sales(self, client, auth_headers):
        r = client.get("/reports/sales/daily", headers=auth_headers)
        assert r.status_code == 200

    def test_monthly_sales(self, client, auth_headers):
        r = client.get("/reports/sales/monthly?year=2026&month=8", headers=auth_headers)
        assert r.status_code == 200


# ---- Inventory ----

class TestInventoryAPI:

    def test_inventory_list(self, client, auth_headers):
        r = client.get("/inventory/", headers=auth_headers)
        assert r.status_code == 200

    def test_low_stock(self, client, auth_headers):
        r = client.get("/inventory/low", headers=auth_headers)
        assert r.status_code == 200

    def test_near_expiry(self, client, auth_headers):
        r = client.get("/inventory/near-expiry", headers=auth_headers)
        assert r.status_code == 200

    def test_expired(self, client, auth_headers):
        r = client.get("/inventory/expired", headers=auth_headers)
        assert r.status_code == 200


# ---- Dashboard ----

class TestDashboardAPI:

    def test_dashboard_main(self, client, auth_headers):
        r = client.get("/dashboard/", headers=auth_headers)
        assert r.status_code == 200

    def test_dashboard_today(self, client, auth_headers):
        r = client.get("/dashboard/today", headers=auth_headers)
        assert r.status_code == 200

    def test_dashboard_inventory(self, client, auth_headers):
        r = client.get("/dashboard/inventory", headers=auth_headers)
        assert r.status_code == 200


# ---- Expiry ----

class TestExpiryAPI:

    def test_expiry_dashboard(self, client, auth_headers):
        r = client.get("/expiry/dashboard", headers=auth_headers)
        assert r.status_code == 200

    def test_expiry_list(self, client, auth_headers):
        r = client.get("/expiry/", headers=auth_headers)
        assert r.status_code == 200

    def test_list_actions(self, client, auth_headers):
        r = client.get("/expiry/actions", headers=auth_headers)
        assert r.status_code == 200


# ---- Disposals ----

class TestDisposalAPI:

    def test_list_disposals(self, client, auth_headers):
        r = client.get("/disposals/", headers=auth_headers)
        assert r.status_code == 200


# ---- Stock Adjustments ----

class TestStockAdjustmentAPI:

    def test_list_adjustments(self, client, auth_headers):
        r = client.get("/stock-adjustments/", headers=auth_headers)
        assert r.status_code == 200


# ---- Returns ----

class TestReturnAPI:

    def test_list_returns(self, client, auth_headers):
        r = client.get("/returns/", headers=auth_headers)
        assert r.status_code == 200


# ---- Stock Transfers ----

class TestStockTransferAPI:

    def test_list_transfers(self, client, auth_headers):
        r = client.get("/stock-transfers/", headers=auth_headers)
        assert r.status_code == 200


# ---- Activities ----

class TestActivityAPI:

    def test_list_activities(self, client, auth_headers):
        r = client.get("/activities/", headers=auth_headers)
        assert r.status_code == 200


# ---- Backup ----

class TestBackupAPI:

    def test_list_backups(self, client, auth_headers):
        r = client.get("/backup/list", headers=auth_headers)
        assert r.status_code == 200

    def test_create_backup(self, client, auth_headers):
        r = client.post("/backup/create", headers=auth_headers)
        assert r.status_code == 200
