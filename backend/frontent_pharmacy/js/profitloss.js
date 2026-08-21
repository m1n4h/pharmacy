// ============================================
// PROFIT & LOSS MODULE
// ============================================

let plChartInstance = null;

async function renderProfitLoss() {
    const content = document.getElementById('pageContent');
    const period = document.getElementById('plPeriod')?.value || 'month';
    try {
        const res = await api.getProfitLoss({ period });
        const d = res.data;

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <div class="d-flex gap-2 align-items-center">
                    <label class="form-label mb-0">Period:</label>
                    <select id="plPeriod" class="form-control" style="width:auto;" onchange="renderProfitLoss()">
                        <option value="today">Today</option>
                        <option value="week">This Week</option>
                        <option value="month" selected>This Month</option>
                        <option value="last_month">Last Month</option>
                        <option value="year">This Year</option>
                    </select>
                </div>
                <span class="text-muted">${d.period.from} → ${d.period.to}</span>
            </div>
            <div class="row g-3 mb-4">
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-primary"><i class="fas fa-coins"></i></div><div class="stat-info"><div class="stat-value">${formatMoney(d.revenue)}</div><div class="stat-label">Revenue</div></div></div></div>
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-info"><i class="fas fa-boxes"></i></div><div class="stat-info"><div class="stat-value">${formatMoney(d.cogs)}</div><div class="stat-label">COGS</div></div></div></div>
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-success"><i class="fas fa-chart-line"></i></div><div class="stat-info"><div class="stat-value">${formatMoney(d.gross_profit)}</div><div class="stat-label">Gross Profit</div></div></div></div>
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-secondary"><i class="fas fa-receipt"></i></div><div class="stat-info"><div class="stat-value">${formatMoney(d.expenses)}</div><div class="stat-label">Expenses</div></div></div></div>
            </div>
            <div class="row g-3 mb-4">
                <div class="col-12 col-lg-4"><div class="stat-card border-success"><div class="stat-info"><div class="stat-value text-success">${formatMoney(d.net_profit)}</div><div class="stat-label">Net Profit</div></div></div></div>
                <div class="col-12 col-lg-4"><div class="stat-card"><div class="stat-info"><div class="stat-value">${d.margin_percent}%</div><div class="stat-label">Profit Margin</div></div></div></div>
                <div class="col-12 col-lg-4"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(d.discount)}</div><div class="stat-label">Discounts Given</div></div></div></div>
            </div>
            <div class="card"><div class="card-header"><i class="fas fa-chart-area me-2"></i>Monthly Revenue</div><div class="card-body"><div class="chart-box"><canvas id="plChart"></canvas></div></div></div>
        `;

        const ctx = document.getElementById('plChart');
        if (ctx && window.Chart) {
            if (plChartInstance) plChartInstance.destroy();
            plChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: (d.monthly_revenue || []).map(m => m.month),
                    datasets: [{ label: 'Revenue (TZS)', data: (d.monthly_revenue || []).map(m => m.amount), backgroundColor: '#0d6efd' }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load P&L: ${error.message}</div>`;
    }
}

console.log('Profit & Loss module loaded');
