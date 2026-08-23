// ============================================
// BACKUP & RESTORE MODULE
// ============================================

async function renderBackup() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="row g-3 mb-4">
            <div class="col-12 col-md-4">
                <div class="stat-card"><div class="stat-icon bg-primary"><i class="fas fa-database"></i></div>
                <div class="stat-info"><div class="stat-value">Local DB</div><div class="stat-label">pharmacy_db</div></div></div>
            </div>
        </div>
        <div class="d-flex gap-2 mb-4 flex-wrap">
            <button class="btn btn-success" onclick="createBackup()"><i class="fas fa-download me-2"></i>Create Backup Now</button>
        </div>
        <div class="card"><div class="card-header"><i class="fas fa-history me-2"></i>Available Backups</div>
        <div class="card-body"><div class="table-container"><table class="table table-hover">
            <thead><tr><th>Filename</th><th>Created</th><th>Size</th><th>Action</th></tr></thead>
            <tbody id="backupListBody"><tr><td colspan="4" class="text-center text-muted">Loading...</td></tr></tbody>
        </table></div></div></div>
    `;
    await loadBackups();
}

async function loadBackups() {
    const body = document.getElementById('backupListBody');
    try {
        const res = await api.listBackups();
        const items = res.data || [];
        body.innerHTML = items.length ? items.map(b => `
            <tr>
                <td>${b.filename}</td>
                <td>${b.created_at ? b.created_at.replace('T', ' ') : '-'}</td>
                <td>${(b.size / 1024).toFixed(1)} KB</td>
                <td><button class="btn btn-sm btn-outline-primary" onclick="restoreBackup('${b.filename}')"><i class="fas fa-upload"></i> Restore</button></td>
            </tr>
        `).join('') : '<tr><td colspan="4" class="text-center text-muted">No backups yet.</td></tr>';
    } catch (e) {
        body.innerHTML = `<tr><td colspan="4" class="text-danger">Failed to load: ${e.message}</td></tr>`;
    }
}

async function createBackup() {
    const result = await SwalAlert.confirm('Unda backup mpya ya database?');
    if (!result.isConfirmed) return;
    try {
        const res = await api.createBackup();
        if (res.success === false) { SwalAlert.error(res.error || res.message); return; }
        SwalAlert.success('Backup imeundwa!');
        loadBackups();
    } catch (e) {
        SwalAlert.error(e.message);
    }
}

async function restoreBackup(filename) {
    const result = await SwalAlert.confirm(`Rejesha database kutoka "${filename}"? Hii itafuta data ya sasa kabisa!`);
    if (!result.isConfirmed) return;
    try {
        const res = await api.restoreBackup(filename);
        if (res.success === false) { SwalAlert.error(res.error || res.message); return; }
        SwalAlert.success('Restore imefanikiwa! Ingia tena.');
    } catch (e) {
        SwalAlert.error(e.message);
    }
}

console.log('Backup module loaded');
