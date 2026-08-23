// ============================================
// CUSTOMERS MODULE
// ============================================

let editingCustomerId = null;
let customersData = [];

async function renderCustomers() {
    const content = document.getElementById('pageContent');
    try {
        customersData = await api.getCustomers();

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openCustomerModal()">
                    <i class="fas fa-plus"></i> <span data-i18n="addCustomer">Add Customer</span>
                </button>
                <div class="d-flex align-items-center flex-wrap gap-2">
                    <span class="text-muted">Total: ${customersData.length} <span data-i18n="customers">customers</span></span>
                    <input type="text" class="form-control" style="width:200px;max-width:100%;"
                           placeholder="Search name/phone..." oninput="filterCustomers(this.value)">
                </div>
            </div>
            <div class="table-container">
                <table class="table table-hover" id="customersTable">
                    <thead>
                        <tr>
                            <th data-i18n="name">Name</th>
                            <th data-i18n="phone">Phone</th>
                            <th data-i18n="email">Email</th>
                            <th data-i18n="totalPurchases">Total Purchases</th>
                            <th data-i18n="totalSpent">Total Spent</th>
                            <th data-i18n="actions">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="customersTableBody">
                        ${customersData.map(c => `
                            <tr>
                                <td><strong>${c.name}</strong></td>
                                <td>${c.phone || '-'}</td>
                                <td>${c.email || '-'}</td>
                                <td>${c.total_purchases || 0}</td>
                                <td><strong>${formatMoney(c.total_spent || 0)}</strong></td>
                                <td class="text-nowrap">
                                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editCustomer(${c.id})">
                                        <i class="fas fa-edit"></i> <span data-i18n="edit">Edit</span>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteCustomer(${c.id})">
                                        <i class="fas fa-trash"></i> <span data-i18n="delete">Delete</span>
                                    </button>
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="6" class="text-center text-muted">No customers found.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load customers: ${error.message}</div>`;
    }
}

function filterCustomers(query) {
    const rows = document.querySelectorAll('#customersTableBody tr');
    const q = query.toLowerCase();
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
    });
}

function openCustomerModal() {
    editingCustomerId = null;
    document.getElementById('customerForm').reset();
    const btn = document.getElementById('customerSaveBtn');
    if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Save Customer';
    new bootstrap.Modal(document.getElementById('customerModal')).show();
}

async function editCustomer(id) {
    try {
        const c = await api.getCustomer(id);
        if (!c) { SwalAlert.error('Customer not found'); return; }
        editingCustomerId = id;
        const set = (el, val) => { const e = document.getElementById(el); if (e) e.value = val || ''; };
        set('customer_name', c.name);
        set('customer_phone', c.phone);
        set('customer_email', c.email);
        set('customer_address', c.address);
        set('customer_gender', c.gender);
        set('customer_notes', c.notes);
        const btn = document.getElementById('customerSaveBtn');
        if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Update Customer';
        new bootstrap.Modal(document.getElementById('customerModal')).show();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function saveCustomer() {
    const data = {
        name: document.getElementById('customer_name').value,
        phone: document.getElementById('customer_phone').value || null,
        email: document.getElementById('customer_email').value || null,
        address: document.getElementById('customer_address').value || null,
        gender: document.getElementById('customer_gender').value || null,
        notes: document.getElementById('customer_notes').value || null
    };

    if (!data.name) {
        SwalAlert.warning('Customer name is required!');
        return;
    }

    try {
        if (editingCustomerId) {
            await api.updateCustomer(editingCustomerId, data);
            SwalAlert.success('Customer updated successfully!');
        } else {
            await api.createCustomer(data);
            SwalAlert.success('Customer added successfully!');
        }
        editingCustomerId = null;
        bootstrap.Modal.getInstance(document.getElementById('customerModal')).hide();
        renderCustomers();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function deleteCustomer(id) {
    const result = await SwalAlert.confirm('Delete this customer? This action cannot be undone.');
    if (!result.isConfirmed) return;
    try {
        await api.deleteCustomer(id);
        SwalAlert.success('Customer deleted successfully!');
        renderCustomers();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Customers module loaded');
