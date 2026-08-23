// ============================================
// USERS & ROLES MODULE
// ============================================

async function renderUsers() {
    const content = document.getElementById('pageContent');
    try {
        const result = await api.getUsers();
        const users = result?.data?.items || [];

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-success" onclick="openUserModal()">
                    <i class="fas fa-user-plus"></i> Add User
                </button>
                <span class="text-muted">Total: ${users.length} users</span>
            </div>
            <div class="table-container">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${users.map(u => `
                            <tr>
                                <td>${u.id}</td>
                                <td>${u.full_name || '-'} ${u.is_superuser ? '<span class="badge bg-dark ms-1">SUPERUSER</span>' : ''}</td>
                                <td>${u.email}</td>
                                <td><span class="badge ${u.role === 'admin' || u.role === 'superadmin' ? 'bg-danger' : 'bg-primary'}">${u.role}</span></td>
                                <td>
                                    <span class="badge ${u.is_active ? 'bg-success' : 'bg-secondary'}">
                                        ${u.is_active ? 'Active' : 'Disabled'}
                                    </span>
                                </td>
                                <td class="text-nowrap">
                                    ${u.is_superuser
                                        ? '<span class="text-muted">Protected</span>'
                                        : `<button class="btn btn-sm ${u.is_active ? 'btn-outline-warning' : 'btn-outline-success'} me-1" onclick="toggleUser(${u.id})">${u.is_active ? 'Disable' : 'Enable'}</button>
                                           <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${u.id}, '${(u.full_name || u.email).replace(/'/g, "\\'")}')">Delete</button>`
                                    }
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="6" class="text-center text-muted">No users found</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load users: ${error.message}</div>`;
    }
}

function openUserModal() {
    document.getElementById('user_full_name').value = '';
    document.getElementById('user_email').value = '';
    document.getElementById('user_password').value = '';
    document.getElementById('user_role').value = 'staff';
    const modal = new bootstrap.Modal(document.getElementById('addUserModal'));
    modal.show();
}

async function saveUser() {
    const data = {
        full_name: document.getElementById('user_full_name').value,
        email: document.getElementById('user_email').value,
        password: document.getElementById('user_password').value,
        role: document.getElementById('user_role').value
    };
    if (!data.email || !data.password || !data.full_name) {
        SwalAlert.warning('Jaza full name, email na password!');
        return;
    }
    try {
        const result = await api.createUser(data);
        if (result && result.success === false) {
            SwalAlert.error(result.message || 'Unknown error');
            return;
        }
        bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
        SwalAlert.success('User created successfully!');
        renderUsers();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function toggleUser(id) {
    const result = await SwalAlert.confirm('Badilisha hali ya user huyu (enable/disable)?');
    if (!result.isConfirmed) return;
    try {
        const result = await api.toggleUserActive(id);
        if (result && result.success === false) {
            SwalAlert.error(result.message || 'Unknown error');
            return;
        }
        renderUsers();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function deleteUser(id, name) {
    const result = await SwalAlert.confirm(`Futa user "${name}"? Hatua hii haiwezi kutenduliwa.`);
    if (!result.isConfirmed) return;
    try {
        const result = await api.deleteUser(id);
        if (result && result.success === false) {
            SwalAlert.error(result.message || 'Unknown error');
            return;
        }
        SwalAlert.success('User amefutwa.');
        renderUsers();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Users module loaded');
