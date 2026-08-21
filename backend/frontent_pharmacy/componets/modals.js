// ============================================
// MODAL MANAGEMENT - Centralized Modal Controls
// ============================================

// ============ MEDICINE MODALS ============

function openAddMedicineModal() {
    document.getElementById('addMedicineForm').reset();
    const modal = new bootstrap.Modal(document.getElementById('addMedicineModal'));
    modal.show();
}

async function saveMedicine() {
    const data = {
        name: document.getElementById('med_name').value,
        generic_name: document.getElementById('med_generic').value,
        brand: document.getElementById('med_brand').value,
        category: document.getElementById('med_category').value,
        unit: document.getElementById('med_unit').value,
        strength: document.getElementById('med_strength').value,
        barcode: document.getElementById('med_barcode').value
    };
    
    if (!data.name) {
        showToast('Medicine name is required!', 'warning');
        return;
    }
    
    try {
        await api.createMedicine(data);
        bootstrap.Modal.getInstance(document.getElementById('addMedicineModal')).hide();
        showToast('Medicine added successfully!', 'success');
        navigateTo('medicines');
    } catch (error) {
        showToast('Failed to add medicine: ' + error.message, 'danger');
    }
}

function editMedicine(id) {
    // Find medicine from the loaded data
    const medicine = medicinesData?.find(m => m.id === id);
    if (!medicine) {
        showToast('Medicine not found!', 'warning');
        return;
    }
    
    // Populate form with medicine data
    document.getElementById('med_name').value = medicine.name || '';
    document.getElementById('med_generic').value = medicine.generic_name || '';
    document.getElementById('med_brand').value = medicine.brand || '';
    document.getElementById('med_category').value = medicine.category || 'Tablet';
    document.getElementById('med_unit').value = medicine.unit || 'Strip';
    document.getElementById('med_strength').value = medicine.strength || '';
    document.getElementById('med_barcode').value = medicine.barcode || '';
    
    // Change button to update
    const saveBtn = document.querySelector('#addMedicineModal .modal-footer .btn-primary');
    saveBtn.innerHTML = '<i class="fas fa-save"></i> Update Medicine';
    saveBtn.onclick = function() {
        updateMedicine(id);
    };
    
    const modal = new bootstrap.Modal(document.getElementById('addMedicineModal'));
    modal.show();
}

async function updateMedicine(id) {
    const data = {
        name: document.getElementById('med_name').value,
        generic_name: document.getElementById('med_generic').value,
        brand: document.getElementById('med_brand').value,
        category: document.getElementById('med_category').value,
        unit: document.getElementById('med_unit').value,
        strength: document.getElementById('med_strength').value,
        barcode: document.getElementById('med_barcode').value
    };
    
    if (!data.name) {
        showToast('Medicine name is required!', 'warning');
        return;
    }
    
    try {
        await api.updateMedicine(id, data);
        bootstrap.Modal.getInstance(document.getElementById('addMedicineModal')).hide();
        showToast('Medicine updated successfully!', 'success');
        navigateTo('medicines');
    } catch (error) {
        showToast('Failed to update medicine: ' + error.message, 'danger');
    }
}

async function deleteMedicine(id) {
    if (!confirm('⚠️ Are you sure you want to delete this medicine?\nThis action cannot be undone!')) return;
    
    try {
        await api.deleteMedicine(id);
        showToast('Medicine deleted successfully!', 'success');
        navigateTo('medicines');
    } catch (error) {
        showToast('Failed to delete medicine: ' + error.message, 'danger');
    }
}

async function viewBatches(medicineId) {
    try {
        const batches = await api.getBatches(medicineId);
        const medicine = medicinesData?.find(m => m.id === medicineId);
        
        if (!batches || batches.length === 0) {
            showToast(`No batches found for ${medicine?.name || 'this medicine'}`, 'info');
            return;
        }
        
        const batchList = batches.map(b => 
            `📦 Batch: ${b.batch_no}\n   Qty: ${b.quantity}\n   Exp: ${b.expiry_date}\n   Price: $${b.selling_price || b.purchase_price || 0}`
        ).join('\n\n');
        
        alert(`📋 Batches for ${medicine?.name || 'Medicine'}:\n\n${batchList}`);
    } catch (error) {
        showToast('Failed to load batches: ' + error.message, 'danger');
    }
}

// ============ SUPPLIER MODALS ============

function openAddSupplierModal() {
    document.getElementById('addSupplierForm').reset();
    const modal = new bootstrap.Modal(document.getElementById('addSupplierModal'));
    modal.show();
}

async function saveSupplier() {
    const data = {
        name: document.getElementById('sup_name').value,
        company_name: document.getElementById('sup_company').value,
        phone: document.getElementById('sup_phone').value,
        email: document.getElementById('sup_email').value,
        address: document.getElementById('sup_address').value
    };
    
    if (!data.name) {
        showToast('Supplier name is required!', 'warning');
        return;
    }
    
    try {
        await api.createSupplier(data);
        bootstrap.Modal.getInstance(document.getElementById('addSupplierModal')).hide();
        showToast('Supplier added successfully!', 'success');
        navigateTo('suppliers');
    } catch (error) {
        showToast('Failed to add supplier: ' + error.message, 'danger');
    }
}

// ============ SALE MODALS ============

let saleCart = [];
let saleSubtotal = 0;

function openSaleModal() {
    saleCart = [];
    saleSubtotal = 0;
    
    document.getElementById('sale_customer').value = 'Walk-in Customer';
    document.getElementById('sale_date').value = new Date().toISOString().split('T')[0];
    document.getElementById('sale_discount').value = 0;
    document.getElementById('sale_cart').innerHTML = '<p class="text-muted text-center">No items added yet</p>';
    document.getElementById('sale_subtotal').value = '0';
    document.getElementById('sale_total').value = '0';
    document.getElementById('sale_search').value = '';
    document.getElementById('saleSearchResults').innerHTML = '';
    
    const modal = new bootstrap.Modal(document.getElementById('createSaleModal'));
    modal.show();
}

async function searchMedicinesForSale(query) {
    const resultsDiv = document.getElementById('saleSearchResults');
    if (!query || query.length < 2) {
        resultsDiv.innerHTML = '';
        return;
    }
    
    try {
        const medicines = await api.getMedicines();
        const filtered = medicines.filter(m => 
            m.name.toLowerCase().includes(query.toLowerCase()) ||
            (m.generic_name && m.generic_name.toLowerCase().includes(query.toLowerCase()))
        ).slice(0, 10);
        
        if (filtered.length === 0) {
            resultsDiv.innerHTML = '<p class="text-muted">No medicines found</p>';
            return;
        }
        
        resultsDiv.innerHTML = `
            <div class="list-group">
                ${filtered.map(m => `
                    <button class="list-group-item list-group-item-action" onclick="addToCart(${m.id}, '${m.name}')">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${m.name}</strong>
                                <small class="text-muted d-block">${m.generic_name || 'No generic'}</small>
                            </div>
                            <span class="badge bg-info">${m.category || 'General'}</span>
                        </div>
                    </button>
                `).join('')}
            </div>
        `;
    } catch (error) {
        resultsDiv.innerHTML = `<p class="text-danger">Error searching: ${error.message}</p>`;
    }
}

async function addToCart(medicineId, medicineName) {
    const quantity = parseInt(document.getElementById('sale_quantity').value) || 1;
    
    try {
        const stock = await api.getMedicineStock(medicineId);
        if (stock.total_stock < quantity) {
            showToast(`Not enough stock! Available: ${stock.total_stock}`, 'warning');
            return;
        }
        
        const existing = saleCart.find(item => item.medicine_id === medicineId);
        if (existing) {
            existing.quantity += quantity;
        } else {
            const price = stock.batches?.[0]?.selling_price || 0;
            saleCart.push({
                medicine_id: medicineId,
                medicine_name: medicineName,
                quantity: quantity,
                selling_price: price
            });
        }
        
        updateSaleCart();
        document.getElementById('sale_search').value = '';
        document.getElementById('saleSearchResults').innerHTML = '';
        showToast(`${medicineName} added to cart!`, 'success');
    } catch (error) {
        showToast('Failed to add item: ' + error.message, 'danger');
    }
}

function removeFromCart(index) {
    const item = saleCart[index];
    saleCart.splice(index, 1);
    updateSaleCart();
    showToast(`${item.medicine_name} removed from cart`, 'info');
}

function updateSaleCart() {
    const cartDiv = document.getElementById('sale_cart');
    saleSubtotal = saleCart.reduce((sum, item) => sum + (item.quantity * item.selling_price), 0);
    
    if (saleCart.length === 0) {
        cartDiv.innerHTML = '<p class="text-muted text-center">No items added yet</p>';
        document.getElementById('sale_subtotal').value = '0';
        updateSaleTotal();
        return;
    }
    
    cartDiv.innerHTML = `
        <div class="table-responsive">
            <table class="table table-sm table-hover">
                <thead>
                    <tr>
                        <th>Medicine</th>
                        <th class="text-center">Qty</th>
                        <th class="text-end">Price</th>
                        <th class="text-end">Total</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    ${saleCart.map((item, index) => `
                        <tr>
                            <td><strong>${item.medicine_name}</strong></td>
                            <td class="text-center">
                                <button class="btn btn-sm btn-outline-secondary" onclick="updateCartQuantity(${index}, -1)">-</button>
                                <span class="mx-2">${item.quantity}</span>
                                <button class="btn btn-sm btn-outline-secondary" onclick="updateCartQuantity(${index}, 1)">+</button>
                            </td>
                            <td class="text-end">$${item.selling_price.toFixed(2)}</td>
                            <td class="text-end"><strong>$${(item.quantity * item.selling_price).toFixed(2)}</strong></td>
                            <td>
                                <button class="btn btn-sm btn-danger" onclick="removeFromCart(${index})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="3" class="text-end"><strong>Subtotal:</strong></td>
                        <td class="text-end"><strong>$${saleSubtotal.toFixed(2)}</strong></td>
                        <td></td>
                    </tr>
                </tfoot>
            </table>
        </div>
    `;
    
    document.getElementById('sale_subtotal').value = saleSubtotal.toFixed(2);
    updateSaleTotal();
}

function updateCartQuantity(index, change) {
    const item = saleCart[index];
    const newQty = item.quantity + change;
    if (newQty < 1) {
        removeFromCart(index);
        return;
    }
    item.quantity = newQty;
    updateSaleCart();
}

function updateSaleTotal() {
    const discount = parseFloat(document.getElementById('sale_discount').value) || 0;
    const total = saleSubtotal - discount;
    document.getElementById('sale_total').value = total.toFixed(2);
}

async function createSale() {
    if (saleCart.length === 0) {
        showToast('Please add at least one item to the sale!', 'warning');
        return;
    }
    
    const data = {
        customer_name: document.getElementById('sale_customer').value || 'Walk-in Customer',
        sale_date: document.getElementById('sale_date').value || new Date().toISOString().split('T')[0],
        discount_amount: parseFloat(document.getElementById('sale_discount').value) || 0,
        items: saleCart.map(item => ({
            medicine_id: item.medicine_id,
            quantity: item.quantity
        }))
    };
    
    try {
        await api.createSale(data);
        bootstrap.Modal.getInstance(document.getElementById('createSaleModal')).hide();
        showToast('✅ Sale completed successfully!', 'success');
        navigateTo('sales');
    } catch (error) {
        showToast('Failed to create sale: ' + error.message, 'danger');
    }
}

async function viewSale(id) {
    try {
        const sale = await api.getSale(id);
        const items = sale.items || [];
        const itemList = items.map(item => 
            `  • ${item.medicine_name || 'Medicine'}: ${item.quantity} x $${item.selling_price} = $${(item.quantity * item.selling_price).toFixed(2)}`
        ).join('\n');
        
        alert(`📋 Sale Details\n\n` +
              `Invoice: ${sale.invoice_number}\n` +
              `Date: ${sale.sale_date}\n` +
              `Customer: ${sale.customer_name || 'Walk-in'}\n` +
              `\nItems:\n${itemList || '  No items'}\n` +
              `\nSubtotal: $${sale.subtotal || 0}\n` +
              `Discount: $${sale.discount_amount || 0}\n` +
              `Total: $${sale.total_amount || 0}`);
    } catch (error) {
        showToast('Failed to load sale: ' + error.message, 'danger');
    }
}

async function downloadInvoice(saleId) {
    try {
        const blob = await api.downloadInvoice(saleId);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `invoice_${saleId}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast('Invoice downloaded successfully!', 'success');
    } catch (error) {
        showToast('Failed to download invoice: ' + error.message, 'danger');
    }
}

// ============ PURCHASE MODALS ============

function openPurchaseModal() {
    document.getElementById('purchase_supplier').value = '';
    document.getElementById('purchase_date').value = new Date().toISOString().split('T')[0];
    document.getElementById('purchaseItems').innerHTML = getPurchaseItemRow();
    
    const modal = new bootstrap.Modal(document.getElementById('createPurchaseModal'));
    modal.show();
}

function getPurchaseItemRow() {
    return `
        <div class="purchase-item-row row mb-2">
            <div class="col-md-2">
                <input type="number" class="form-control form-control-sm" placeholder="Med ID" name="purchase_medicine_id" required>
            </div>
            <div class="col-md-2">
                <input type="text" class="form-control form-control-sm" placeholder="Batch No" name="purchase_batch" required>
            </div>
            <div class="col-md-2">
                <input type="date" class="form-control form-control-sm" name="purchase_expiry" required>
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control form-control-sm" placeholder="Qty" name="purchase_qty" required>
            </div>
            <div class="col-md-2">
                <input type="number" step="0.01" min="0" class="form-control form-control-sm" placeholder="Buy Price" name="purchase_buy_price" required>
            </div>
            <div class="col-md-2">
                <input type="number" step="0.01" min="0" class="form-control form-control-sm" placeholder="Sell Price" name="purchase_sell_price" required>
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
        showToast('Item row removed', 'info');
    } else {
        showToast('At least one item is required!', 'warning');
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
        showToast('Please fill all fields in each item row!', 'warning');
        return;
    }
    
    if (items.length === 0) {
        showToast('Please add at least one valid item!', 'warning');
        return;
    }
    
    const data = {
        supplier_name: document.getElementById('purchase_supplier').value || 'Unknown Supplier',
        purchase_date: document.getElementById('purchase_date').value || new Date().toISOString().split('T')[0],
        items: items
    };
    
    try {
        await api.createPurchase(data);
        bootstrap.Modal.getInstance(document.getElementById('createPurchaseModal')).hide();
        showToast('✅ Purchase created successfully!', 'success');
        navigateTo('purchases');
    } catch (error) {
        showToast('Failed to create purchase: ' + error.message, 'danger');
    }
}

async function viewPurchase(id) {
    try {
        const purchase = await api.getPurchase(id);
        const items = purchase.items || [];
        const itemList = items.map(item => 
            `  • Medicine ID ${item.medicine_id}: ${item.quantity} x $${item.purchase_price} = $${(item.quantity * item.purchase_price).toFixed(2)}`
        ).join('\n');
        
        alert(`📋 Purchase Details\n\n` +
              `Invoice: ${purchase.invoice_number}\n` +
              `Date: ${purchase.purchase_date}\n` +
              `Supplier: ${purchase.supplier_name || 'Unknown'}\n` +
              `\nItems:\n${itemList || '  No items'}\n` +
              `\nTotal: $${purchase.total_amount || 0}`);
    } catch (error) {
        showToast('Failed to load purchase: ' + error.message, 'danger');
    }
}

// ============ TOAST NOTIFICATIONS ============

function showToast(message, type = 'info') {
    // Check if toast container exists
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 350px;
        `;
        document.body.appendChild(container);
    }
    
    const colors = {
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        info: '#2563eb'
    };
    
    const toast = document.createElement('div');
    toast.className = 'toast show';
    toast.style.cssText = `
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        border-left: 4px solid ${colors[type] || colors.info};
        animation: slideIn 0.3s ease;
        min-width: 250px;
    `;
    
    toast.innerHTML = `
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:32px;height:32px;border-radius:50%;background:${colors[type] || colors.info};display:flex;align-items:center;justify-content:center;color:white;">
                <i class="fas ${type === 'success' ? 'fa-check' : type === 'danger' ? 'fa-times' : type === 'warning' ? 'fa-exclamation' : 'fa-info'}"></i>
            </div>
            <div style="flex:1;">
                <div style="font-weight:600;font-size:0.9rem;">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <div style="font-size:0.85rem;color:#6b7280;">${message}</div>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" style="background:none;border:none;font-size:1.2rem;cursor:pointer;color:#9ca3af;">
                ×
            </button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Add animation styles
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(styleSheet);

console.log('Modals module loaded');