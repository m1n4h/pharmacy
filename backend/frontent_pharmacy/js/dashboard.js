// ============================================
// DASHBOARD MODULE — Pharmacy Monitoring System
// Answers: What is happening in my pharmacy?
// ============================================

let dashChartInstance = null;

async function renderDashboard() {
    const content = document.getElementById('pageContent');
    
    try {
        content.innerHTML = `
            <div class="page-header">
                <div>
                    <h4 style="margin:0;"><i class="fas fa-chart-line me-2"></i>Pharmacy Dashboard</h4>
                    <p class="mb-0">Business overview at a glance</p>
                </div>
                <div class="dash-quick-actions">
                    <button class="btn btn-primary btn-sm" onclick="navigateTo('sales'); setTimeout(()=>openSaleModal(),300);">
                        <i class="fas fa-plus me-1"></i>New Sale
                    </button>
                    <button class="btn btn-success btn-sm" onclick="navigateTo('purchases'); setTimeout(()=>openPurchaseModal(),300);">
                        <i class="fas fa-plus me-1"></i>New Purchase
                    </button>
                    <button class="btn btn-info btn-sm" onclick="navigateTo('reports')">
                        <i class="fas fa-file-alt me-1"></i>Reports
                    </button>
                </div>
            </div>
            <div id="dashContent"><p class="text-center text-muted py-5"><i class="fas fa-spinner fa-spin fa-2x"></i><br>Loading dashboard data...</p></div>
        `;

        const [grand, today, inventory, profitLoss, topSelling, expiry, expenses] = await Promise.allSettled([
            api.getDashboardTotals(),
            api.getDashboardToday(),
            api.getDashboardInventory(),
            api.getProfitLoss({ period: 'month' }),
            api.getTopSelling({ period: 'month', limit: 5 }),
            api.getExpiryDashboard(),
            api.getExpenseTrending({ period: 'month' })
        ]);

        const g = grand.status === 'fulfilled' ? grand.value : {};
        const t = today.status === 'fulfilled' ? today.value : {};
        const inv = inventory.status === 'fulfilled' ? inventory.value : {};
        const pl = profitLoss.status === 'fulfilled' ? (profitLoss.value?.data || {}) : {};
        const top = topSelling.status === 'fulfilled' ? (topSelling.value?.data || {}) : {};
        const exp = expiry.status === 'fulfilled' ? (expiry.value?.data || {}) : {};
        const trending = expenses.status === 'fulfilled' ? (expenses.value?.data || {}) : {};

        const totalStockValue = inv.total_stock_value || 0;
        const nearExpiryCount = (inv.near_expiry || []).length;
        const lowStockCount = inv.low_stock_count || 0;
        const lowStockItems = inv.low_stock || [];
        const expiredCount = exp.counts?.expired || 0;
        const criticalCount = exp.counts?.critical || 0;
        const expiringCount = exp.counts?.expiring_soon || 0;
        const topItems = top.items || [];
        const expenseCategories = trending.by_category || [];

        content.querySelector('#dashContent').innerHTML = `
            <!-- ROW 1: TODAY'S PERFORMANCE -->
            <div class="stats-grid mb-4">
                <div class="stat-card">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon bg-primary"><i class="fas fa-receipt"></i></div>
                        <div class="stat-info">
                            <div class="stat-value">${t.today_invoices || 0}</div>
                            <div class="stat-label">Today's Sales</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card border-mint">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon bg-success"><i class="fas fa-coins"></i></div>
                        <div class="stat-info">
                            <div class="stat-value">${formatMoney(t.today_revenue || 0)}</div>
                            <div class="stat-label">Today's Revenue</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card border-orange">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon bg-info"><i class="fas fa-shopping-cart"></i></div>
                        <div class="stat-info">
                            <div class="stat-value">${formatMoney(t.today_purchases || 0)}</div>
                            <div class="stat-label">Today's Purchases</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card border-success">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon" style="background:${(t.today_profit || 0) >= 0 ? '#059669' : '#dc2626'}">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value" style="color:${(t.today_profit || 0) >= 0 ? 'var(--mint-green)' : 'var(--soft-red)'}">${formatMoney(t.today_profit || 0)}</div>
                            <div class="stat-label">Today's Profit</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ROW 2: MONTHLY P&L SUMMARY -->
            <div class="stats-grid-3 mb-4">
                <div class="stat-card">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon bg-primary"><i class="fas fa-coins"></i></div>
                        <div class="stat-info">
                            <div class="stat-value">${formatMoney(pl.revenue || 0)}</div>
                            <div class="stat-label">Monthly Revenue</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon bg-danger"><i class="fas fa-receipt"></i></div>
                        <div class="stat-info">
                            <div class="stat-value">${formatMoney(pl.expenses || 0)}</div>
                            <div class="stat-label">Monthly Expenses</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card border-success">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon" style="background:${(pl.net_profit || 0) >= 0 ? '#059669' : '#dc2626'}">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value" style="color:${(pl.net_profit || 0) >= 0 ? 'var(--mint-green)' : 'var(--soft-red)'}">${formatMoney(pl.net_profit || 0)}</div>
                            <div class="stat-label">Net Profit (${pl.margin_percent || 0}% margin)</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ROW 3: ALL-TIME TOTALS -->
            <div class="stats-grid mb-4">
                <div class="stat-card">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon bg-primary"><i class="fas fa-pills"></i></div>
                        <div class="stat-info">
                            <div class="stat-value">${g.total_medicines || 0}</div>
                            <div class="stat-label">Total Medicines</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card border-mint">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon bg-success"><i class="fas fa-coins"></i></div>
                        <div class="stat-info">
                            <div class="stat-value">${formatMoney(g.total_revenue || 0)}</div>
                            <div class="stat-label">All-Time Revenue</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card border-orange">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon bg-info"><i class="fas fa-shopping-cart"></i></div>
                        <div class="stat-info">
                            <div class="stat-value">${g.total_sales || 0}</div>
                            <div class="stat-label">Total Transactions</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card border-success">
                    <div class="d-flex align-items-center gap-3">
                        <div class="stat-icon" style="background:${(g.total_profit || 0) >= 0 ? '#059669' : '#dc2626'}">
                            <i class="fas fa-hand-holding-usd"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value" style="color:${(g.total_profit || 0) >= 0 ? 'var(--mint-green)' : 'var(--soft-red)'}">${formatMoney(g.total_profit || 0)}</div>
                            <div class="stat-label">All-Time Profit</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ROW 4: SALES TREND CHART + TOP SELLING -->
            <div class="row g-3 mb-4">
                <div class="col-lg-8">
                    <div class="dash-section">
                        <div class="dash-section-header"><i class="fas fa-chart-area"></i>Sales Trend (Last 7 Days)</div>
                        <div class="dash-section-body">
                            <div class="chart-box" style="height:280px;"><canvas id="salesTrendChart"></canvas></div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="dash-section">
                        <div class="dash-section-header"><i class="fas fa-trophy"></i>Top Selling Medicines</div>
                        <div class="dash-section-body" style="padding:0;">
                            ${topItems.length ? topItems.map((m, i) => `
                                <div class="dash-alert-item">
                                    <div class="alert-left">
                                        <span style="width:24px;height:24px;border-radius:50%;background:${i < 3 ? '#2563eb' : '#475569'};color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:700;flex-shrink:0;">${i + 1}</span>
                                        <div>
                                            <div class="alert-name">${m.name}</div>
                                            <div class="alert-meta">${m.quantity_sold} sold &middot; ${m.transactions} txns</div>
                                        </div>
                                    </div>
                                    <span class="badge bg-success">${formatMoney(m.revenue)}</span>
                                </div>
                            `).join('') : '<div class="text-center text-muted py-3">No sales data yet</div>'}
                        </div>
                    </div>
                </div>
            </div>

            <!-- ROW 5: ALERTS — Low Stock + Expiry -->
            <div class="row g-3 mb-4">
                <div class="col-lg-4">
                    <div class="dash-section">
                        <div class="dash-section-header">
                            <i class="fas fa-exclamation-triangle" style="color:var(--soft-orange);"></i>
                            Low Stock Alerts
                            ${lowStockCount > 0 ? `<span class="badge bg-warning ms-auto">${lowStockCount}</span>` : ''}
                        </div>
                        <div class="dash-section-body" style="padding:0;max-height:280px;overflow-y:auto;">
                            ${lowStockItems.length ? lowStockItems.slice(0, 8).map(item => `
                                <div class="dash-alert-item">
                                    <div class="alert-left">
                                        <span class="alert-dot" style="background:${item.quantity <= 3 ? 'var(--soft-red)' : 'var(--soft-orange)'}"></span>
                                        <div>
                                            <div class="alert-name">${item.medicine_name || 'Unknown'}</div>
                                            <div class="alert-meta">${item.quantity} units remaining</div>
                                        </div>
                                    </div>
                                    <span class="badge ${item.quantity <= 3 ? 'bg-danger' : 'bg-warning'}">${item.quantity <= 3 ? 'Critical' : 'Low'}</span>
                                </div>
                            `).join('') : '<div class="text-center text-muted py-3"><i class="fas fa-check-circle text-success"></i><p class="mb-0 mt-2">All items well stocked</p></div>'}
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="dash-section">
                        <div class="dash-section-header">
                            <i class="fas fa-clock" style="color:var(--soft-red);"></i>
                            Expiry Alerts
                            ${(expiredCount + criticalCount + expiringCount) > 0 ? `<span class="badge bg-danger ms-auto">${expiredCount + criticalCount + expiringCount}</span>` : ''}
                        </div>
                        <div class="dash-section-body" style="padding:0;max-height:280px;overflow-y:auto;">
                            ${expiredCount > 0 ? `
                                <div class="dash-alert-item" style="background:rgba(239,68,68,0.05);">
                                    <div class="alert-left">
                                        <span class="alert-dot" style="background:var(--soft-red)"></span>
                                        <div>
                                            <div class="alert-name" style="color:var(--soft-red);font-weight:600;">${expiredCount} Expired Batches</div>
                                            <div class="alert-meta">Need immediate action</div>
                                        </div>
                                    </div>
                                    <span class="badge bg-danger">Expired</span>
                                </div>
                            ` : ''}
                            ${criticalCount > 0 ? `
                                <div class="dash-alert-item" style="background:rgba(245,158,11,0.05);">
                                    <div class="alert-left">
                                        <span class="alert-dot" style="background:var(--soft-orange)"></span>
                                        <div>
                                            <div class="alert-name" style="color:var(--soft-orange);font-weight:600;">${criticalCount} Critical (&lt;7 days)</div>
                                            <div class="alert-meta">Expiring this week</div>
                                        </div>
                                    </div>
                                    <span class="badge bg-warning">Critical</span>
                                </div>
                            ` : ''}
                            ${expiringCount > 0 ? `
                                <div class="dash-alert-item" style="background:rgba(37,99,235,0.05);">
                                    <div class="alert-left">
                                        <span class="alert-dot" style="background:var(--medical-blue)"></span>
                                        <div>
                                            <div class="alert-name">${expiringCount} Expiring Soon (&lt;30 days)</div>
                                            <div class="alert-meta">Review and plan</div>
                                        </div>
                                    </div>
                                    <span class="badge bg-info">Warning</span>
                                </div>
                            ` : ''}
                            ${!expiredCount && !criticalCount && !expiringCount ? '<div class="text-center text-muted py-3"><i class="fas fa-check-circle text-success"></i><p class="mb-0 mt-2">No expiry concerns</p></div>' : ''}
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="dash-section">
                        <div class="dash-section-header">
                            <i class="fas fa-money-bill-trend-up" style="color:var(--medical-blue);"></i>
                            Expense Breakdown
                            ${expenseCategories.length ? `<span class="badge bg-primary ms-auto">TSh ${formatMoney(trending.total || 0).replace('TSh ','')}</span>` : ''}
                        </div>
                        <div class="dash-section-body" style="padding:0;max-height:280px;overflow-y:auto;">
                            ${expenseCategories.length ? expenseCategories.slice(0, 6).map((c, i) => {
                                const pct = trending.total > 0 ? Math.round(c.amount / trending.total * 100) : 0;
                                return `
                                <div class="dash-alert-item">
                                    <div class="alert-left">
                                        <span style="width:24px;height:24px;border-radius:6px;background:${['#2563eb','#059669','#f59e0b','#ef4444','#8b5cf6','#06b6d4'][i % 6]};color:#fff;display:flex;align-items:center;justify-content:center;font-size:0.65rem;font-weight:700;flex-shrink:0;">${pct}%</span>
                                        <div>
                                            <div class="alert-name">${c.category}</div>
                                            <div class="alert-meta">${pct}% of total expenses</div>
                                        </div>
                                    </div>
                                    <span class="badge bg-secondary">${formatMoney(c.amount)}</span>
                                </div>`;
                            }).join('') : '<div class="text-center text-muted py-3"><i class="fas fa-receipt"></i><p class="mb-0 mt-2">No expenses recorded</p></div>'}
                        </div>
                    </div>
                </div>
            </div>

            <!-- ROW 6: STOCK VALUE + DEAD STOCK + PURCHASES BY SUPPLIER -->
            <div class="row g-3 mb-4">
                <div class="col-lg-4">
                    <div class="dash-section">
                        <div class="dash-section-header"><i class="fas fa-boxes-stacked"></i>Stock Summary</div>
                        <div class="dash-section-body">
                            <div class="d-flex justify-content-between align-items-center mb-3 pb-3" style="border-bottom:1px solid var(--border-light);">
                                <div>
                                    <div class="stat-label mb-1">Total Stock Value</div>
                                    <div class="stat-value" style="font-size:1.3rem;">${formatMoney(totalStockValue)}</div>
                                </div>
                                <div class="stat-icon bg-primary" style="width:44px;height:44px;font-size:1rem;"><i class="fas fa-boxes-stacked"></i></div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mb-3 pb-3" style="border-bottom:1px solid var(--border-light);">
                                <div>
                                    <div class="stat-label mb-1">Total Medicines</div>
                                    <div class="stat-value" style="font-size:1.3rem;">${g.total_medicines || 0}</div>
                                </div>
                                <div class="stat-icon bg-info" style="width:44px;height:44px;font-size:1rem;"><i class="fas fa-pills"></i></div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <div class="stat-label mb-1">Total Batches</div>
                                    <div class="stat-value" style="font-size:1.3rem;">${g.total_batches || 0}</div>
                                </div>
                                <div class="stat-icon bg-warning" style="width:44px;height:44px;font-size:1rem;"><i class="fas fa-layer-group"></i></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="dash-section">
                        <div class="dash-section-header"><i class="fas fa-calendar-day" style="color:var(--mint-green);"></i>Today's Breakdown</div>
                        <div class="dash-section-body">
                            <div class="d-flex justify-content-between align-items-center mb-3 pb-3" style="border-bottom:1px solid var(--border-light);">
                                <div>
                                    <div class="stat-label mb-1">Invoices</div>
                                    <div class="stat-value" style="font-size:1.3rem;">${t.today_invoices || 0}</div>
                                </div>
                                <div class="stat-icon bg-primary" style="width:44px;height:44px;font-size:1rem;"><i class="fas fa-file-invoice"></i></div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mb-3 pb-3" style="border-bottom:1px solid var(--border-light);">
                                <div>
                                    <div class="stat-label mb-1">Items Sold</div>
                                    <div class="stat-value" style="font-size:1.3rem;">${t.today_items_sold || 0}</div>
                                </div>
                                <div class="stat-icon bg-success" style="width:44px;height:44px;font-size:1rem;"><i class="fas fa-shopping-bag"></i></div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <div class="stat-label mb-1">Average Sale</div>
                                    <div class="stat-value" style="font-size:1.3rem;">${(t.today_invoices || 0) > 0 ? formatMoney((t.today_revenue || 0) / t.today_invoices) : formatMoney(0)}</div>
                                </div>
                                <div class="stat-icon bg-info" style="width:44px;height:44px;font-size:1rem;"><i class="fas fa-calculator"></i></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="dash-section">
                        <div class="dash-section-header"><i class="fas fa-hand-holding-usd" style="color:var(--soft-orange);"></i>Key Metrics</div>
                        <div class="dash-section-body">
                            <div class="d-flex justify-content-between align-items-center mb-3 pb-3" style="border-bottom:1px solid var(--border-light);">
                                <div>
                                    <div class="stat-label mb-1">COGS</div>
                                    <div class="stat-value" style="font-size:1.3rem;">${formatMoney(pl.cogs || 0)}</div>
                                </div>
                                <div class="stat-icon bg-secondary" style="width:44px;height:44px;font-size:1rem;"><i class="fas fa-box"></i></div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mb-3 pb-3" style="border-bottom:1px solid var(--border-light);">
                                <div>
                                    <div class="stat-label mb-1">Discounts Given</div>
                                    <div class="stat-value" style="font-size:1.3rem;">${formatMoney(pl.discount || 0)}</div>
                                </div>
                                <div class="stat-icon bg-warning" style="width:44px;height:44px;font-size:1rem;"><i class="fas fa-percent"></i></div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <div class="stat-label mb-1">Profit Margin</div>
                                    <div class="stat-value" style="font-size:1.3rem;color:${(pl.margin_percent || 0) >= 0 ? 'var(--mint-green)' : 'var(--soft-red)'};">${pl.margin_percent || 0}%</div>
                                </div>
                                <div class="stat-icon" style="width:44px;height:44px;font-size:1rem;background:${(pl.margin_percent || 0) >= 0 ? '#059669' : '#dc2626'};"><i class="fas fa-chart-pie"></i></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        await initDashChart();
    } catch (error) {
        console.error('Dashboard error:', error);
        content.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i>
                Failed to load dashboard: ${error.message}
            </div>
        `;
    }
}

async function initDashChart() {
    const ctx = document.getElementById('salesTrendChart');
    if (!ctx) return;
    if (dashChartInstance) dashChartInstance.destroy();
    
    try {
        const data = await api.getSalesReportLast7Days();
        const labels = data.map(d => {
            if (!d.date) return '';
            const dt = new Date(d.date);
            return dt.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        });
        const values = data.map(d => d.amount || 0);
        
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
        const textColor = isDark ? '#94a3b8' : '#6b7280';
        
        dashChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.length ? labels : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Sales (TSh)',
                    data: values.length ? values : [0, 0, 0, 0, 0, 0, 0],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37,99,235,0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#2563eb',
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'TSh ' + (context.raw || 0).toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: textColor,
                            callback: function(value) {
                                if (value >= 1000000) return 'TSh ' + (value / 1000000).toFixed(1) + 'M';
                                if (value >= 1000) return 'TSh ' + (value / 1000).toFixed(0) + 'K';
                                return 'TSh ' + value;
                            }
                        },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { display: false }
                    }
                }
            }
        });
    } catch (e) {
        console.error('Dashboard chart error:', e);
    }
}

console.log('Dashboard module loaded');
