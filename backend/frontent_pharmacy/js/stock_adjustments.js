// ============================================
// STOCK ADJUSTMENTS MODULE
// ============================================

let stockAdjustmentMedicineSearchTimeout = null;
let stockAdjustmentSelectedMedicine = null;
let stockAdjustmentSelectedBatch = null;

async function renderStockAdjustments() {
    const content = document.getElementById('pageContent');
    try {
        const adjustments = await api.getStockAdjustments();

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openStockAdjustmentModal()">
                    <i class="fas fa-plus"></i> <span data-i18n="newAdjustment">New Adjustment</span>
                </button>
                <span class="text-muted">Total: ${adjustments.length} <span data-i18n="adjustments">adjustments</span></span>
            </div>
            <div class="table-container">
                <table class="table table-hover" id="stockAdjustmentsTable">
                    <thead>
                        <tr>
                            <th data-i18n="medicine">Medicine</th>
                            <th data-i18n="batch">Batch</th>
                            <th data-i18n="systemQty">System Qty</th>
                            <th data-i18n="physicalQty">Physical Qty</th>
                            <th data-i18n="difference">Difference</th>
                            <th data-i18n="reason">Reason</th>
                            <th data-i18n="status">Status</th>
                            <th data-i18n="actions">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="stockAdjustmentsTableBody">
                        ${adjustments.map(adj => {
                            const diff = (adj.physical_quantity || 0) - (adj.system_quantity || 0);
                            const diffClass = diff > 0 ? 'text-success' : diff < 0 ? 'text-danger' : 'text-muted';
                            return `
                                <tr>
                                    <td><strong>${adj.medicine_name || 'Medicine #' + adj.medicine_id}</strong></td>
                                    <td>${adj.batch_no || '-'}</td>
                                    <td>${adj.system_quantity || 0}</td>
                                    <td>${adj.physical_quantity || 0}</td>
                                    <td><strong class="${diffClass}">${diff > 0 ? '+' : ''}${diff}</strong></td>
                                    <td>${adj.reason || '-'}</td>
                                    <td>
                                        <span class="badge ${adj.status === 'approved' ? 'bg-success' : adj.status === 'rejected' ? 'bg-danger' : 'bg-warning text-dark'}">
                                            ${adj.status || 'pending'}
                                        </span>
                                    </td>
                                    <td class="text-nowrap">
                                        ${adj.status === 'pending' ? `
                                            <button class="btn btn-sm btn-outline-success me-1" onclick="approveStockAdjustment(${adj.id})">
                                                <i class="fas fa-check"></i> <span data-i18n="approve">Approve</span>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" onclick="rejectStockAdjustment(${adj.id})">
                                                <i class="fas fa-times"></i> <span data-i18n="reject">Reject</span>
                                            </button>
                                        ` : '-'}
                                    </td>
                                </tr>
                            `;
                        }).join('') || '<tr><td colspan="8" class="text-center text-muted">No adjustments found.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load stock adjustments: ${error.message}</div>`;
    }
}

function openStockAdjustmentModal() {
    document.getElementById('stockAdjustmentForm').reset();
    stockAdjustmentSelectedMedicine = null;
    stockAdjustmentSelectedBatch = null;
    document.getElementById('adjustmentSearchResults').innerHTML = '';
    document.getElementById('adjustmentBatchResults').innerHTML = '';
    document.getElementById('adjustmentDiff').textContent = '-';
    document.getElementById('adjustmentDiff').className = '';
    const btn = document.getElementById('adjustmentSaveBtn');
    if (btn) btn.disabled = false;
    new bootstrap.Modal(document.getElementById('stockAdjustmentModal')).show();
}

async function searchMedicineForAdjustment(query) {
    const resultsDiv = document.getElementById('adjustmentSearchResults');
    if (!query || query.length < 2) {
        resultsDiv.innerHTML = '';
        stockAdjustmentSelectedMedicine = null;
        return;
    }

    clearTimeout(stockAdjustmentMedicineSearchTimeout);
    stockAdjustmentMedicineSearchTimeout = setTimeout(async () => {
        try {
            const medicines = await api.searchMedicines(query, 10);
            if (!medicines || medicines.length === 0) {
                resultsDiv.innerHTML = '<p class="text-muted">No medicines found</p>';
                return;
            }
            resultsDiv.innerHTML = `
                <div class="list-group" style="max-height:200px;overflow-y:auto;">
                    ${medicines.map(m => `
                        <button type="button" class="list-group-item list-group-item-action"
                            onclick="selectMedicineForAdjustment(${m.id}, '${(m.name || '').replace(/'/g, "\\'")}')">
                            <strong>${m.name}</strong>
                            <small class="text-muted ms-2">${m.category || ''}</small>
                        </button>
                    `).join('')}
                </div>
            `;
        } catch (e) {
            resultsDiv.innerHTML = '<p class="text-danger">Error searching</p>';
        }
    }, 300);
}

function selectMedicineForAdjustment(id, name) {
    stockAdjustmentSelectedMedicine = { id, name };
    document.getElementById('adjustment_medicine_search').value = name;
    document.getElementById('adjustmentSearchResults').innerHTML = '';
    document.getElementById('adjustmentBatchResults').innerHTML = '';
    stockAdjustmentSelectedBatch = null;
    loadBatchesForAdjustment(id);
}

async function loadBatchesForAdjustment(medicineId) {
    const batchDiv = document.getElementById('adjustmentBatchResults');
    try {
        const batches = await api.getBatches(medicineId);
        if (!batches || batches.length === 0) {
            batchDiv.innerHTML = '<p class="text-muted">No batches found for this medicine</p>';
            return;
        }
        batchDiv.innerHTML = `
            <div class="list-group" style="max-height:150px;overflow-y:auto;">
                ${batches.map(b => `
                    <button type="button" class="list-group-item list-group-item-action"
                        onclick="selectBatchForAdjustment('${(b.batch_no || '').replace(/'/g, "\\'")}', ${b.quantity || 0}, '${(b.expiry_date || '').replace(/'/g, "\\'")}')">
                        <strong>Batch: ${b.batch_no}</strong>
                        <small class="text-muted ms-2">Qty: ${b.quantity || 0}, Exp: ${b.expiry_date || '-'}</small>
                    </button>
                `).join('')}
            </div>
        `;
    } catch (e) {
        batchDiv.innerHTML = '<p class="text-danger">Error loading batches</p>';
    }
}

function selectBatchForAdjustment(batchNo, quantity, expiryDate) {
    stockAdjustmentSelectedBatch = { batch_no: batchNo, system_quantity: quantity, expiry_date: expiryDate };
    document.getElementById('adjustment_system_qty').value = quantity;
    document.getElementById('adjustmentBatchResults').innerHTML = '';
    updateAdjustmentDiff();
}

function updateAdjustmentDiff() {
    const systemQty = parseInt(document.getElementById('adjustment_system_qty').value) || 0;
    const physicalQty = parseInt(document.getElementById('adjustment_physical_qty').value) || 0;
    const diff = physicalQty - systemQty;
    const diffEl = document.getElementById('adjustmentDiff');
    if (diff > 0) {
        diffEl.textContent = '+' + diff;
        diffEl.className = 'text-success fw-bold';
    } else if (diff < 0) {
        diffEl.textContent = diff;
        diffEl.className = 'text-danger fw-bold';
    } else {
        diffEl.textContent = '0';
        diffEl.className = 'text-muted';
    }
}

async function saveStockAdjustment() {
    if (!stockAdjustmentSelectedMedicine) {
        SwalAlert.warning(t('Please select a medicine'));
        return;
    }
    if (!stockAdjustmentSelectedBatch) {
        SwalAlert.warning(t('Please select a batch'));
        return;
    }

    const physicalQty = parseInt(document.getElementById('adjustment_physical_qty').value);
    const reason = document.getElementById('adjustment_reason').value;
    const notes = document.getElementById('adjustment_notes').value;

    if (!physicalQty && physicalQty !== 0) {
        SwalAlert.warning(t('Please enter physical quantity'));
        return;
    }

    if (!reason) {
        SwalAlert.warning(t('Please enter a reason for the adjustment'));
        return;
    }

    const data = {
        medicine_id: stockAdjustmentSelectedMedicine.id,
        batch_no: stockAdjustmentSelectedBatch.batch_no,
        system_quantity: stockAdjustmentSelectedBatch.system_quantity,
        physical_quantity: physicalQty,
        reason: reason,
        notes: notes || null
    };

    const btn = document.getElementById('adjustmentSaveBtn');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...'; }

    try {
        await api.createStockAdjustment(data);
        bootstrap.Modal.getInstance(document.getElementById('stockAdjustmentModal')).hide();
        SwalAlert.success(t('Stock adjustment submitted successfully'));
        renderStockAdjustments();
    } catch (error) {
        SwalAlert.error(error.message);
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-save"></i> Submit Adjustment'; }
    }
}

async function approveStockAdjustment(id) {
    const result = await SwalAlert.confirm(t('Approve this stock adjustment?'));
    if (!result.isConfirmed) return;
    try {
        await api.approveStockAdjustment(id);
        SwalAlert.success(t('Stock adjustment approved'));
        renderStockAdjustments();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function rejectStockAdjustment(id) {
    const result = await SwalAlert.confirm(t('Reject this stock adjustment?'));
    if (!result.isConfirmed) return;
    try {
        await api.rejectStockAdjustment(id);
        SwalAlert.success(t('Stock adjustment rejected'));
        renderStockAdjustments();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Stock Adjustments module loaded');
