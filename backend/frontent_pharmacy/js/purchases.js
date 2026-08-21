// ============================================
// PURCHASES MODULE
// ============================================

async function renderPurchases() {
    const content = document.getElementById('pageContent');
    try {
        const purchases = await api.getPurchases();
        
        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openPurchaseModal()">
                    <i class="fas fa-plus"></i> New Purchase
                </button>
                <span class="text-muted">Total: ${purchases.length} purchases</span>
            </div>
            <div class="table-container">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Invoice #</th>
                            <th>Date</th>
                            <th>Supplier</th>
                            <th>Items</th>
                            <th>Total</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${purchases.map(purchase => `
                            <tr>
                                <td><strong>${purchase.invoice_number}</strong></td>
                                <td>${new Date(purchase.purchase_date).toLocaleDateString()}</td>
                                <td>${purchase.supplier_name || 'Unknown'}</td>
                                <td>${purchase.items?.length || 0}</td>
                                <td><strong>${formatMoney(purchase.total_amount || 0)}</strong></td>
                                <td>
                                    <button class="btn btn-sm btn-outline-info" onclick="viewPurchase(${purchase.id})">View</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load purchases: ${error.message}</div>`;
    }
}

function openPurchaseModal() {
    document.getElementById('purchase_supplier').value = '';
    document.getElementById('purchase_date').value = new Date().toISOString().split('T')[0];
    document.getElementById('purchase_currency').value = (window.APP_CONFIG?.defaultCurrency) || 'TZS';
    updatePurchaseCurrencyHint();
    document.getElementById('purchaseItems').innerHTML = getPurchaseItemRow();
    
    const modal = new bootstrap.Modal(document.getElementById('createPurchaseModal'));
    modal.show();
}

function updatePurchaseCurrencyHint() {
    const code = document.getElementById('purchase_currency').value;
    const rates = (window.APP_CONFIG && window.APP_CONFIG.currencyRates) || {};
    const rate = rates[code];
    const hint = document.getElementById('purchaseCurrencyHint');
    if (!hint) return;
    if (!code || code === 'TZS') {
        hint.innerHTML = '<i class="fas fa-exchange-alt me-1"></i>Bei zitahesabiwa kwa TZS moja kwa moja';
    } else if (rate) {
        hint.innerHTML = `<i class="fas fa-exchange-alt me-1"></i>Bei zitabadilishwa kuwa TZS (1 ${code} ≈ ${formatMoney(rate)})`;
    } else {
        hint.innerHTML = '<i class="fas fa-exchange-alt me-1"></i>Bei zitabadilishwa kuwa TZS';
    }
}

function getPurchaseItemRow() {
    return `
        <div class="purchase-item-row row mb-2">
            <div class="col-md-2">
                <input type="number" class="form-control" placeholder="Med ID" name="purchase_medicine_id">
            </div>
            <div class="col-md-2">
                <input type="text" class="form-control" placeholder="Batch No" name="purchase_batch">
            </div>
            <div class="col-md-2">
                <input type="date" class="form-control" name="purchase_expiry">
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control" placeholder="Qty" name="purchase_qty">
            </div>
            <div class="col-md-2">
                <input type="number" step="0.01" min="0" class="form-control" placeholder="Buy Price" name="purchase_buy_price">
            </div>
            <div class="col-md-2">
                <input type="number" step="0.01" min="0" class="form-control" placeholder="Sell Price" name="purchase_sell_price">
            </div>
            <div class="col-md-12 mt-1">
                <button type="button" class="btn btn-danger btn-sm" onclick="removePurchaseItem(this)">
                    <i class="fas fa-times"></i> Remove
                </button>
            </div>
        </div>
    `;
}

function addPurchaseItemRow() {
    const container = document.getElementById('purchaseItems');
    const row = document.createElement('div');
    row.className = 'purchase-item-row row mb-2';
    row.innerHTML = getPurchaseItemRow();
    container.appendChild(row);
}

function removePurchaseItem(btn) {
    const row = btn.closest('.purchase-item-row');
    if (document.querySelectorAll('.purchase-item-row').length > 1) {
        row.remove();
    } else {
        alert('At least one item is required!');
    }
}

async function createPurchase() {
    const rows = document.querySelectorAll('.purchase-item-row');
    const items = [];
    let valid = true;
    
    rows.forEach(row => {
        const inputs = row.querySelectorAll('input');
        const medicineId = inputs[0].value;
        const batch = inputs[1].value;
        const expiry = inputs[2].value;
        const qty = inputs[3].value;
        const buyPrice = inputs[4].value;
        const sellPrice = inputs[5].value;
        
        if (medicineId && batch && expiry && qty && buyPrice && sellPrice) {
            items.push({
                medicine_id: parseInt(medicineId),
                batch_no: batch,
                expiry_date: expiry,
                purchase_price: parseFloat(buyPrice) || 0,
                selling_price: parseFloat(sellPrice) || 0,
                quantity: parseInt(qty)
            });
        } else {
            valid = false;
        }
    });
    
    if (!valid) {
        alert('Please fill all fields in each item row!');
        return;
    }
    
    if (items.length === 0) {
        alert('Please add at least one valid item!');
        return;
    }
    
    const data = {
        supplier_name: document.getElementById('purchase_supplier').value || 'Unknown Supplier',
        purchase_date: document.getElementById('purchase_date').value || new Date().toISOString().split('T')[0],
        currency_code: document.getElementById('purchase_currency').value || 'TZS',
        items: items
    };
    
    try {
        await api.createPurchase(data);
        bootstrap.Modal.getInstance(document.getElementById('createPurchaseModal')).hide();
        alert('Purchase created successfully!');
        navigateTo('purchases');
    } catch (error) {
        alert('Failed to create purchase: ' + error.message);
    }
}

async function viewPurchase(id) {
    try {
        const purchase = await api.getPurchase(id);
        alert(`Purchase #${purchase.invoice_number}\nSupplier: ${purchase.supplier_name}\nTotal: ${formatMoney(purchase.total_amount)}\nItems: ${purchase.items?.length || 0}`);
    } catch (error) {
        alert('Failed to load purchase: ' + error.message);
    }
}

console.log('Purchases module loaded');
