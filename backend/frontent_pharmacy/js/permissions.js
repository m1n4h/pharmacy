// ============================================
// PERMISSIONS MODULE — Granular RBAC
// ============================================

let permissionsData = {};
let permissionsModules = [];
let permissionTypes = ["read", "write", "delete", "*"];

async function renderPermissions() {
    const content = document.getElementById('pageContent');
    try {
        const result = await api.getAllPermissions();
        permissionsData = result?.data?.permissions || {};
        permissionsModules = result?.data?.modules || [];
        permissionTypes = result?.data?.permission_types || ["read", "write", "delete", "*"];
        const roles = Object.keys(permissionsData);

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <h5 class="mb-0"><i class="fas fa-shield-alt me-2"></i>Role Permissions</h5>
                <button class="btn btn-primary" onclick="savePermissions()">
                    <i class="fas fa-save"></i> Save Changes
                </button>
            </div>
            <div class="table-responsive">
                <table class="table table-bordered table-sm">
                    <thead>
                        <tr>
                            <th style="min-width:140px">Module</th>
                            ${roles.map(r => `<th class="text-center text-uppercase" style="min-width:90px">${r}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${permissionsModules.map(module => `
                            <tr>
                                <td class="text-capitalize fw-semibold">${module.replace(/_/g, ' ')}</td>
                                ${roles.map(role => {
                                    if (role === 'admin' || role === 'superadmin') {
                                        return `<td class="text-center"><span class="badge bg-success">ALL</span></td>`;
                                    }
                                    const perm = (permissionsData[role] || {})[module] || '-';
                                    return `<td class="text-center">
                                        <select class="form-select form-select-sm perm-select"
                                                data-role="${role}" data-module="${module}"
                                                style="width:auto;margin:auto;font-size:0.75rem">
                                            <option value="" ${perm === '-' ? 'selected' : ''}>-</option>
                                            <option value="read" ${perm === 'read' ? 'selected' : ''}>Read</option>
                                            <option value="write" ${perm === 'write' ? 'selected' : ''}>Write</option>
                                            <option value="delete" ${perm === 'delete' ? 'selected' : ''}>Delete</option>
                                            <option value="*" ${perm === '*' ? 'selected' : ''}>All (*)</option>
                                        </select>
                                    </td>`;
                                }).join('')}
                            </tr>
                        `).join('') || '<tr><td colspan="' + (roles.length + 1) + '" class="text-center text-muted">No modules found</td></tr>'}
                    </tbody>
                </table>
            </div>
            <p class="text-muted small"><i class="fas fa-info-circle me-1"></i>admin / superadmin roles always have ALL permissions (cannot be changed).</p>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load permissions: ${error.message}</div>`;
    }
}

async function savePermissions() {
    const selects = document.querySelectorAll('.perm-select');
    const byRole = {};
    selects.forEach(sel => {
        const role = sel.dataset.role;
        const module = sel.dataset.module;
        const permType = sel.value;
        if (permType && role !== 'admin' && role !== 'superadmin') {
            if (!byRole[role]) byRole[role] = {};
            byRole[role][module] = permType;
        }
    });

    try {
        for (const role of Object.keys(byRole)) {
            await api.updatePermissions({ role, permissions: byRole[role] });
        }
        SwalAlert.success('Permissions saved successfully!');
        await renderPermissions();
    } catch (error) {
        SwalAlert.error('Failed to save permissions: ' + (error.message || ''));
    }
}

console.log('Permissions module loaded');
