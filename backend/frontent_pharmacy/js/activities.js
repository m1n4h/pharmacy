// ============================================
// ACTIVITIES LOG MODULE
// ============================================

async function renderActivities() {
    const content = document.getElementById('pageContent');
    try {
        const result = await api.getActivities(1, 100);
        const activities = result?.data?.items || [];

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <h5 class="mb-0"><i class="fas fa-history me-2"></i>System Activities</h5>
                <button class="btn btn-outline-primary btn-sm" onclick="renderActivities()">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
            </div>
            <div class="table-container">
                <table class="table table-hover table-sm">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>User</th>
                            <th>Action</th>
                            <th>Module</th>
                            <th>Details</th>
                            <th>IP</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${activities.map(a => `
                            <tr>
                                <td>${new Date(a.created_at).toLocaleString()}</td>
                                <td>${a.user_email}</td>
                                <td><span class="badge bg-primary">${a.action}</span></td>
                                <td><span class="badge bg-secondary">${a.module}</span></td>
                                <td>${a.details || ''}</td>
                                <td><small>${a.ip_address}</small></td>
                            </tr>
                        `).join('') || '<tr><td colspan="6" class="text-center text-muted">No activities recorded</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load activities: ${error.message}</div>`;
    }
}

console.log('Activities module loaded');