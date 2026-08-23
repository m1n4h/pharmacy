// ============================================
// BRANCHES MODULE
// ============================================

let editingBranchId = null;

async function renderBranches() {
    const content = document.getElementById('pageContent');
    try {
        const branches = await api.getBranches();

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openBranchModal()">
                    <i class="fas fa-plus"></i> <span data-i18n="addBranch">Add Branch</span>
                </button>
                <span class="text-muted">Total: ${branches.length} <span data-i18n="branches">branches</span></span>
            </div>
            <div class="table-container">
                <table class="table table-hover" id="branchesTable">
                    <thead>
                        <tr>
                            <th data-i18n="name">Name</th>
                            <th data-i18n="code">Code</th>
                            <th data-i18n="phone">Phone</th>
                            <th data-i18n="address">Address</th>
                            <th data-i18n="status">Status</th>
                            <th data-i18n="actions">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="branchesTableBody">
                        ${branches.map(b => `
                            <tr>
                                <td><strong>${b.name}</strong>${b.is_main ? ' <span class="badge bg-primary">Main</span>' : ''}</td>
                                <td>${b.code || '-'}</td>
                                <td>${b.phone || '-'}</td>
                                <td>${b.address || '-'}</td>
                                <td>
                                    <span class="badge ${b.is_active !== false ? 'bg-success' : 'bg-secondary'}">
                                        ${b.is_active !== false ? 'Active' : 'Inactive'}
                                    </span>
                                </td>
                                <td class="text-nowrap">
                                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editBranch(${b.id})">
                                        <i class="fas fa-edit"></i> <span data-i18n="edit">Edit</span>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteBranch(${b.id})">
                                        <i class="fas fa-trash"></i> <span data-i18n="delete">Delete</span>
                                    </button>
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="6" class="text-center text-muted">No branches found.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load branches: ${error.message}</div>`;
    }
}

function openBranchModal() {
    editingBranchId = null;
    document.getElementById('branchForm').reset();
    document.getElementById('branch_is_main').checked = false;
    const btn = document.getElementById('branchSaveBtn');
    if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Save Branch';
    new bootstrap.Modal(document.getElementById('branchModal')).show();
}

async function editBranch(id) {
    try {
        const branches = await api.getBranches();
        const b = branches.find(x => x.id === id);
        if (!b) { SwalAlert.error('Branch not found'); return; }
        editingBranchId = id;
        const set = (el, val) => { const e = document.getElementById(el); if (e) e.value = val || ''; };
        set('branch_name', b.name);
        set('branch_code', b.code);
        set('branch_address', b.address);
        set('branch_phone', b.phone);
        set('branch_email', b.email);
        set('branch_region', b.region);
        set('branch_district', b.district);
        document.getElementById('branch_is_main').checked = !!b.is_main;
        const btn = document.getElementById('branchSaveBtn');
        if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Update Branch';
        new bootstrap.Modal(document.getElementById('branchModal')).show();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function saveBranch() {
    const data = {
        name: document.getElementById('branch_name').value,
        code: document.getElementById('branch_code').value || null,
        address: document.getElementById('branch_address').value || null,
        phone: document.getElementById('branch_phone').value || null,
        email: document.getElementById('branch_email').value || null,
        region: document.getElementById('branch_region').value || null,
        district: document.getElementById('branch_district').value || null,
        is_main: document.getElementById('branch_is_main').checked
    };

    if (!data.name) {
        SwalAlert.warning('Branch name is required!');
        return;
    }

    try {
        if (editingBranchId) {
            await api.updateBranch(editingBranchId, data);
            SwalAlert.success('Branch updated successfully!');
        } else {
            await api.createBranch(data);
            SwalAlert.success('Branch added successfully!');
        }
        editingBranchId = null;
        bootstrap.Modal.getInstance(document.getElementById('branchModal')).hide();
        renderBranches();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function deleteBranch(id) {
    const result = await SwalAlert.confirm('Delete this branch? This action cannot be undone.');
    if (!result.isConfirmed) return;
    try {
        await api.deleteBranch(id);
        SwalAlert.success('Branch deleted successfully!');
        renderBranches();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Branches module loaded');
