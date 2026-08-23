// ============================================
// EXPIRY MONITORING MODULE
// ============================================

let expiryChartInstance = null;

async function renderExpiry() {
    const content = document.getElementById('pageContent');
    const filter = document.getElementById('expiryFilter')?.value || 'all';
    try {
        const [dashRes, listRes] = await Promise.all([
            api.getExpiryDashboard(),
            api.getExpiryList({ status_filter: filter })
        ]);
        const d = dashRes.data;
        const counts = d.counts;
        const items = listRes.data.items || [];

        const statusBadge = (s) => {
            if (s === 'expired') return '<span class="badge bg-danger">Expired</span>';
            if (s === 'quarantined') return '<span class="badge bg-dark">Quarantined</span>';
            if (s === 'disposed') return '<span class="badge bg-secondary">Disposed</span>';
            if (s === 'returned') return '<span class="badge bg-info">Returned</span>';
            return '<span class="badge bg-success">Active</span>';
        };

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <div class="d-flex gap-2 align-items-center">
                    <label class="form-label mb-0">Filter:</label>
                    <select id="expiryFilter" class="form-control" style="width:auto;" onchange="renderExpiry()">
                        <option value="all">All</option>
                        <option value="expired">Expired</option>
                        <option value="critical">Critical (&lt;7d)</option>
                        <option value="expiring_soon">Expiring Soon (&lt;30d)</option>
                        <option value="safe">Safe</option>
                    </select>
                </div>
                <span class="text-muted">Expired value lost: <strong class="text-danger">${formatMoney(d.total_expired_value)}</strong></span>
            </div>
            <div class="row g-3 mb-4">
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-danger"><i class="fas fa-times-circle"></i></div><div class="stat-info"><div class="stat-value">${counts.expired}</div><div class="stat-label">Expired</div></div></div></div>
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-warning"><i class="fas fa-exclamation-triangle"></i></div><div class="stat-info"><div class="stat-value">${counts.critical}</div><div class="stat-label">Critical (&lt;7d)</div></div></div></div>
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-info"><i class="fas fa-hourglass-half"></i></div><div class="stat-info"><div class="stat-value">${counts.expiring_soon}</div><div class="stat-label">Expiring Soon</div></div></div></div>
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-success"><i class="fas fa-check-circle"></i></div><div class="stat-info"><div class="stat-value">${counts.safe}</div><div class="stat-label">Safe</div></div></div></div>
            </div>
            <div class="card mb-4"><div class="card-header"><i class="fas fa-chart-pie me-2"></i>Expiry Distribution</div><div class="card-body"><div class="chart-box"><canvas id="expiryChart"></canvas></div></div></div>
            <div class="table-container">
                <table class="table table-hover">
                    <thead>
                        <tr><th>Batch</th><th>Med ID</th><th>Qty</th><th>Expiry</th><th>Days Left</th><th>Stock Value</th><th>Status</th><th>Action</th></tr>
                    </thead>
                    <tbody>
                        ${items.map(it => `
                            <tr>
                                <td>${it.batch_no}</td>
                                <td>${it.medicine_id}</td>
                                <td>${it.quantity}</td>
                                <td>${it.expiry_date}</td>
                                <td class="${it.days_remaining < 0 ? 'text-danger' : it.days_remaining <= 7 ? 'text-warning' : ''}">${it.days_remaining}</td>
                                <td>${formatMoney(it.stock_value)}</td>
                                <td>${statusBadge(it.status)}</td>
                                <td>
                                    ${it.status === 'active' ? `<button class="btn btn-sm btn-outline-warning" onclick="openExpiryAction(${it.batch_id}, '${it.batch_no}', ${it.medicine_id}, '${(it.medicine_name || '').replace(/'/g, "\\'")}', '${it.expiry_date}', ${it.quantity})"><i class="fas fa-cog"></i> Action</button>` : '<span class="text-muted">-</span>'}
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="8" class="text-center text-muted">No batches found.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;

        const ctx = document.getElementById('expiryChart');
        if (ctx && window.Chart) {
            if (expiryChartInstance) expiryChartInstance.destroy();
            expiryChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Expired', 'Critical', 'Expiring Soon', 'Safe'],
                    datasets: [{ data: [counts.expired, counts.critical, counts.expiring_soon, counts.safe], backgroundColor: ['#dc3545', '#ffc107', '#0dcaf0', '#198754'] }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load expiry: ${error.message}</div>`;
    }
}

function openExpiryAction(batchId, batchNo, medicineId, medicineName, expiry, qty) {
    document.getElementById('exp_act_batch_id').value = batchId;
    document.getElementById('exp_act_batch_no').value = batchNo;
    document.getElementById('exp_act_medicine_id').value = medicineId;
    document.getElementById('exp_act_medicine_name').value = medicineName;
    document.getElementById('exp_act_expiry').value = expiry;
    document.getElementById('exp_act_qty').value = qty;
    document.getElementById('exp_act_info').innerHTML = `<strong>${batchNo}</strong> — Expiry: ${expiry} — Qty: ${qty}`;
    new bootstrap.Modal(document.getElementById('expiryActionModal')).show();
}

async function submitExpiryAction() {
    const data = {
        action_type: document.getElementById('exp_act_type').value,
        batch_id: parseInt(document.getElementById('exp_act_batch_id').value),
        batch_no: document.getElementById('exp_act_batch_no').value,
        medicine_id: parseInt(document.getElementById('exp_act_medicine_id').value),
        medicine_name: document.getElementById('exp_act_medicine_name').value,
        expiry_date: document.getElementById('exp_act_expiry').value || null,
        quantity: parseInt(document.getElementById('exp_act_qty').value),
        responsible_person: document.getElementById('exp_act_person').value || null,
        reason: document.getElementById('exp_act_reason').value || null
    };
    if (!data.quantity || data.quantity <= 0) {
        SwalAlert.warning('Weka kiasi sahihi!');
        return;
    }
    try {
        await api.createExpiryAction(data);
        bootstrap.Modal.getInstance(document.getElementById('expiryActionModal')).hide();
        renderExpiry();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Expiry module loaded');
