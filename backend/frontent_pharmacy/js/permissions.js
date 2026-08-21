// ============================================
// PERMISSIONS MODULE
// ============================================

let permissionsData = null;
let permissionsModules = [];

async function renderPermissions() {
    const content = document.getElementById('pageContent');
    try {
        const result = await api.getAllPermissions();
        permissionsData = result?.data?.permissions || {};
        permissionsModules = result?.data?.modules || [];

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <h5 class="mb-0"><i class="fas fa-shield-alt me-2"></i>Role Permissions</h5>
                <button class="btn btn-primary" onclick="savePermissions()">
                    <i class="fas fa-save"></i> Save Changes
                </button>
            </div>
            <div class="table-container">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Module</th>
                            ${Object.keys(permissionsData).map(role => `
                                <th class="text-center text-uppercase">${role}</th>
                            `).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${permissionsModules.map(module => `
                            <tr>
                                <td class="text-capitalize">${module}</td>
                                ${Object.keys(permissionsData).map(role => {
                                    const checked = (permissionsData[role] || []).includes(module);
                                    const disabled = role === 'admin'; // admin always has everything
                                    return `<td class="text-center">
                                        <input type="checkbox" data-role="${role}" data-module="${module}"
                                            ${checked ? 'checked' : ''} ${disabled ? 'disabled' : ''}>
                                    </td>`;
                                }).join('')}
                            </tr>
                        `).join('') || '<tr><td colspan="3" class="text-center text-muted">No permissions data</td></tr>'}
                    </tbody>
                </table>
                <p class="text-muted small"><i class="fas fa-info-circle me-1"></i>Admin ina ruhusa zote kila wakati (haitobadilishwa).</p>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load permissions: ${error.message}</div>`;
    }
}

async function savePermissions() {
    const checkboxes = document.querySelectorAll('#pageContent input[type="checkbox"]:not(:disabled)');
    const byRole = {};
    checkboxes.forEach(cb => {
        if (cb.checked) {
            const role = cb.dataset.role;
            const module = cb.dataset.module;
            if (!byRole[role]) byRole[role] = [];
            byRole[role].push(module);
        }
    });

    try {
        for (const role of Object.keys(byRole)) {
            await api.updatePermissions({ role, modules: byRole[role] });
        }
        alert('Permissions saved successfully!');
        renderPermissions();
    } catch (error) {
        alert('Failed to save permissions: ' + error.message);
    }
}

console.log('Permissions module loaded');