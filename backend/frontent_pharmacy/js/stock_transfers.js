// ============================================
// STOCK TRANSFERS MODULE
// ============================================

let transferMedicineSearchTimeout = null;
let transferSelectedMedicine = null;
let transferSelectedBatch = null;
let transferBranches = [];

async function renderStockTransfers() {
    const content = document.getElementById('pageContent');
    try {
        const transfers = await api.getStockTransfers();

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openStockTransferModal()">
                    <i class="fas fa-plus"></i> <span data-i18n="newTransfer">New Transfer</span>
                </button>
                <span class="text-muted">Total: ${transfers.length} <span data-i18n="transfers">transfers</span></span>
            </div>
            <div class="table-container">
                <table class="table table-hover" id="stockTransfersTable">
                    <thead>
                        <tr>
                            <th data-i18n="medicine">Medicine</th>
                            <th data-i18n="batch">Batch</th>
                            <th data-i18n="fromBranch">From Branch</th>
                            <th data-i18n="toBranch">To Branch</th>
                            <th data-i18n="quantity">Quantity</th>
                            <th data-i18n="status">Status</th>
                            <th data-i18n="actions">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="stockTransfersTableBody">
                        ${transfers.map(t => `
                            <tr>
                                <td><strong>${t.medicine_name || 'Medicine #' + t.medicine_id}</strong></td>
                                <td>${t.batch_no || '-'}</td>
                                <td>${t.from_branch_name || 'Branch #' + t.from_branch_id}</td>
                                <td>${t.to_branch_name || 'Branch #' + t.to_branch_id}</td>
                                <td>${t.quantity || 0}</td>
                                <td>
                                    <span class="badge ${t.status === 'approved' ? 'bg-success' : t.status === 'rejected' ? 'bg-danger' : 'bg-warning text-dark'}">
                                        ${t.status || 'pending'}
                                    </span>
                                </td>
                                <td class="text-nowrap">
                                    ${t.status === 'pending' ? `
                                        <button class="btn btn-sm btn-outline-success me-1" onclick="approveStockTransfer(${t.id})">
                                            <i class="fas fa-check"></i> <span data-i18n="approve">Approve</span>
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger" onclick="rejectStockTransfer(${t.id})">
                                            <i class="fas fa-times"></i> <span data-i18n="reject">Reject</span>
                                        </button>
                                    ` : '-'}
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="7" class="text-center text-muted">No stock transfers found.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load stock transfers: ${error.message}</div>`;
    }
}

async function openStockTransferModal() {
    document.getElementById('stockTransferForm').reset();
    transferSelectedMedicine = null;
    transferSelectedBatch = null;
    document.getElementById('transferSearchResults').innerHTML = '';
    document.getElementById('transferBatchResults').innerHTML = '';

    try {
        transferBranches = await api.getBranches();
        const fromSelect = document.getElementById('transfer_from_branch');
        const toSelect = document.getElementById('transfer_to_branch');
        fromSelect.innerHTML = '<option value="">Select branch...</option>';
        toSelect.innerHTML = '<option value="">Select branch...</option>';
        transferBranches.forEach(b => {
            fromSelect.innerHTML += `<option value="${b.id}">${b.name}</option>`;
            toSelect.innerHTML += `<option value="${b.id}">${b.name}</option>`;
        });
    } catch (e) {
        console.warn('Failed to load branches for transfer modal', e);
    }

    const btn = document.getElementById('transferSaveBtn');
    if (btn) btn.disabled = false;
    new bootstrap.Modal(document.getElementById('stockTransferModal')).show();
}

async function searchMedicineForTransfer(query) {
    const resultsDiv = document.getElementById('transferSearchResults');
    if (!query || query.length < 2) {
        resultsDiv.innerHTML = '';
        transferSelectedMedicine = null;
        return;
    }

    clearTimeout(transferMedicineSearchTimeout);
    transferMedicineSearchTimeout = setTimeout(async () => {
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
                            onclick="selectMedicineForTransfer(${m.id}, '${(m.name || '').replace(/'/g, "\\'")}')">
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

function selectMedicineForTransfer(id, name) {
    transferSelectedMedicine = { id, name };
    document.getElementById('transfer_medicine_search').value = name;
    document.getElementById('transferSearchResults').innerHTML = '';
    document.getElementById('transferBatchResults').innerHTML = '';
    transferSelectedBatch = null;
    loadBatchesForTransfer(id);
}

async function loadBatchesForTransfer(medicineId) {
    const batchDiv = document.getElementById('transferBatchResults');
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
                        onclick="selectBatchForTransfer('${(b.batch_no || '').replace(/'/g, "\\'")}', ${b.quantity || 0})">
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

function selectBatchForTransfer(batchNo, quantity) {
    transferSelectedBatch = { batch_no: batchNo, available_quantity: quantity };
    document.getElementById('transfer_batch_no').value = batchNo;
    document.getElementById('transferBatchResults').innerHTML = '';
}

async function saveStockTransfer() {
    if (!transferSelectedMedicine) {
        SwalAlert.warning(t('Please select a medicine'));
        return;
    }
    if (!transferSelectedBatch) {
        SwalAlert.warning(t('Please select a batch'));
        return;
    }

    const fromBranch = document.getElementById('transfer_from_branch').value;
    const toBranch = document.getElementById('transfer_to_branch').value;
    const quantity = parseInt(document.getElementById('transfer_quantity').value);
    const notes = document.getElementById('transfer_notes').value;

    if (!fromBranch) {
        SwalAlert.warning(t('Please select source branch'));
        return;
    }
    if (!toBranch) {
        SwalAlert.warning(t('Please select destination branch'));
        return;
    }
    if (fromBranch === toBranch) {
        SwalAlert.warning(t('Source and destination branches must be different'));
        return;
    }
    if (!quantity || quantity <= 0) {
        SwalAlert.warning(t('Please enter a valid quantity'));
        return;
    }
    if (transferSelectedBatch && quantity > transferSelectedBatch.available_quantity) {
        SwalAlert.warning(t('Quantity exceeds available stock').replace('{qty}', transferSelectedBatch.available_quantity));
        return;
    }

    const data = {
        medicine_id: transferSelectedMedicine.id,
        batch_no: transferSelectedBatch.batch_no,
        from_branch_id: parseInt(fromBranch),
        to_branch_id: parseInt(toBranch),
        quantity: quantity,
        notes: notes || null
    };

    const btn = document.getElementById('transferSaveBtn');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...'; }

    try {
        await api.createStockTransfer(data);
        bootstrap.Modal.getInstance(document.getElementById('stockTransferModal')).hide();
        SwalAlert.success(t('Stock transfer submitted successfully'));
        renderStockTransfers();
    } catch (error) {
        SwalAlert.error(error.message);
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-save"></i> Submit Transfer'; }
    }
}

async function approveStockTransfer(id) {
    const result = await SwalAlert.confirm(t('Approve this stock transfer?'));
    if (!result.isConfirmed) return;
    try {
        await api.approveStockTransfer(id);
        SwalAlert.success(t('Stock transfer approved'));
        renderStockTransfers();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function rejectStockTransfer(id) {
    const result = await SwalAlert.confirm(t('Reject this stock transfer?'));
    if (!result.isConfirmed) return;
    try {
        await api.rejectStockTransfer(id);
        SwalAlert.success(t('Stock transfer rejected'));
        renderStockTransfers();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Stock Transfers module loaded');
