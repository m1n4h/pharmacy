// ============================================
// DASHBOARD MODULE
// ============================================

let chartInstance = null;

async function renderDashboard() {
    console.log('Rendering dashboard...');
    const content = document.getElementById('pageContent');
    
    try {
        const [totals, today, inventory] = await Promise.all([
            api.getDashboardTotals(),
            api.getDashboardToday(),
            api.getDashboardInventory()
        ]);
        
        console.log('Dashboard data:', { totals, today, inventory });
        
        content.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${totals.total_medicines || 0}</div>
                    <div class="stat-label">Total Medicines</div>
                </div>
                <div class="stat-card border-mint">
                    <div class="stat-value">${totals.total_batches || 0}</div>
                    <div class="stat-label">Total Batches</div>
                </div>
                <div class="stat-card border-orange">
                    <div class="stat-value">${totals.total_sales || 0}</div>
                    <div class="stat-label">Total Sales</div>
                </div>
                <div class="stat-card border-red">
                    <div class="stat-value">${inventory.low_stock_count || 0}</div>
                    <div class="stat-label">Low Stock Items</div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="table-container">
                        <h6><i class="fas fa-calendar-day me-2"></i>Today's Summary</h6>
                        <div class="row mt-3">
                            <div class="col-6">
                                <small class="text-muted">Revenue</small>
                                <h4>${formatMoney(today.today_revenue || 0)}</h4>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Invoices</small>
                                <h4>${today.today_invoices || 0}</h4>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-6">
                                <small class="text-muted">Items Sold</small>
                                <h4>${today.today_items_sold || 0}</h4>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Purchases</small>
                                <h4>${formatMoney(today.today_purchases || 0)}</h4>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="table-container">
                        <h6><i class="fas fa-clock me-2"></i>Quick Actions</h6>
                        <div class="d-flex gap-2 mt-3 flex-wrap">
                            <button class="btn btn-primary btn-sm" onclick="navigateTo('sales'); openSaleModal();">
                                <i class="fas fa-plus"></i> New Sale
                            </button>
                            <button class="btn btn-success btn-sm" onclick="navigateTo('purchases'); openPurchaseModal();">
                                <i class="fas fa-plus"></i> New Purchase
                            </button>
                            <button class="btn btn-info btn-sm" onclick="navigateTo('medicines'); openAddMedicineModal();">
                                <i class="fas fa-plus"></i> Add Medicine
                            </button>
                            <button class="btn btn-warning btn-sm" onclick="navigateTo('suppliers'); openAddSupplierModal();">
                                <i class="fas fa-plus"></i> Add Supplier
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-8">
                    <div class="table-container">
                        <h6><i class="fas fa-chart-line me-2"></i>Sales Trend (Last 7 Days)</h6>
                        <div class="chart-box"><canvas id="salesChart"></canvas></div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="table-container">
                        <h6><i class="fas fa-exclamation-circle me-2"></i>Low Stock Alerts</h6>
                        <div id="lowStockList"><p class="text-muted text-center">Loading...</p></div>
                    </div>
                </div>
            </div>
        `;
        
        await loadLowStock();
        await initChart();
        console.log('Dashboard rendered');
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

async function loadLowStock() {
    const container = document.getElementById('lowStockList');
    if (!container) return;
    
    try {
        const items = await api.getLowStock();
        if (items && items.length > 0) {
            container.innerHTML = items.slice(0, 5).map(item => `
                <div class="d-flex justify-content-between border-bottom py-2">
                    <span>${item.medicine_name || item.name || 'Unknown'}</span>
                    <span class="badge badge-danger">${item.quantity || 0} left</span>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="fas fa-check-circle text-success"></i>
                    <p class="mb-0">All items well stocked!</p>
                </div>
            `;
        }
    } catch (e) {
        container.innerHTML = '<p class="text-muted text-center">Unable to load</p>';
    }
}

async function initChart() {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;
    if (chartInstance) chartInstance.destroy();
    
    try {
        const data = await api.getSalesReportLast7Days();
        const labels = data.map(d => d.date || '');
        const values = data.map(d => d.amount || 0);
        
        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.length ? labels : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Sales ($)',
                    data: values.length ? values : [1200, 1900, 1500, 2100, 1800, 2400, 2200],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37,99,235,0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#2563eb',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    } catch (e) {
        console.error('Chart error:', e);
    }
}

console.log('Dashboard module loaded');
