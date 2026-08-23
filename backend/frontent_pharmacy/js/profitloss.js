// ============================================
// PROFIT & LOSS MODULE — Enhanced with Multi-Dataset Chart
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
                    <label class="form-label mb-0 fw-bold">Period:</label>
                    <select id="plPeriod" class="form-control" style="width:auto;" onchange="renderProfitLoss()">
                        <option value="today" ${period==='today'?'selected':''}>Today</option>
                        <option value="week" ${period==='week'?'selected':''}>This Week</option>
                        <option value="month" ${period==='month'?'selected':''}>This Month</option>
                        <option value="last_month" ${period==='last_month'?'selected':''}>Last Month</option>
                        <option value="3_months" ${period==='3_months'?'selected':''}>3 Months</option>
                        <option value="6_months" ${period==='6_months'?'selected':''}>6 Months</option>
                        <option value="year" ${period==='year'?'selected':''}>This Year</option>
                        <option value="5_years" ${period==='5_years'?'selected':''}>5 Years</option>
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
                <div class="col-12 col-lg-4"><div class="stat-card border-success"><div class="stat-info"><div class="stat-value ${d.net_profit >= 0 ? 'text-success' : 'text-danger'}">${formatMoney(d.net_profit)}</div><div class="stat-label">Net Profit</div></div></div></div>
                <div class="col-12 col-lg-4"><div class="stat-card"><div class="stat-info"><div class="stat-value">${d.margin_percent}%</div><div class="stat-label">Profit Margin</div></div></div></div>
                <div class="col-12 col-lg-4"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(d.discount)}</div><div class="stat-label">Discounts Given</div></div></div></div>
            </div>
            <div class="card mb-4">
                <div class="card-header"><i class="fas fa-chart-area me-2"></i>Profit & Loss Trend</div>
                <div class="card-body">
                    <div class="chart-box" style="height:350px;"><canvas id="plChart"></canvas></div>
                    <div class="d-flex gap-4 mt-3 justify-content-center flex-wrap">
                        <span><span style="display:inline-block;width:14px;height:14px;background:#2563eb;border-radius:3px;margin-right:6px;"></span>Revenue</span>
                        <span><span style="display:inline-block;width:14px;height:14px;background:#ef4444;border-radius:3px;margin-right:6px;"></span>Expenses</span>
                        <span><span style="display:inline-block;width:14px;height:14px;background:#10b981;border-radius:3px;margin-right:6px;"></span>Net Profit</span>
                    </div>
                </div>
            </div>
        `;

        const ctx = document.getElementById('plChart');
        if (ctx && window.Chart) {
            if (plChartInstance) plChartInstance.destroy();
            
            const months = d.monthly_revenue || [];
            const labels = months.map(m => m.month);
            
            const revenueData = months.map(m => m.amount || 0);
            
            const expensesData = months.map(m => {
                const monthStr = m.month;
                const mRevs = d.monthly_expenses || [];
                const match = mRevs.find(e => e.month === monthStr);
                return match ? match.amount : 0;
            });
            
            const profitData = months.map((m, i) => revenueData[i] - expensesData[i]);
            
            plChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Revenue',
                            data: revenueData,
                            backgroundColor: 'rgba(37, 99, 235, 0.7)',
                            borderColor: '#2563eb',
                            borderWidth: 1,
                            order: 2
                        },
                        {
                            label: 'Expenses',
                            data: expensesData,
                            backgroundColor: 'rgba(239, 68, 68, 0.7)',
                            borderColor: '#ef4444',
                            borderWidth: 1,
                            order: 3
                        },
                        {
                            label: 'Net Profit',
                            data: profitData,
                            type: 'line',
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            borderWidth: 3,
                            pointRadius: 5,
                            pointBackgroundColor: '#10b981',
                            fill: true,
                            tension: 0.3,
                            order: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + formatMoney(context.raw);
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    if (value >= 1000000) return 'TSh ' + (value / 1000000).toFixed(1) + 'M';
                                    if (value >= 1000) return 'TSh ' + (value / 1000).toFixed(0) + 'K';
                                    return 'TSh ' + value;
                                }
                            },
                            grid: { color: 'rgba(0,0,0,0.05)' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load P&L: ${error.message}</div>`;
    }
}

console.log('Profit & Loss module loaded');
