// ============================================
// REPORT GENERATOR MODULE
// ============================================

let reportChartInstance = null;

async function renderReports() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="d-flex flex-wrap gap-3 align-items-end mb-4">
            <div>
                <label class="form-label mb-1 fw-bold">Report Type</label>
                <select id="reportType" class="form-control" onchange="onReportTypeChange()" style="min-width:200px;">
                    <option value="sales">Sales Report</option>
                    <option value="purchases">Purchases Report</option>
                    <option value="inventory">Inventory Report</option>
                    <option value="expiry">Expiry Report</option>
                </select>
            </div>
            <div id="periodWrap">
                <label class="form-label mb-1 fw-bold">Period</label>
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
            <button class="btn btn-outline-secondary" onclick="printReportClean()"><i class="fas fa-print me-1"></i>Print</button>
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
            <div class="card" id="reportOutput"><div class="card-header"><i class="fas fa-chart-bar me-2"></i>${title}</div>
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

function printReportClean() {
    const output = document.getElementById('reportOutput');
    if (!output) {
        SwalAlert.warning('Generate a report first!');
        return;
    }

    const reportType = document.getElementById('reportType')?.value || 'Report';
    const period = document.getElementById('reportPeriod')?.value || '';
    const title = output.querySelector('.card-header')?.textContent || reportType;
    
    const statsHtml = output.querySelectorAll('.stat-card').length > 0
        ? Array.from(output.querySelectorAll('.stat-card')).map(sc => {
            const val = sc.querySelector('.stat-value')?.textContent || '';
            const label = sc.querySelector('.stat-label')?.textContent || '';
            return `<div style="flex:1;min-width:140px;"><strong>${label}:</strong> ${val}</div>`;
        }).join('')
        : '';

    const table = output.querySelector('table');
    const tableHtml = table ? table.outerHTML : '';

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>${title}</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 30px; color: #333; }
                h1 { text-align: center; font-size: 22px; margin-bottom: 4px; color: #1e3a5f; }
                .subtitle { text-align: center; color: #666; margin-bottom: 4px; }
                .date { text-align: center; color: #999; font-size: 12px; margin-bottom: 20px; }
                .stats { display: flex; flex-wrap: wrap; gap: 15px; margin: 15px 0; }
                table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }
                th, td { border: 1px solid #ddd; padding: 8px 10px; text-align: left; }
                th { background: #f5f5f5; font-weight: 600; text-transform: uppercase; font-size: 11px; }
                .footer { text-align: center; color: #999; font-size: 11px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }
                @media print { body { padding: 15px; } }
            </style>
        </head>
        <body>
            <h1>PharmaCare - Pharmacy Management System</h1>
            <p class="subtitle">${title}</p>
            <p class="subtitle">${period ? 'Period: ' + period : ''}</p>
            <p class="date">Generated: ${new Date().toLocaleString()}</p>
            ${statsHtml ? '<div class="stats">' + statsHtml + '</div>' : ''}
            ${tableHtml}
            <div class="footer">PharmaCare Pharmacy Management System — Confidential</div>
            <script>window.onload=function(){window.print();}<\/script>
        </body>
        </html>
    `);
    printWindow.document.close();
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
        SwalAlert.error(e.message);
    }
}

console.log('Report Generator module loaded');
