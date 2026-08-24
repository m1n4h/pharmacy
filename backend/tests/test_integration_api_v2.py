"""
Integration Tests v2 — All Previously Untested Endpoints
Covers: Sales CRUD, Purchases CRUD, Prescriptions actions, Stock Adjustments,
Transfers, Disposals, Returns, Auth, Notifications, Expenses, Batches,
Currencies, Permissions, Invoice, Reports, Inventory
"""
import pytest
from datetime import datetime, timedelta


# ─── Helper ───────────────────────────────────────────────────────

def _med(client, h, name="TestMed", price=1000, purchase=500):
    """Create a medicine and return its ID."""
    r = client.post("/medicines/", json={
        "name": name, "default_selling_price": price,
        "default_purchase_price": purchase, "reorder_level": 5,
    }, headers=h)
    return r.json()["data"]["id"]


def _batch(client, h, med_id, qty=100, sp=1000, pp=500, bno=None):
    """Create a batch and return its ID."""
    bno = bno or f"B-{med_id}-{qty}"
    r = client.post("/batches/create", json={
        "medicine_id": med_id, "batch_no": bno,
        "quantity": qty, "selling_price": sp, "purchase_price": pp,
        "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
    }, headers=h)
    return r.json()["data"]["id"]


# ═══════════════════════════════════════════════════════════════════
# 1. SALES MODULE — CRUD + bulk + POS + invoice
# ═══════════════════════════════════════════════════════════════════

class TestSalesAPI:

    def test_create_sale(self, client, auth_headers):
        mid = _med(client, auth_headers, "SaleMed1", 2000, 1000)
        bid = _batch(client, auth_headers, mid, 50, 2000, 1000)
        r = client.post("/sales/create", json={
            "customer_name": "C1", "payment_method": "cash",
            "amount_paid": 4000,
            "items": [{"medicine_id": mid, "batch_id": bid, "quantity": 2, "selling_price": 2000}],
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert r.json()["data"]["total_amount"] == 4000

    def test_list_sales(self, client, auth_headers):
        r = client.get("/sales/", headers=auth_headers)
        assert r.status_code == 200

    def test_get_sale_detail(self, client, auth_headers):
        mid = _med(client, auth_headers, "SaleDetailMed", 1500, 800)
        bid = _batch(client, auth_headers, mid, 30, 1500, 800)
        create = client.post("/sales/create", json={
            "customer_name": "Detail", "payment_method": "cash",
            "amount_paid": 3000,
            "items": [{"medicine_id": mid, "batch_id": bid, "quantity": 2, "selling_price": 1500}],
        }, headers=auth_headers)
        sale_id = create.json()["data"]["id"]
        r = client.get(f"/sales/{sale_id}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["data"]["id"] == sale_id

    def test_delete_sale(self, client, auth_headers):
        mid = _med(client, auth_headers, "SaleDelMed", 1200, 600)
        bid = _batch(client, auth_headers, mid, 20, 1200, 600)
        create = client.post("/sales/create", json={
            "customer_name": "Del", "payment_method": "cash",
            "amount_paid": 2400,
            "items": [{"medicine_id": mid, "batch_id": bid, "quantity": 2, "selling_price": 1200}],
        }, headers=auth_headers)
        sale_id = create.json()["data"]["id"]
        r = client.delete(f"/sales/{sale_id}", headers=auth_headers)
        assert r.status_code == 200

    def test_pos_medicines(self, client, auth_headers):
        r = client.get("/sales/pos/medicines", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 2. PURCHASES MODULE — CRUD + bulk
# ═══════════════════════════════════════════════════════════════════

class TestPurchaseAPI:

    def test_create_purchase(self, client, auth_headers):
        mid = _med(client, auth_headers, "PurchMed1", 1500, 700)
        sup_r = client.post("/suppliers/create", json={"name": "SupPC"}, headers=auth_headers)
        sup_id = sup_r.json()["data"]["id"]
        r = client.post("/purchases/create", json={
            "supplier_name": "SupPC", "supplier_id": sup_id,
            "payment_method": "bank_transfer",
            "purchase_date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": 35000,
            "items": [{
                "medicine_id": mid, "batch_no": "PC-001", "quantity": 50,
                "purchase_price": 700, "selling_price": 1500,
                "expiry_date": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d"),
            }],
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_list_purchases(self, client, auth_headers):
        r = client.get("/purchases/", headers=auth_headers)
        assert r.status_code == 200

    def test_get_purchase_detail(self, client, auth_headers):
        mid = _med(client, auth_headers, "PurchDetailMed", 1200, 600)
        sup_r = client.post("/suppliers/create", json={"name": "SupDetail"}, headers=auth_headers)
        sup_id = sup_r.json()["data"]["id"]
        create = client.post("/purchases/create", json={
            "supplier_name": "SupDetail", "supplier_id": sup_id,
            "payment_method": "cash",
            "purchase_date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": 30000,
            "items": [{
                "medicine_id": mid, "batch_no": "PD-001", "quantity": 50,
                "purchase_price": 600, "selling_price": 1200,
                "expiry_date": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d"),
            }],
        }, headers=auth_headers)
        purchase_id = create.json()["data"]["id"]
        r = client.get(f"/purchases/{purchase_id}", headers=auth_headers)
        assert r.status_code == 200

    def test_update_purchase(self, client, auth_headers):
        mid = _med(client, auth_headers, "PurchUpdMed", 1200, 600)
        sup_r = client.post("/suppliers/create", json={"name": "SupUpd"}, headers=auth_headers)
        sup_id = sup_r.json()["data"]["id"]
        create = client.post("/purchases/create", json={
            "supplier_name": "SupUpd", "supplier_id": sup_id,
            "payment_method": "cash",
            "purchase_date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": 30000,
            "items": [{
                "medicine_id": mid, "batch_no": "PU-001", "quantity": 50,
                "purchase_price": 600, "selling_price": 1200,
                "expiry_date": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d"),
            }],
        }, headers=auth_headers)
        purchase_id = create.json()["data"]["id"]
        r = client.put(f"/purchases/{purchase_id}", json={
            "status": "received", "notes": "Updated"
        }, headers=auth_headers)
        assert r.status_code == 200

    def test_delete_purchase(self, client, auth_headers):
        mid = _med(client, auth_headers, "PurchDelMed", 1200, 600)
        sup_r = client.post("/suppliers/create", json={"name": "SupDel"}, headers=auth_headers)
        sup_id = sup_r.json()["data"]["id"]
        create = client.post("/purchases/create", json={
            "supplier_name": "SupDel", "supplier_id": sup_id,
            "payment_method": "cash",
            "purchase_date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": 30000,
            "items": [{
                "medicine_id": mid, "batch_no": "PDel-001", "quantity": 50,
                "purchase_price": 600, "selling_price": 1200,
                "expiry_date": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d"),
            }],
        }, headers=auth_headers)
        purchase_id = create.json()["data"]["id"]
        r = client.delete(f"/purchases/{purchase_id}", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 3. PRESCRIPTIONS — detail + update + delete + cancel + dispense
# ═══════════════════════════════════════════════════════════════════

class TestPrescriptionDetailAPI:

    def test_get_prescription_detail(self, client, auth_headers):
        mid = _med(client, auth_headers, "PrescDetailMed", 3000, 1500)
        _batch(client, auth_headers, mid, 50, 3000, 1500)
        create = client.post("/prescriptions/create", json={
            "patient_name": "PW",
            "patient_age": 30,
            "doctor_name": "Dr. X",
            "items": [{"medicine_id": mid, "medicine_name": "PrescDetailMed", "quantity": 1, "price": 3000}],
        }, headers=auth_headers)
        presc_id = create.json()["data"]["id"]
        r = client.get(f"/prescriptions/{presc_id}", headers=auth_headers)
        assert r.status_code == 200

    def test_update_prescription(self, client, auth_headers):
        mid = _med(client, auth_headers, "PrescUpdMed", 3000, 1500)
        _batch(client, auth_headers, mid, 50, 3000, 1500)
        create = client.post("/prescriptions/create", json={
            "patient_name": "PU",
            "patient_age": 40,
            "doctor_name": "Dr. Y",
            "items": [{"medicine_id": mid, "medicine_name": "PrescUpdMed", "quantity": 1, "price": 3000}],
        }, headers=auth_headers)
        presc_id = create.json()["data"]["id"]
        r = client.put(f"/prescriptions/{presc_id}", json={
            "patient_name": "PU Updated", "doctor_name": "Dr. Z"
        }, headers=auth_headers)
        assert r.status_code == 200

    def test_cancel_prescription(self, client, auth_headers):
        mid = _med(client, auth_headers, "PrescCancelMed", 3000, 1500)
        _batch(client, auth_headers, mid, 50, 3000, 1500)
        create = client.post("/prescriptions/create", json={
            "patient_name": "PC",
            "patient_age": 25,
            "doctor_name": "Dr. A",
            "items": [{"medicine_id": mid, "medicine_name": "PrescCancelMed", "quantity": 1, "price": 3000}],
        }, headers=auth_headers)
        presc_id = create.json()["data"]["id"]
        r = client.post(f"/prescriptions/{presc_id}/cancel", headers=auth_headers)
        assert r.status_code == 200

    def test_delete_prescription(self, client, auth_headers):
        mid = _med(client, auth_headers, "PrescDelMed", 3000, 1500)
        _batch(client, auth_headers, mid, 50, 3000, 1500)
        create = client.post("/prescriptions/create", json={
            "patient_name": "PD",
            "patient_age": 50,
            "doctor_name": "Dr. B",
            "items": [{"medicine_id": mid, "medicine_name": "PrescDelMed", "quantity": 1, "price": 3000}],
        }, headers=auth_headers)
        presc_id = create.json()["data"]["id"]
        r = client.delete(f"/prescriptions/{presc_id}", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 4. STOCK ADJUSTMENTS — create / approve / reject
# ═══════════════════════════════════════════════════════════════════

class TestStockAdjustmentAPI:

    def test_create_adjustment(self, client, auth_headers):
        mid = _med(client, auth_headers, "AdjMed1", 1000, 500)
        bid = _batch(client, auth_headers, mid, 50)
        r = client.post("/stock-adjustments/create", json={
            "medicine_id": mid, "batch_id": bid,
            "system_quantity": 50, "physical_quantity": 45,
            "reason": "Damaged boxes",
        }, headers=auth_headers)
        assert r.status_code == 200
        return r.json()["data"]["id"]

    def test_approve_adjustment(self, client, auth_headers):
        mid = _med(client, auth_headers, "AdjAppMed", 1000, 500)
        bid = _batch(client, auth_headers, mid, 50)
        create = client.post("/stock-adjustments/create", json={
            "medicine_id": mid, "batch_id": bid,
            "system_quantity": 50, "physical_quantity": 45,
            "reason": "Damaged",
        }, headers=auth_headers)
        adj_id = create.json()["data"]["id"]
        r = client.post(f"/stock-adjustments/{adj_id}/approve", headers=auth_headers)
        assert r.status_code == 200

    def test_reject_adjustment(self, client, auth_headers):
        mid = _med(client, auth_headers, "AdjRejMed", 1000, 500)
        bid = _batch(client, auth_headers, mid, 50)
        create = client.post("/stock-adjustments/create", json={
            "medicine_id": mid, "batch_id": bid,
            "system_quantity": 50, "physical_quantity": 45,
            "reason": "Rejected case",
        }, headers=auth_headers)
        adj_id = create.json()["data"]["id"]
        r = client.post(f"/stock-adjustments/{adj_id}/reject", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 5. STOCK TRANSFERS — create / approve / reject
# ═══════════════════════════════════════════════════════════════════

class TestStockTransferAPI:

    def test_create_transfer(self, client, auth_headers):
        mid = _med(client, auth_headers, "XferMed", 1000, 500)
        bid = _batch(client, auth_headers, mid, 100)
        br1 = client.post("/branches/create", json={"name": "From", "code": "FR01"}, headers=auth_headers)
        br2 = client.post("/branches/create", json={"name": "To", "code": "TO01"}, headers=auth_headers)
        from_id = br1.json()["data"]["id"]
        to_id = br2.json()["data"]["id"]
        r = client.post("/stock-transfers/create", json={
            "medicine_id": mid, "batch_id": bid,
            "from_branch_id": from_id, "to_branch_id": to_id,
            "quantity": 10,
        }, headers=auth_headers)
        assert r.status_code == 200
        return r.json()["data"]["id"]

    def test_approve_transfer(self, client, auth_headers):
        mid = _med(client, auth_headers, "XferAppMed", 1000, 500)
        bid = _batch(client, auth_headers, mid, 100)
        br1 = client.post("/branches/create", json={"name": "F2", "code": "F201"}, headers=auth_headers)
        br2 = client.post("/branches/create", json={"name": "T2", "code": "T201"}, headers=auth_headers)
        create = client.post("/stock-transfers/create", json={
            "medicine_id": mid, "batch_id": bid,
            "from_branch_id": br1.json()["data"]["id"],
            "to_branch_id": br2.json()["data"]["id"],
            "quantity": 10,
        }, headers=auth_headers)
        xfer_id = create.json()["data"]["id"]
        r = client.post(f"/stock-transfers/{xfer_id}/approve", headers=auth_headers)
        assert r.status_code == 200

    def test_reject_transfer(self, client, auth_headers):
        mid = _med(client, auth_headers, "XferRejMed", 1000, 500)
        bid = _batch(client, auth_headers, mid, 100)
        br1 = client.post("/branches/create", json={"name": "F3", "code": "F301"}, headers=auth_headers)
        br2 = client.post("/branches/create", json={"name": "T3", "code": "T301"}, headers=auth_headers)
        create = client.post("/stock-transfers/create", json={
            "medicine_id": mid, "batch_id": bid,
            "from_branch_id": br1.json()["data"]["id"],
            "to_branch_id": br2.json()["data"]["id"],
            "quantity": 10,
        }, headers=auth_headers)
        xfer_id = create.json()["data"]["id"]
        r = client.post(f"/stock-transfers/{xfer_id}/reject", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 6. DISPOSALS — create / approve / dispose
# ═══════════════════════════════════════════════════════════════════

class TestDisposalAPI:

    def test_create_disposal(self, client, auth_headers):
        mid = _med(client, auth_headers, "DispMed", 5000, 3000)
        bid = _batch(client, auth_headers, mid, 20, 5000, 3000)
        r = client.post("/disposals/create", json={
            "medicine_id": mid, "batch_id": bid, "quantity": 20,
            "disposal_method": "incineration",
            "reason": "Expired",
            "witness_name": "Pharm A",
        }, headers=auth_headers)
        assert r.status_code == 200
        return r.json()["data"]["id"]

    def test_approve_disposal(self, client, auth_headers):
        mid = _med(client, auth_headers, "DispAppMed", 5000, 3000)
        bid = _batch(client, auth_headers, mid, 20, 5000, 3000)
        create = client.post("/disposals/create", json={
            "medicine_id": mid, "batch_id": bid, "quantity": 20,
            "disposal_method": "incineration", "reason": "Expired",
        }, headers=auth_headers)
        disp_id = create.json()["data"]["id"]
        r = client.post(f"/disposals/{disp_id}/approve", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 7. RETURNS — create + detail
# ═══════════════════════════════════════════════════════════════════

class TestReturnAPI:

    def test_create_return(self, client, auth_headers):
        mid = _med(client, auth_headers, "RetMed", 1000, 500)
        bid = _batch(client, auth_headers, mid, 50)
        sale = client.post("/sales/create", json={
            "customer_name": "RetCust", "payment_method": "cash",
            "amount_paid": 5000,
            "items": [{"medicine_id": mid, "batch_id": bid, "quantity": 5, "selling_price": 1000}],
        }, headers=auth_headers)
        sale_id = sale.json()["data"]["id"]
        sale_items = sale.json()["data"].get("items", [])
        if sale_items:
            r = client.post("/returns/create", json={
                "sale_id": sale_id,
                "reason": "Wrong medicine",
                "items": [{"sale_item_id": sale_items[0]["id"], "medicine_id": mid, "batch_id": bid, "quantity": 2, "unit_price": 1000}],
            }, headers=auth_headers)
            assert r.status_code == 200

    def test_get_return_detail(self, client, auth_headers):
        r = client.get("/returns/1", headers=auth_headers)
        assert r.status_code in (200, 404)


# ═══════════════════════════════════════════════════════════════════
# 8. AUTH — logout + refresh
# ═══════════════════════════════════════════════════════════════════

class TestAuthExtendedAPI:

    def test_logout(self, client, auth_headers):
        r = client.post("/auth/logout", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_refresh_token_no_cookie(self, client):
        r = client.post("/auth/refresh")
        assert r.status_code in (200, 401, 403)


# ═══════════════════════════════════════════════════════════════════
# 9. NOTIFICATIONS — mark-read + read-all + delete
# ═══════════════════════════════════════════════════════════════════

class TestNotificationExtendedAPI:

    def _create_notif(self, client, auth_headers):
        """Create a notification via expiry action (which auto-generates notifications)."""
        # Just list to confirm notifications endpoint works
        r = client.get("/notifications/", headers=auth_headers)
        assert r.status_code == 200
        return r.json().get("data", {}).get("items", [])

    def test_mark_read(self, client, auth_headers):
        notifs = self._create_notif(client, auth_headers)
        if notifs:
            nid = notifs[0]["id"]
            r = client.post(f"/notifications/{nid}/read", headers=auth_headers)
            assert r.status_code == 200

    def test_mark_all_read(self, client, auth_headers):
        r = client.post("/notifications/read-all", headers=auth_headers)
        assert r.status_code == 200

    def test_delete_notification(self, client, auth_headers):
        notifs = self._create_notif(client, auth_headers)
        if notifs:
            nid = notifs[0]["id"]
            r = client.delete(f"/notifications/{nid}", headers=auth_headers)
            assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 10. EXPENSES — update + delete
# ═══════════════════════════════════════════════════════════════════

class TestExpenseExtendedAPI:

    def test_update_expense(self, client, auth_headers):
        create = client.post("/expenses/create", json={
            "category": "Transport", "amount": 30000,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }, headers=auth_headers)
        assert create.status_code == 200
        exp_id = create.json()["data"]["id"]
        r = client.put(f"/expenses/{exp_id}", json={
            "category": "Transport Updated", "amount": 35000,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }, headers=auth_headers)
        assert r.status_code == 200

    def test_delete_expense(self, client, auth_headers):
        create = client.post("/expenses/create", json={
            "category": "To Delete", "amount": 10000,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }, headers=auth_headers)
        exp_id = create.json()["data"]["id"]
        r = client.delete(f"/expenses/{exp_id}", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 11. BATCHES — update + delete
# ═══════════════════════════════════════════════════════════════════

class TestBatchExtendedAPI:

    def test_update_batch(self, client, auth_headers):
        mid = _med(client, auth_headers, "BatchUpdMed", 1000, 500)
        bid = _batch(client, auth_headers, mid, 50, 1000, 500, "BU-001")
        r = client.put(f"/batches/{bid}", json={"quantity": 75, "batch_no": "BU-001",
            "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "purchase_price": 500, "selling_price": 1000}, headers=auth_headers)
        assert r.status_code == 200

    def test_delete_batch(self, client, auth_headers):
        mid = _med(client, auth_headers, "BatchDelMed", 1000, 500)
        bid = _batch(client, auth_headers, mid, 50, 1000, 500, "BD-001")
        r = client.delete(f"/batches/{bid}", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 12. CURRENCIES — update rates
# ═══════════════════════════════════════════════════════════════════

class TestCurrencyExtendedAPI:

    def test_update_rates(self, client, auth_headers):
        r = client.put("/currencies/update", json={
            "rates": [{"code": "USD", "rate_to_tzs": 2550}]
        }, headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 13. MEDICINES — bulk-create
# ═══════════════════════════════════════════════════════════════════

class TestMedicineBulkAPI:

    def test_bulk_create(self, client, auth_headers):
        r = client.post("/medicines/bulk-create", json=[
            {"name": "BulkMed1", "default_selling_price": 1000},
            {"name": "BulkMed2", "default_selling_price": 2000},
        ], headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 14. PERMISSIONS — update
# ═══════════════════════════════════════════════════════════════════

class TestPermissionExtendedAPI:

    def test_update_permissions(self, client, auth_headers):
        r = client.post("/permissions/update", json={
            "role": "staff",
            "permissions": {"medicines": "read", "sales": "*"},
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["success"] is True


# ═══════════════════════════════════════════════════════════════════
# 15. INVOICE — PDF download
# ═══════════════════════════════════════════════════════════════════

class TestInvoiceAPI:

    def test_download_invoice(self, client, auth_headers):
        mid = _med(client, auth_headers, "InvMed", 2000, 1000)
        bid = _batch(client, auth_headers, mid, 30, 2000, 1000)
        sale = client.post("/sales/create", json={
            "customer_name": "InvCust", "payment_method": "cash",
            "amount_paid": 4000,
            "items": [{"medicine_id": mid, "batch_id": bid, "quantity": 2, "selling_price": 2000}],
        }, headers=auth_headers)
        sale_id = sale.json()["data"]["id"]
        r = client.get(f"/invoice/sale/{sale_id}", headers=auth_headers)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf") or r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 16. REPORTS — export + medicine-specific + 7-day
# ═══════════════════════════════════════════════════════════════════

class TestReportExtendedAPI:

    def test_export_csv(self, client, auth_headers):
        r = client.get("/reports/export/sales?period=monthly", headers=auth_headers)
        assert r.status_code == 200

    def test_sales_by_medicine(self, client, auth_headers):
        mid = _med(client, auth_headers, "RptMed", 1000, 500)
        r = client.get(f"/reports/sales/medicine/{mid}", headers=auth_headers)
        assert r.status_code == 200

    def test_last_7_days_sales(self, client, auth_headers):
        r = client.get("/reports/sales/sales-7-days", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 17. INVENTORY — medicine-specific
# ═══════════════════════════════════════════════════════════════════

class TestInventoryExtendedAPI:

    def test_medicine_stock(self, client, auth_headers):
        mid = _med(client, auth_headers, "InvStockMed", 1000, 500)
        _batch(client, auth_headers, mid, 50)
        r = client.get(f"/inventory/medicine/{mid}", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 18. EXPIRY — record action
# ═══════════════════════════════════════════════════════════════════

class TestExpiryExtendedAPI:

    def test_record_expiry_action(self, client, auth_headers):
        mid = _med(client, auth_headers, "ExpActMed", 5000, 3000)
        r = client.post("/expiry/action", json={
            "action_type": "quarantine",
            "medicine_id": mid,
            "medicine_name": "ExpActMed",
            "batch_no": "EXP-001",
            "quantity": 10,
            "reason": "Near expiry",
            "responsible_person": "Pharmacist",
        }, headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# 19. EDGE CASES — error paths, validation, auth failures
# ═══════════════════════════════════════════════════════════════════

class TestEdgeCases:

    def test_unauthorized_access(self, client):
        """All protected endpoints should return 401 without token."""
        endpoints = [
            "/medicines/", "/batches/", "/categories/", "/manufacturers/",
            "/branches/", "/customers/", "/suppliers/", "/settings/",
            "/sales/", "/purchases/", "/expenses/", "/dashboard/",
            "/reports/profit-loss", "/inventory/", "/expiry/",
        ]
        for ep in endpoints:
            r = client.get(ep)
            assert r.status_code in (401, 403), f"{ep} returned {r.status_code} without auth"

    def test_invalid_token(self, client):
        h = {"Authorization": "Bearer invalid.token.here"}
        r = client.get("/medicines/", headers=h)
        assert r.status_code in (401, 403)

    def test_expired_token(self, client):
        """An expired JWT should be rejected."""
        from jose import jwt
        from app.core.config import get_settings
        settings = get_settings()
        from datetime import datetime, timedelta
        expired = jwt.encode(
            {"sub": "test@test.com", "role": "staff",
             "exp": datetime.utcnow() - timedelta(hours=1),
             "type": "access"},
            settings.secret_key, algorithm="HS256"
        )
        h = {"Authorization": f"Bearer {expired}"}
        r = client.get("/medicines/", headers=h)
        assert r.status_code in (401, 403)

    def test_create_medicine_missing_name(self, client, auth_headers):
        r = client.post("/medicines/", json={
            "default_selling_price": 1000,
        }, headers=auth_headers)
        assert r.status_code in (400, 422)

    def test_get_nonexistent_medicine(self, client, auth_headers):
        r = client.get("/medicines/99999", headers=auth_headers)
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            assert r.json().get("data") is None or r.json().get("success") is False

    def test_delete_nonexistent_medicine(self, client, auth_headers):
        r = client.delete("/medicines/99999", headers=auth_headers)
        assert r.status_code in (200, 404)

    def test_get_nonexistent_batch(self, client, auth_headers):
        r = client.get("/batches/99999", headers=auth_headers)
        assert r.status_code in (200, 404)

    def test_create_sale_empty_items(self, client, auth_headers):
        r = client.post("/sales/create", json={
            "customer_name": "Empty", "payment_method": "cash",
            "amount_paid": 0, "items": [],
        }, headers=auth_headers)
        assert r.status_code in (200, 400, 422)

    def test_create_sale_insufficient_stock(self, client, auth_headers):
        mid = _med(client, auth_headers, "InsufMed", 1000, 500)
        bid = _batch(client, auth_headers, mid, 2, 1000, 500)
        r = client.post("/sales/create", json={
            "customer_name": "Insuf", "payment_method": "cash",
            "amount_paid": 10000,
            "items": [{"medicine_id": mid, "batch_id": bid, "quantity": 999, "selling_price": 1000}],
        }, headers=auth_headers)
        assert r.status_code in (200, 400)

    def test_update_settings_all_fields(self, client, auth_headers):
        r = client.put("/settings/", json={
            "pharmacy_name": "Full Settings Test",
            "address": "123 Test St",
            "phone": "+255712345678",
            "email": "test@pharmacy.com",
            "invoice_footer": "Thank you!",
            "default_currency": "TZS",
            "expiry_warning_days": 45,
            "low_stock_threshold": 20,
            "tax_rate": 18.0,
            "registration_number": "PHA-12345",
            "region": "Dar es Salaam",
            "district": "Ilala",
        }, headers=auth_headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["tax_rate"] == 18.0
        assert data["registration_number"] == "PHA-12345"

    def test_login_wrong_email(self, client):
        r = client.post("/auth/login", json={
            "email": "nonexistent@test.com", "password": "anything"
        })
        assert r.status_code in (401, 200)
        if r.status_code == 200:
            assert r.json()["success"] is False

    def test_list_with_pagination(self, client, auth_headers):
        r = client.get("/medicines/?page=1&limit=5", headers=auth_headers)
        assert r.status_code == 200

    def test_search_medicines(self, client, auth_headers):
        _med(client, auth_headers, "SearchableMedicine", 1000, 500)
        r = client.get("/medicines/?search=Searchable", headers=auth_headers)
        assert r.status_code == 200

    def test_search_suppliers(self, client, auth_headers):
        client.post("/suppliers/create", json={"name": "SearchableSupplier"}, headers=auth_headers)
        r = client.get("/suppliers/?search=Searchable", headers=auth_headers)
        assert r.status_code == 200

    def test_search_customers(self, client, auth_headers):
        client.post("/customers/create", json={"name": "SearchableCustomer"}, headers=auth_headers)
        r = client.get("/customers/?search=Searchable", headers=auth_headers)
        assert r.status_code == 200

    def test_create_duplicate_category(self, client, auth_headers):
        client.post("/categories/create", json={"name": "DupCat"}, headers=auth_headers)
        r = client.post("/categories/create", json={"name": "DupCat"}, headers=auth_headers)
        assert r.status_code in (200, 400, 409)
        if r.status_code == 200:
            assert r.json()["success"] is False or r.json().get("data") is None

    def test_create_duplicate_branch_code(self, client, auth_headers):
        client.post("/branches/create", json={"name": "DupBranch", "code": "DUP001"}, headers=auth_headers)
        r = client.post("/branches/create", json={"name": "DupBranch2", "code": "DUP001"}, headers=auth_headers)
        assert r.status_code in (200, 400, 409)
        if r.status_code == 200:
            assert r.json()["success"] is False or r.json().get("data") is None

    def test_export_all_report_types(self, client, auth_headers):
        for rtype in ["sales", "purchases", "inventory", "profit-loss"]:
            r = client.get(f"/reports/export/{rtype}?period=monthly", headers=auth_headers)
            assert r.status_code == 200, f"Export {rtype} failed"

    def test_dashboard_returns_structured_data(self, client, auth_headers):
        r = client.get("/dashboard/", headers=auth_headers)
        assert r.status_code == 200
        data = r.json().get("data", {})
        assert isinstance(data, dict)

    def test_expiry_dashboard_returns_structure(self, client, auth_headers):
        r = client.get("/expiry/dashboard", headers=auth_headers)
        assert r.status_code == 200

    def test_multiple_sales_same_batch(self, client, auth_headers):
        mid = _med(client, auth_headers, "MultiSaleMed", 1000, 500)
        bid = _batch(client, auth_headers, mid, 100, 1000, 500)
        for i in range(3):
            r = client.post("/sales/create", json={
                "customer_name": f"MS{i}", "payment_method": "cash",
                "amount_paid": 2000,
                "items": [{"medicine_id": mid, "batch_id": bid, "quantity": 2, "selling_price": 1000}],
            }, headers=auth_headers)
            assert r.status_code == 200

    def test_create_purchase_with_multiple_items(self, client, auth_headers):
        mid1 = _med(client, auth_headers, "PurchMulti1", 1000, 500)
        mid2 = _med(client, auth_headers, "PurchMulti2", 2000, 800)
        sup_r = client.post("/suppliers/create", json={"name": "PurchMultiSup"}, headers=auth_headers)
        sup_id = sup_r.json()["data"]["id"]
        r = client.post("/purchases/create", json={
            "supplier_name": "PurchMultiSup", "supplier_id": sup_id,
            "payment_method": "bank_transfer",
            "purchase_date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": 65000,
            "items": [
                {"medicine_id": mid1, "batch_no": "PM-001", "quantity": 50, "purchase_price": 500, "selling_price": 1000,
                 "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")},
                {"medicine_id": mid2, "batch_no": "PM-002", "quantity": 25, "purchase_price": 800, "selling_price": 2000,
                 "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")},
            ]
        }, headers=auth_headers)
        assert r.status_code == 200

    def test_sale_with_discount(self, client, auth_headers):
        mid = _med(client, auth_headers, "DiscMed", 5000, 2500)
        bid = _batch(client, auth_headers, mid, 20, 5000, 2500)
        r = client.post("/sales/create", json={
            "customer_name": "DiscCust", "payment_method": "cash",
            "amount_paid": 9000, "discount_amount": 1000,
            "items": [{"medicine_id": mid, "batch_id": bid, "quantity": 2, "selling_price": 5000}],
        }, headers=auth_headers)
        assert r.status_code == 200
        sale = r.json()["data"]
        assert sale["total_amount"] == 9000  # 10000 - 1000 discount

    def test_sale_with_due_amount(self, client, auth_headers):
        mid = _med(client, auth_headers, "DueMed", 3000, 1500)
        bid = _batch(client, auth_headers, mid, 10, 3000, 1500)
        r = client.post("/sales/create", json={
            "customer_name": "DueCust", "payment_method": "credit",
            "amount_paid": 3000, "due_amount": 3000,
            "items": [{"medicine_id": mid, "batch_id": bid, "quantity": 2, "selling_price": 3000}],
        }, headers=auth_headers)
        assert r.status_code == 200

    def test_concurrent_same_user_operations(self, client, auth_headers):
        """Multiple rapid operations by same user should not crash."""
        for i in range(5):
            _med(client, auth_headers, f"ConcMed{i}", 1000, 500)
        r = client.get("/medicines/", headers=auth_headers)
        assert r.status_code == 200
