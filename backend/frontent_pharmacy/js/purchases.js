// ============================================
// PURCHASES MODULE — Medicine Name Search + Supplier Search
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
    document.getElementById('purchase_supplier_id').value = '';
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
        hint.innerHTML = '<i class="fas fa-exchange-alt me-1"></i>Prices in TZS directly';
    } else if (rate) {
        hint.innerHTML = `<i class="fas fa-exchange-alt me-1"></i>1 ${code} ≈ ${formatMoney(rate)}`;
    } else {
        hint.innerHTML = '<i class="fas fa-exchange-alt me-1"></i>Converted to TZS';
    }
}

// ============================================
// SUPPLIER SEARCH for Purchase Modal
// ============================================
let supplierSearchTimeout = null;

async function searchSuppliersForPurchase(query) {
    const resultsDiv = document.getElementById('supplierSearchResults');
    if (!resultsDiv) return;
    
    if (!query || query.length < 2) {
        resultsDiv.style.display = 'none';
        resultsDiv.innerHTML = '';
        document.getElementById('purchase_supplier_id').value = '';
        return;
    }

    clearTimeout(supplierSearchTimeout);
    supplierSearchTimeout = setTimeout(async () => {
        try {
            const suppliers = await api.getSuppliers(50, query);
            let html = '<div class="list-group" style="max-height:200px;overflow-y:auto;">';
            
            if (suppliers && suppliers.length > 0) {
                html += suppliers.map(s => `
                    <button type="button" class="list-group-item list-group-item-action" onclick="selectSupplierForPurchase(${s.id}, '${(s.company_name || '').replace(/'/g, "\\'")}')">
                        <strong>${s.company_name || 'Unknown'}</strong>
                        <small class="text-muted ms-2">${s.contact_person || ''}</small>
                    </button>
                `).join('');
            }
            
            html += `<button type="button" class="list-group-item list-group-item-action text-primary" onclick="createNewSupplierFromPurchase('${query.replace(/'/g, "\\'")}')">
                <i class="fas fa-plus me-1"></i> Create new supplier: "${query}"
            </button>`;
            html += '</div>';
            
            resultsDiv.innerHTML = html;
            resultsDiv.style.display = 'block';
        } catch (e) {
            resultsDiv.style.display = 'none';
        }
    }, 300);
}

function selectSupplierForPurchase(id, name) {
    document.getElementById('purchase_supplier').value = name;
    document.getElementById('purchase_supplier_id').value = id;
    document.getElementById('supplierSearchResults').style.display = 'none';
}

async function createNewSupplierFromPurchase(name) {
    try {
        const result = await api.createSupplier({ company_name: name });
        const newId = result?.id || result?.data?.id;
        if (newId) {
            selectSupplierForPurchase(newId, name);
        } else {
            document.getElementById('purchase_supplier').value = name;
            document.getElementById('supplierSearchResults').style.display = 'none';
        }
    } catch (e) {
        document.getElementById('purchase_supplier').value = name;
        document.getElementById('supplierSearchResults').style.display = 'none';
    }
}

// Close supplier dropdown when clicking outside
document.addEventListener('click', function(e) {
    const sr = document.getElementById('supplierSearchResults');
    const input = document.getElementById('purchase_supplier');
    if (sr && input && !sr.contains(e.target) && e.target !== input) {
        sr.style.display = 'none';
    }
});

// ============================================
// MEDICINE SEARCH for Purchase Items
// ============================================
let medSearchTimeouts = {};

function searchMedicineForPurchase(inputEl) {
    const row = inputEl.closest('.purchase-item-row');
    const resultsDiv = row.querySelector('.purchase-med-results');
    const query = inputEl.value.trim();
    
    if (!query || query.length < 2) {
        resultsDiv.style.display = 'none';
        resultsDiv.innerHTML = '';
        row.querySelector('.purchase-medicine-id').value = '';
        row.querySelector('.purchase-medicine-name').textContent = '';
        return;
    }

    const uid = Math.random().toString(36).substr(2, 9);
    clearTimeout(medSearchTimeouts[uid]);
    medSearchTimeouts[uid] = setTimeout(async () => {
        try {
            const medicines = await api.searchMedicines(query, 10);
            
            let html = '<div class="list-group">';
            if (medicines && medicines.length > 0) {
                html += medicines.map(m => `
                    <button type="button" class="list-group-item list-group-item-action" 
                        onclick="selectMedicineForPurchase(this, ${m.id}, '${(m.name || '').replace(/'/g, "\\'")}', ${m.default_selling_price || 0})">
                        <strong>${m.name}</strong>
                        <small class="text-muted ms-2">${m.category || ''} ${m.strength || ''}</small>
                        <span class="badge bg-secondary float-end">${formatMoney(m.default_selling_price || 0)}</span>
                    </button>
                `).join('');
            } else {
                html += '<div class="list-group-item text-muted">No medicines found</div>';
            }
            html += '</div>';
            
            resultsDiv.innerHTML = html;
            resultsDiv.style.display = 'block';
        } catch (e) {
            resultsDiv.style.display = 'none';
        }
    }, 300);
}

function selectMedicineForPurchase(btn, id, name, defaultPrice) {
    const row = btn.closest('.purchase-item-row');
    row.querySelector('.purchase-medicine-id').value = id;
    row.querySelector('.purchase-medicine-search').value = name;
    row.querySelector('.purchase-medicine-name').textContent = `ID: ${id}`;
    
    if (defaultPrice > 0) {
        const sellInput = row.querySelector('[name="purchase_sell_price"]');
        if (sellInput && !sellInput.value) sellInput.value = defaultPrice;
    }
    
    row.querySelector('.purchase-med-results').style.display = 'none';
}

// Close medicine dropdowns when clicking outside
document.addEventListener('click', function(e) {
    document.querySelectorAll('.purchase-med-results').forEach(div => {
        const row = div.closest('.purchase-item-row');
        const input = row?.querySelector('.purchase-medicine-search');
        if (!div.contains(e.target) && e.target !== input) {
            div.style.display = 'none';
        }
    });
});

// ============================================
// PURCHASE ITEM ROWS
// ============================================

function getPurchaseItemRow() {
    return `
        <div class="purchase-item-row row mb-2">
            <div class="col-md-3" style="position:relative;">
                <label class="form-label small required">Medicine Name</label>
                <input type="text" class="form-control purchase-medicine-search" placeholder="Search medicine..." autocomplete="off" oninput="searchMedicineForPurchase(this)">
                <div class="purchase-med-results" style="display:none;position:absolute;top:100%;left:0;right:0;z-index:9999;background:var(--bg-card,#fff);border:1px solid var(--border-color,#ddd);border-radius:6px;max-height:220px;overflow-y:auto;box-shadow:0 6px 20px rgba(0,0,0,0.2);"></div>
                <input type="hidden" class="purchase-medicine-id" name="purchase_medicine_id">
                <small class="text-muted purchase-medicine-name"></small>
            </div>
            <div class="col-md-2">
                <label class="form-label small required">Batch No</label>
                <input type="text" class="form-control" placeholder="Batch No" name="purchase_batch">
            </div>
            <div class="col-md-2">
                <label class="form-label small required">Expiry Date</label>
                <input type="date" class="form-control" name="purchase_expiry">
            </div>
            <div class="col-md-1">
                <label class="form-label small required">Qty</label>
                <input type="number" class="form-control" placeholder="Qty" name="purchase_qty" min="1" value="1">
            </div>
            <div class="col-md-2">
                <label class="form-label small required">Buy Price</label>
                <input type="text" class="form-control" placeholder="TSh" name="purchase_buy_price" oninput="this.value=this.value.replace(/[^0-9]/g,'')">
                <small class="text-muted">e.g. 200000</small>
            </div>
            <div class="col-md-2">
                <label class="form-label small required">Sell Price</label>
                <input type="text" class="form-control" placeholder="TSh" name="purchase_sell_price" oninput="this.value=this.value.replace(/[^0-9]/g,'')">
                <small class="text-muted">e.g. 350000</small>
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
        SwalAlert.warning(t('At least one item is required'));
    }
}

// ============================================
// CREATE PURCHASE
// ============================================

async function createPurchase() {
    const rows = document.querySelectorAll('.purchase-item-row');
    const items = [];
    let valid = true;
    
    rows.forEach(row => {
        const medIdInput = row.querySelector('.purchase-medicine-id');
        const batch = row.querySelector('[name="purchase_batch"]')?.value;
        const expiry = row.querySelector('[name="purchase_expiry"]')?.value;
        const qty = row.querySelector('[name="purchase_qty"]')?.value;
        const buyPrice = row.querySelector('[name="purchase_buy_price"]')?.value;
        const sellPrice = row.querySelector('[name="purchase_sell_price"]')?.value;
        const medicineId = medIdInput?.value;
        
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
        SwalAlert.warning(t('Please fill all required fields in each item row'));
        return;
    }
    
    if (items.length === 0) {
        SwalAlert.warning(t('Please add at least one valid item'));
        return;
    }
    
    const supplierName = document.getElementById('purchase_supplier').value.trim();
    if (!supplierName) {
        SwalAlert.warning(t('Please enter a supplier name'));
        return;
    }
    
    const data = {
        supplier_name: supplierName,
        purchase_date: document.getElementById('purchase_date').value || new Date().toISOString().split('T')[0],
        currency_code: document.getElementById('purchase_currency').value || 'TZS',
        items: items
    };
    
    try {
        await api.createPurchase(data);
        bootstrap.Modal.getInstance(document.getElementById('createPurchaseModal')).hide();
        SwalAlert.success(t('Purchase created successfully'));
        navigateTo('purchases');
    } catch (error) {
        SwalAlert.error(t('Failed to create purchase') + ': ' + error.message);
    }
}

async function viewPurchase(id) {
    try {
        const purchase = await api.getPurchase(id);
        SwalAlert.success(`Purchase #${purchase.invoice_number}\nSupplier: ${purchase.supplier_name}\nTotal: ${formatMoney(purchase.total_amount)}\nItems: ${purchase.items?.length || 0}`);
    } catch (error) {
        SwalAlert.error(t('Failed to load purchase') + ': ' + error.message);
    }
}

console.log('Purchases module loaded');
