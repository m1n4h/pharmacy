// ============================================
// MEDICINES MODULE
// ============================================

let medicinesData = [];
let editingMedicineId = null;

async function renderMedicines() {
    const content = document.getElementById('pageContent');
    try {
        medicinesData = await api.getMedicines();
        console.log('Medicines loaded:', medicinesData.length);
        
        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openAddMedicineModal()">
                    <i class="fas fa-plus"></i> Add Medicine
                </button>
                <div class="d-flex align-items-center flex-wrap gap-2">
                    <span class="text-muted">Total: ${medicinesData.length} medicines</span>
                    <input type="text" class="form-control" style="width:200px;max-width:100%;"
                           placeholder="Search..." oninput="filterMedicines(this.value)">
                </div>
            </div>
            <div class="table-container">
                <table class="table table-hover" id="medicinesTable">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Generic</th>
                            <th>Category</th>
                            <th>Unit</th>
                            <th>Strength</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="medicinesTableBody">
                        ${medicinesData.map(med => `
                            <tr>
                                <td>${med.id}</td>
                                <td><strong>${med.name}</strong></td>
                                <td>${med.generic_name || '-'}</td>
                                <td><span class="badge bg-info">${med.category || 'General'}</span></td>
                                <td>${med.unit || '-'}</td>
                                <td>${med.strength || '-'}</td>
                                <td class="text-nowrap">
                                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editMedicine(${med.id})">Edit</button>
                                    <button class="btn btn-sm btn-outline-info me-1" onclick="viewBatches(${med.id})">Batches</button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteMedicine(${med.id})">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load medicines: ${error.message}</div>`;
    }
}

function filterMedicines(query) {
    const rows = document.querySelectorAll('#medicinesTableBody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query.toLowerCase()) ? '' : 'none';
    });
}

function openAddMedicineModal() {
    editingMedicineId = null;
    document.getElementById('addMedicineForm').reset();
    document.getElementById('aiSuggestHint').textContent = '';
    const btn = document.getElementById('medSaveBtn');
    if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Save Medicine';
    const modal = new bootstrap.Modal(document.getElementById('addMedicineModal'));
    modal.show();
}

// AI-assisted medicine creation
async function aiSuggestMedicine() {
    const nameInput = document.getElementById('med_name');
    const hint = document.getElementById('aiSuggestHint');
    const name = nameInput.value.trim();
    if (!name) {
        SwalAlert.warning(t('Enter medicine name first'));
        nameInput.focus();
        return;
    }
    hint.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>AI inachanganua...';
    const btn = document.querySelector('#addMedicineModal .btn-outline-primary');
    if (btn) btn.disabled = true;
    try {
        const res = await api.aiSuggestMedicine(name);
        const s = res?.data || {};
        if (s.generic_name) document.getElementById('med_generic').value = s.generic_name;
        if (s.category && document.querySelector('#med_category option[value="' + s.category + '"]')) {
            document.getElementById('med_category').value = s.category;
        }
        if (s.form && document.querySelector('#med_form option[value="' + s.form + '"]')) {
            document.getElementById('med_form').value = s.form;
        }
        if (s.unit && document.querySelector('#med_unit option[value="' + s.unit + '"]')) {
            document.getElementById('med_unit').value = s.unit;
        }
        if (s.strength && !document.getElementById('med_strength').value) {
            document.getElementById('med_strength').value = s.strength;
        }
        const reasons = (s.explanation || []).join(' • ');
        hint.innerHTML = `<span class="text-success"><i class="fas fa-check-circle me-1"></i>${s.confidence === 'high' ? 'Imepatikana kwa uhakika' : 'Maelezo yamependekezwa'} (${s.form || '?'}, ${s.unit || '?'})</span>`;
        if (reasons) hint.innerHTML += `<div class="text-muted mt-1">${reasons}</div>`;
    } catch (e) {
        hint.innerHTML = `<span class="text-danger">AI haikufanikiwa: ${e.message}</span>`;
    } finally {
        if (btn) btn.disabled = false;
    }
}

async function saveMedicine() {
    const data = {
        name: document.getElementById('med_name').value,
        generic_name: document.getElementById('med_generic').value,
        brand: document.getElementById('med_brand').value,
        category: document.getElementById('med_category').value,
        form: document.getElementById('med_form').value,
        unit: document.getElementById('med_unit').value,
        strength: document.getElementById('med_strength').value,
        barcode: document.getElementById('med_barcode').value,
        default_purchase_price: parseFloat(document.getElementById('med_purchase_price')?.value) || 0,
        default_selling_price: parseFloat(document.getElementById('med_selling_price')?.value) || 0
    };
    
    if (!data.name) {
        SwalAlert.warning(t('Medicine name is required'));
        return;
    }
    
    try {
        if (editingMedicineId) {
            await api.updateMedicine(editingMedicineId, data);
            SwalAlert.success(t('Medicine updated successfully'));
        } else {
            await api.createMedicine(data);
            SwalAlert.success(t('Medicine added successfully'));
        }
        editingMedicineId = null;
        bootstrap.Modal.getInstance(document.getElementById('addMedicineModal')).hide();
        navigateTo('medicines');
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function deleteMedicine(id) {
    const result = await SwalAlert.confirm(t('Are you sure you want to delete this medicine?'));
    if (!result.isConfirmed) return;
    try {
        await api.deleteMedicine(id);
        SwalAlert.success(t('Medicine deleted successfully'));
        navigateTo('medicines');
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function editMedicine(id) {
    try {
        const med = await api.getMedicine(id);
        editingMedicineId = id;
        const set = (el, val) => { const e = document.getElementById(el); if (e) e.value = val || ''; };
        set('med_name', med.name);
        set('med_generic', med.generic_name);
        set('med_brand', med.brand);
        set('med_category', med.category);
        set('med_form', med.form);
        set('med_unit', med.unit);
        set('med_strength', med.strength);
        set('med_barcode', med.barcode);
        set('med_purchase_price', med.default_purchase_price);
        set('med_selling_price', med.default_selling_price);
        document.getElementById('aiSuggestHint').textContent = '';
        const btn = document.getElementById('medSaveBtn');
        if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Update Medicine';
        new bootstrap.Modal(document.getElementById('addMedicineModal')).show();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function viewBatches(medicineId) {
    try {
        const batches = await api.getBatches(medicineId);
        const medicine = medicinesData.find(m => m.id === medicineId);
        SwalAlert.success(`Batches for ${medicine?.name || 'Medicine'}:\n${batches.map(b => 
            `Batch: ${b.batch_no}, Qty: ${b.quantity}, Exp: ${b.expiry_date}`
        ).join('\n') || 'No batches found'}`);
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Medicines module loaded');
