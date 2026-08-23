// ============================================
// PRESCRIPTIONS MODULE
// ============================================

let rxCart = [];
let rxFilterStatus = '';
let editingRxId = null;

async function renderPrescriptions() {
    const content = document.getElementById('pageContent');
    try {
        const result = await api.getPrescriptions(rxFilterStatus);
        const prescriptions = result?.data?.items || [];

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-success" onclick="openPrescriptionModal()">
                    <i class="fas fa-plus"></i> New Prescription
                </button>
                <div class="d-flex align-items-center gap-2 flex-wrap">
                    <select class="form-control" onchange="setRxFilter(this.value)" style="width:200px;max-width:100%;">
                        <option value="">All Status</option>
                        <option value="pending" ${rxFilterStatus === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="dispensed" ${rxFilterStatus === 'dispensed' ? 'selected' : ''}>Dispensed</option>
                        <option value="cancelled" ${rxFilterStatus === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                    </select>
                    <span class="text-muted">Total: ${result?.data?.pagination?.total || prescriptions.length}</span>
                </div>
            </div>
            <div class="table-container">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>RX #</th>
                            <th>Patient</th>
                            <th>Doctor</th>
                            <th>Items</th>
                            <th>Total</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${prescriptions.map(rx => `
                            <tr>
                                <td><strong>${rx.prescription_no}</strong></td>
                                <td>${rx.patient_name}${rx.patient_age ? ` (${rx.patient_age} yrs)` : ''}</td>
                                <td>${rx.doctor_name || '-'}</td>
                                <td>${rx.items?.length || 0}</td>
                                <td><strong>${formatMoney(rx.total_amount || 0)}</strong></td>
                                <td>
                                    <span class="badge ${rx.status === 'dispensed' ? 'bg-success' : rx.status === 'cancelled' ? 'bg-danger' : 'bg-warning'}">
                                        ${rx.status}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-info me-1" onclick="viewPrescription(${rx.id})">View</button>
                                    ${rx.status === 'pending' ? `
                                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editPrescription(${rx.id})">Edit</button>
                                        <button class="btn btn-sm btn-success me-1" onclick="dispensePrescription(${rx.id})">Dispense</button>
                                        <button class="btn btn-sm btn-danger" onclick="deletePrescription(${rx.id})">Delete</button>
                                    ` : `
                                        <button class="btn btn-sm btn-danger" onclick="deletePrescription(${rx.id})">Delete</button>
                                    `}
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="7" class="text-center text-muted">No prescriptions found</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load prescriptions: ${error.message}</div>`;
    }
}

function setRxFilter(status) {
    rxFilterStatus = status;
    renderPrescriptions();
}

function openPrescriptionModal() {
    editingRxId = null;
    rxCart = [];
    document.getElementById('rx_patient_name').value = '';
    document.getElementById('rx_patient_age').value = '';
    document.getElementById('rx_doctor').value = '';
    document.getElementById('rx_notes').value = '';
    document.getElementById('rx_search').value = '';
    document.getElementById('rxSearchResults').innerHTML = '';
    document.getElementById('rxItems').innerHTML = '<p class="text-muted text-center">No medicines added yet</p>';
    const modal = new bootstrap.Modal(document.getElementById('createPrescriptionModal'));
    const btn = document.getElementById('rxSaveBtn');
    if (btn) btn.innerHTML = '<i class="fas fa-check"></i> Save Prescription';
    modal.show();
}

async function editPrescription(id) {
    try {
        const rx = await api.getPrescription(id);
        editingRxId = id;
        rxCart = (rx.items || []).map(i => ({
            medicine_id: i.medicine_id,
            medicine_name: i.medicine_name,
            quantity: i.quantity
        }));
        document.getElementById('rx_patient_name').value = rx.patient_name || '';
        document.getElementById('rx_patient_age').value = rx.patient_age || '';
        document.getElementById('rx_doctor').value = rx.doctor_name || '';
        document.getElementById('rx_notes').value = rx.notes || '';
        updateRxCart();
        const btn = document.getElementById('rxSaveBtn');
        if (btn) btn.innerHTML = '<i class="fas fa-check"></i> Update Prescription';
        new bootstrap.Modal(document.getElementById('createPrescriptionModal')).show();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function deletePrescription(id) {
    const result = await SwalAlert.confirm('Delete this prescription? This cannot be undone.');
    if (!result.isConfirmed) return;
    try {
        const res = await api.deletePrescription(id);
        if (res && res.success === false) {
            SwalAlert.error(res.message || 'Unknown error');
            return;
        }
        SwalAlert.success('Prescription deleted.');
        renderPrescriptions();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function searchMedicinesForPrescription(query) {
    const resultsDiv = document.getElementById('rxSearchResults');
    if (!query || query.length < 2) {
        resultsDiv.innerHTML = '';
        return;
    }
    try {
        const medicines = await api.getPosMedicines(query);
        if (medicines.length === 0) {
            resultsDiv.innerHTML = '<p class="text-muted">No medicines found</p>';
            return;
        }
        resultsDiv.innerHTML = `
            <div class="list-group">
                ${medicines.map(m => `
                    <button class="list-group-item list-group-item-action" onclick="addRxToCart(${m.id}, '${m.name}')">
                        <strong>${m.name}</strong> - ${m.generic_name || 'No generic'}
                        <span class="badge bg-info float-end">${m.category || 'General'}</span>
                    </button>
                `).join('')}
            </div>
        `;
    } catch (error) {
        resultsDiv.innerHTML = `<p class="text-danger">Error searching: ${error.message}</p>`;
    }
}

async function addRxToCart(medicineId, medicineName) {
    const quantity = parseInt(document.getElementById('rx_quantity').value) || 1;
    try {
        const stock = await api.getMedicineStock(medicineId);
        if (stock.total_stock < quantity) {
            SwalAlert.error(`Not enough stock! Available: ${stock.total_stock}`);
            return;
        }
        const existing = rxCart.find(item => item.medicine_id === medicineId);
        if (existing) {
            existing.quantity += quantity;
        } else {
            rxCart.push({
                medicine_id: medicineId,
                medicine_name: medicineName,
                quantity: quantity
            });
        }
        document.getElementById('rxSearchResults').innerHTML = '';
        document.getElementById('rx_search').value = '';
        updateRxCart();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

function removeRxFromCart(index) {
    rxCart.splice(index, 1);
    updateRxCart();
}

function updateRxCart() {
    const cartDiv = document.getElementById('rxItems');
    if (rxCart.length === 0) {
        cartDiv.innerHTML = '<p class="text-muted text-center">No medicines added yet</p>';
        return;
    }
    cartDiv.innerHTML = `
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Medicine</th>
                    <th>Qty</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                ${rxCart.map((item, index) => `
                    <tr>
                        <td>${item.medicine_name}</td>
                        <td>${item.quantity}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="removeRxFromCart(${index})">
                                <i class="fas fa-times"></i>
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function createPrescription() {
    if (rxCart.length === 0) {
        SwalAlert.warning('Please add at least one medicine!');
        return;
    }
    const data = {
        patient_name: document.getElementById('rx_patient_name').value,
        patient_age: parseInt(document.getElementById('rx_patient_age').value) || null,
        doctor_name: document.getElementById('rx_doctor').value || null,
        notes: document.getElementById('rx_notes').value || null,
        items: rxCart.map(item => ({
            medicine_id: item.medicine_id,
            quantity: item.quantity
        }))
    };
    try {
        let result;
        if (editingRxId) {
            result = await api.updatePrescription(editingRxId, data);
        } else {
            result = await api.createPrescription(data);
        }
        if (result && result.success === false) {
            SwalAlert.error(result.message || 'Unknown error');
            return;
        }
        bootstrap.Modal.getInstance(document.getElementById('createPrescriptionModal')).hide();
        SwalAlert.success(editingRxId ? 'Prescription updated successfully!' : 'Prescription created successfully!');
        editingRxId = null;
        navigateTo('prescriptions');
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function viewPrescription(id) {
    try {
        const rx = await api.getPrescription(id);
        const itemLines = (rx?.items || []).map(i => `  • ${i.medicine_name} x${i.quantity} @ ${formatMoney(i.price)}`).join('\n');
        SwalAlert.success(`RX ${rx.prescription_no}\nPatient: ${rx.patient_name}${rx.patient_age ? ` (${rx.patient_age})` : ''}\nDoctor: ${rx.doctor_name || '-'}\nStatus: ${rx.status}\n\nItems:\n${itemLines}\n\nTotal: ${formatMoney(rx.total_amount)}`);
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function dispensePrescription(id) {
    const result = await SwalAlert.confirm('Dispense this prescription? Stock itapunguzwa.');
    if (!result.isConfirmed) return;
    try {
        const result = await api.dispensePrescription(id);
        if (result && result.success === false) {
            SwalAlert.error(result.message || 'Unknown error');
            return;
        }
        SwalAlert.success('Prescription dispensed successfully!');
        renderPrescriptions();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function cancelPrescription(id) {
    const result = await SwalAlert.confirm('Cancel this prescription?');
    if (!result.isConfirmed) return;
    try {
        const result = await api.cancelPrescription(id);
        if (result && result.success === false) {
            SwalAlert.error(result.message || 'Unknown error');
            return;
        }
        SwalAlert.success('Prescription cancelled.');
        renderPrescriptions();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Prescriptions module loaded');
