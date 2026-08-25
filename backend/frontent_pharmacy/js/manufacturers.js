// ============================================
// MANUFACTURERS MODULE
// ============================================

let editingManufacturerId = null;

async function renderManufacturers() {
    const content = document.getElementById('pageContent');
    try {
        const manufacturers = await api.getManufacturers();

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openManufacturerModal()">
                    <i class="fas fa-plus"></i> <span data-i18n="Add Manufacturer">Add Manufacturer</span>
                </button>
                <span class="text-muted">Total: ${manufacturers.length} <span data-i18n="Manufacturers">Manufacturers</span></span>
            </div>
            <div class="table-container">
                <table class="table table-hover" id="manufacturersTable">
                    <thead>
                        <tr>
                            <th data-i18n="name">Name</th>
                            <th data-i18n="Country">Country</th>
                            <th>Contact Info</th>
                            <th data-i18n="Actions">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="manufacturersTableBody">
                        ${manufacturers.map(m => `
                            <tr>
                                <td><strong>${m.name}</strong></td>
                                <td>${m.country || '-'}</td>
                                <td>${m.contact_info || '-'}</td>
                                <td class="text-nowrap">
                                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editManufacturer(${m.id})">
                                        <i class="fas fa-edit"></i> <span data-i18n="Edit">Edit</span>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteManufacturer(${m.id})">
                                        <i class="fas fa-trash"></i> <span data-i18n="Delete">Delete</span>
                                    </button>
                                </td>
                            </tr>
                        `).join('') || `<tr><td colspan="4" class="text-center text-muted">${t('No data found')}</td></tr>`}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">${t('Failed to load')}: ${error.message}</div>`;
    }
}

function openManufacturerModal() {
    editingManufacturerId = null;
    document.getElementById('manufacturerForm').reset();
    const btn = document.getElementById('manufacturerSaveBtn');
        if (btn) btn.innerHTML = `<i class="fas fa-save"></i> ${t('Save Manufacturer')}`;
    new bootstrap.Modal(document.getElementById('manufacturerModal')).show();
}

async function editManufacturer(id) {
    try {
        const manufacturers = await api.getManufacturers();
        const m = manufacturers.find(x => x.id === id);
        if (!m) { SwalAlert.error(t('No data found')); return; }
        editingManufacturerId = id;
        document.getElementById('manufacturer_name').value = m.name || '';
        document.getElementById('manufacturer_country').value = m.country || '';
        document.getElementById('manufacturer_contact_info').value = m.contact_info || '';
        const btn = document.getElementById('manufacturerSaveBtn');
if (btn) btn.innerHTML = `<i class="fas fa-save"></i> ${t('Save Manufacturer')}`;
        new bootstrap.Modal(document.getElementById('manufacturerModal')).show();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function saveManufacturer() {
    const data = {
        name: document.getElementById('manufacturer_name').value,
        country: document.getElementById('manufacturer_country').value || null,
        contact_info: document.getElementById('manufacturer_contact_info').value || null
    };

    if (!data.name) {
        SwalAlert.warning(t('Manufacturer name is required'));
        return;
    }

    try {
        if (editingManufacturerId) {
            await api.updateManufacturer(editingManufacturerId, data);
            SwalAlert.success(t('Manufacturer updated successfully'));
        } else {
            await api.createManufacturer(data);
            SwalAlert.success(t('Manufacturer added successfully'));
        }
        editingManufacturerId = null;
        bootstrap.Modal.getInstance(document.getElementById('manufacturerModal')).hide();
        renderManufacturers();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function deleteManufacturer(id) {
    const result = await SwalAlert.confirm(t('Delete this manufacturer?'));
    if (!result.isConfirmed) return;
    try {
        await api.deleteManufacturer(id);
        SwalAlert.success(t('Manufacturer deleted successfully'));
        renderManufacturers();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Manufacturers module loaded');
