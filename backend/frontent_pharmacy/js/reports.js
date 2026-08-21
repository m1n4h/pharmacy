// ============================================
// REPORT GENERATOR MODULE
// ============================================

let reportChartInstance = null;

async function renderReports() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="d-flex flex-wrap gap-3 align-items-end mb-4">
            <div>
                <label class="form-label mb-1">Report Type</label>
                <select id="reportType" class="form-control" onchange="onReportTypeChange()" style="min-width:200px;">
                    <option value="sales">Sales Report</option>
                    <option value="purchases">Purchases Report</option>
                    <option value="inventory">Inventory Report</option>
                    <option value="expiry">Expiry Report</option>
                </select>
            </div>
            <div id="periodWrap">
                <label class="form-label mb-1">Period</label>
                <select id="reportPeriod" class="form-control" style="min-width:160px;">
                    <option value="today">Today</option>
                    <option value="week">This Week</option>
                    <option value="month" selected>This Month</option>
                    <option value="last_month">Last Month</option>
                    <option value="year">This Year</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="generateReport()"><i class="fas fa-search me-1"></i>Generate</button>
            <button class="btn btn-outline-success" onclick="exportCurrentReport()"><i class="fas fa-file-csv me-1"></i>Export CSV</button>
            <button class="btn btn-outline-secondary" onclick="window.print()"><i class="fas fa-print me-1"></i>Print</button>
        </div>
        <div id="reportResults"></div>
    `;
    onReportTypeChange();
    generateReport();
}

function onReportTypeChange() {
    const type = document.getElementById('reportType').value;
    const periodWrap = document.getElementById('periodWrap');
    if (type === 'inventory' || type === 'expiry') {
        periodWrap.style.display = 'none';
    } else {
        periodWrap.style.display = '';
    }
}

async function generateReport() {
    const type = document.getElementById('reportType').value;
    const period = document.getElementById('reportPeriod')?.value || 'month';
    const container = document.getElementById('reportResults');
    container.innerHTML = `<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>`;
    try {
        let rows = [];
        let headers = [];
        let title = '';
        if (type === 'sales') {
            const d = (await api.getSalesReport({ period })).data;
            title = `Sales Report (${d.period.from} → ${d.period.to})`;
            rows = d.daily.map(r => ({ Date: r.date, Invoices: r.invoices, Revenue: formatMoney(r.revenue) }));
            headers = ['Date', 'Invoices', 'Revenue'];
        } else if (type === 'purchases') {
            const d = (await api.getPurchasesReport({ period })).data;
            title = `Purchases Report (${d.period.from} → ${d.period.to})`;
            rows = d.by_supplier.map(r => ({ Supplier: r.supplier, Purchases: r.purchases, Amount: formatMoney(r.amount) }));
            headers = ['Supplier', 'Purchases', 'Amount'];
        } else if (type === 'inventory') {
            const d = (await api.getInventoryReport()).data;
            title = 'Inventory Report (Low & Dead Stock)';
            rows = [...d.low_stock, ...d.dead_stock].map(r => ({ Medicine: r.name, Category: r.category, Quantity: r.quantity, Status: r.quantity === 0 ? 'Dead' : 'Low' }));
            headers = ['Medicine', 'Category', 'Quantity', 'Status'];
        } else if (type === 'expiry') {
            const d = (await api.getExpiryReport()).data;
            title = 'Expiry Report';
            rows = d.items.map(r => ({ Batch: r.batch_no, Quantity: r.quantity, Expiry: r.expiry_date, DaysLeft: r.days_remaining, Value: formatMoney(r.stock_value) }));
            headers = ['Batch', 'Quantity', 'Expiry', 'DaysLeft', 'Value'];
        }

        const tableRows = rows.length ? rows.map(r => `
            <tr>${headers.map(h => `<td>${r[h] ?? ''}</td>`).join('')}</tr>
        `).join('') : '<tr><td colspan="10" class="text-center text-muted">No data.</td></tr>';

        container.innerHTML = `
            <div class="card"><div class="card-header"><i class="fas fa-chart-bar me-2"></i>${title}</div>
            <div class="card-body">
                <div class="table-container">
                    <table class="table table-hover">
                        <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
                        <tbody>${tableRows}</tbody>
                    </table>
                </div>
            </div></div>
        `;
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
    }
}

async function exportCurrentReport() {
    const type = document.getElementById('reportType').value;
    const period = document.getElementById('reportPeriod')?.value || 'month';
    try {
        const blob = await api.exportReport(type, { period });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}_report.csv`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (e) {
        alert('Export failed: ' + e.message);
    }
}

console.log('Report Generator module loaded');
