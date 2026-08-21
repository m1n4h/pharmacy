// ============================================
// DASHBOARD MODULE
// ============================================

let chartInstance = null;

// Render dashboard
async function renderDashboard() {
    const content = document.getElementById('pageContent');
    
    try {
        // Fetch dashboard data
        const [totals, today, inventory] = await Promise.all([
            api.getDashboardTotals(),
            api.getDashboardToday(),
            api.getDashboardInventory()
        ]);
        
        // Build dashboard HTML
        content.innerHTML = `
            <!-- Stats Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon" style="background: #dbeafe; color: #2563eb;">
                        <i class="fas fa-capsules"></i>
                    </div>
                    <div class="stat-value">${totals.total_medicines || 0}</div>
                    <div class="stat-label">Total Medicines</div>
                </div>
                <div class="stat-card border-mint">
                    <div class="stat-icon" style="background: #d1fae5; color: #10b981;">
                        <i class="fas fa-box"></i>
                    </div>
                    <div class="stat-value">${totals.total_batches || 0}</div>
                    <div class="stat-label">Total Batches</div>
                </div>
                <div class="stat-card border-orange">
                    <div class="stat-icon" style="background: #fef3c7; color: #f59e0b;">
                        <i class="fas fa-shopping-cart"></i>
                    </div>
                    <div class="stat-value">${totals.total_sales || 0}</div>
                    <div class="stat-label">Total Sales</div>
                </div>
                <div class="stat-card border-red">
                    <div class="stat-icon" style="background: #fee2e2; color: #ef4444;">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="stat-value">${inventory.low_stock_count || 0}</div>
                    <div class="stat-label">Low Stock Items</div>
                </div>
            </div>

            <!-- Today's Summary -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="table-container">
                        <h6 class="mb-3"><i class="fas fa-calendar-day me-2"></i>Today's Summary</h6>
                        <div class="row">
                            <div class="col-6">
                                <p class="text-muted small mb-0">Revenue Today</p>
                                <h4>$${today.today_revenue || 0}</h4>
                            </div>
                            <div class="col-6">
                                <p class="text-muted small mb-0">Invoices</p>
                                <h4>${today.today_invoices || 0}</h4>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="table-container">
                        <h6 class="mb-3"><i class="fas fa-clock me-2"></i>Quick Actions</h6>
                        <div class="d-flex gap-2 flex-wrap">
                            <button class="btn btn-primary btn-sm" onclick="navigateTo('sales')">
                                <i class="fas fa-plus"></i> New Sale
                            </button>
                            <button class="btn btn-success btn-sm" onclick="navigateTo('purchases')">
                                <i class="fas fa-plus"></i> New Purchase
                            </button>
                            <button class="btn btn-info btn-sm" onclick="navigateTo('medicines')">
                                <i class="fas fa-plus"></i> Add Medicine
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="row">
                <div class="col-md-8">
                    <div class="table-container">
                        <h6 class="mb-3"><i class="fas fa-chart-line me-2"></i>Sales Trend</h6>
                        <canvas id="salesChart" height="200"></canvas>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="table-container">
                        <h6 class="mb-3"><i class="fas fa-exclamation-circle me-2"></i>Low Stock Alerts</h6>
                        <div id="lowStockList">
                            <p class="text-muted text-center">Loading...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Load low stock items
        await loadLowStockItems();
        
        // Initialize chart
        initializeChart();
        
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

// Load low stock items
async function loadLowStockItems() {
    const container = document.getElementById('lowStockList');
    if (!container) return;
    
    try {
        const lowStock = await api.getLowStock();
        
        if (lowStock && lowStock.length > 0) {
            container.innerHTML = lowStock.slice(0, 5).map(item => `
                <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                    <span>${item.medicine_name || item.name || 'Unknown'}</span>
                    <span class="badge badge-danger">${item.quantity || 0} left</span>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="fas fa-check-circle text-success"></i>
                    <p class="mb-0">All items are well stocked!</p>
                </div>
            `;
        }
    } catch (error) {
        container.innerHTML = `
            <p class="text-muted text-center">Unable to load low stock items</p>
        `;
    }
}

// Initialize chart
function initializeChart() {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    // Sample data - in production, fetch from API
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const data = [1200, 1900, 1500, 2100, 1800, 2400, 2200];
    
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sales ($)',
                data: data,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#2563eb',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        display: true,
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}
