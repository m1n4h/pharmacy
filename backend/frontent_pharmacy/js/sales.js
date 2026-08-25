// ============================================
// SALES MODULE — Complete Implementation
// ============================================

let saleItems = [];
let saleSubtotal = 0;

const PERIOD_OPTIONS = [
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'last_month', label: 'Last Month' },
    { value: '3_months', label: '3 Months' },
    { value: '5_months', label: '5 Months' },
    { value: '6_months', label: '6 Months' },
    { value: 'year', label: 'This Year' },
    { value: '5_years', label: '5 Years' },
    { value: 'custom', label: 'Custom Range' },
];

function periodOptionsHtml(selected) {
    return PERIOD_OPTIONS.map(p =>
        `<option value="${p.value}" ${p.value === selected ? 'selected' : ''}>${p.label}</option>`
    ).join('');
}

async function renderSales() {
    const content = document.getElementById('pageContent');
    const period = document.getElementById('salesPeriod')?.value || 'month';

    const isAdmin = (localStorage.getItem('userRole') || '').toLowerCase() === 'admin' || (localStorage.getItem('userRole') || '').toLowerCase() === 'superadmin';

    content.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
            <h4 class="mb-0"><i class="fas fa-cash-register me-2"></i>Sales Dashboard</h4>
            <div class="d-flex gap-2">
                ${isAdmin ? `<button class="btn btn-outline-info" onclick="showUploadHistory()">
                    <i class="fas fa-history"></i> ${t('Upload History')}
                </button>` : ''}
                ${isAdmin ? `<button class="btn btn-info" onclick="openUploadSalesModal()">
                    <i class="fas fa-cloud-upload-alt"></i> ${t('Upload Sales')}
                </button>` : ''}
                <button class="btn btn-success" onclick="openSaleModal()">
                    <i class="fas fa-plus"></i> ${t('Create Sale')}
                </button>
            </div>
        </div>

        <div class="d-flex align-items-center gap-2 mb-4 flex-wrap">
            <label class="form-label mb-0 fw-bold">Period:</label>
            <select id="salesPeriod" class="form-control" style="width:auto;" onchange="onSalesPeriodChange()">
                ${periodOptionsHtml(period)}
            </select>
            <div id="customDateRange" class="d-none d-flex gap-2">
                <input type="date" id="dateFrom" class="form-control" style="width:auto;">
                <input type="date" id="dateTo" class="form-control" style="width:auto;">
                <button class="btn btn-primary btn-sm" onclick="renderSalesSummary()">Apply</button>
            </div>
            <button class="btn btn-outline-success btn-sm ms-auto" onclick="exportSalesCSV()">
                <i class="fas fa-file-csv me-1"></i>Export CSV
            </button>
        </div>

        <div class="row g-3 mb-4" id="salesSummary">
            <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-primary"><i class="fas fa-receipt"></i></div><div class="stat-info"><div class="stat-value" id="kpi-transactions">...</div><div class="stat-label">Transactions</div></div></div></div>
            <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-success"><i class="fas fa-coins"></i></div><div class="stat-info"><div class="stat-value" id="kpi-revenue">...</div><div class="stat-label">Revenue</div></div></div></div>
            <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-info"><i class="fas fa-boxes"></i></div><div class="stat-info"><div class="stat-value" id="kpi-cogs">...</div><div class="stat-label">COGS</div></div></div></div>
            <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-warning"><i class="fas fa-chart-line"></i></div><div class="stat-info"><div class="stat-value" id="kpi-profit">...</div><div class="stat-label">Net Profit</div></div></div></div>
        </div>
        <div class="row g-3 mb-4">
            <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-secondary"><i class="fas fa-calculator"></i></div><div class="stat-info"><div class="stat-value" id="kpi-avg">...</div><div class="stat-label">Avg Sale</div></div></div></div>
            <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-danger"><i class="fas fa-percent"></i></div><div class="stat-info"><div class="stat-value" id="kpi-discounts">...</div><div class="stat-label">Discounts</div></div></div></div>
            <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-success"><i class="fas fa-hand-holding-usd"></i></div><div class="stat-info"><div class="stat-value" id="kpi-gross">...</div><div class="stat-label">Gross Profit</div></div></div></div>
            <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-primary"><i class="fas fa-percentage"></i></div><div class="stat-info"><div class="stat-value" id="kpi-margin">...</div><div class="stat-label">Margin</div></div></div></div>
        </div>

        <div class="d-flex gap-2 mb-3 flex-wrap">
            <button class="btn btn-outline-primary btn-sm" onclick="generateSalesReport()"><i class="fas fa-file-alt me-1"></i>Generate Report</button>
        </div>

        <div class="card mb-4">
            <div class="card-header"><i class="fas fa-table me-2"></i>Sales Records</div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover mb-0">
                        <thead>
                            <tr>
                                <th>Invoice #</th>
                                <th>Date</th>
                                <th>Customer</th>
                                <th>Items</th>
                                <th>Subtotal</th>
                                <th>Discount</th>
                                <th>Total</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="salesTableBody">
                            <tr><td colspan="8" class="text-center text-muted">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;

    if (period === 'custom') {
        document.getElementById('customDateRange').classList.remove('d-none');
    }

    await loadSalesList();
    await renderSalesSummary();
}

function onSalesPeriodChange() {
    const period = document.getElementById('salesPeriod')?.value;
    const customDiv = document.getElementById('customDateRange');
    if (customDiv) {
        if (period === 'custom') customDiv.classList.remove('d-none');
        else customDiv.classList.add('d-none');
    }
    renderSalesSummary();
}

function getCurrentPeriodParams() {
    const period = document.getElementById('salesPeriod')?.value || 'month';
    if (period === 'custom') {
        const df = document.getElementById('dateFrom')?.value;
        const dt = document.getElementById('dateTo')?.value;
        if (df && dt) return { date_from: df, date_to: dt };
    }
    return { period };
}

async function loadSalesList() {
    try {
        const sales = await api.getSales(200);
        const tbody = document.getElementById('salesTableBody');
        if (!sales || sales.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No sales found. Create your first sale!</td></tr>';
            return;
        }
        tbody.innerHTML = sales.map(sale => `
            <tr>
                <td><strong>${sale.invoice_number || '-'}</strong></td>
                <td>${new Date(sale.sale_date).toLocaleDateString()}</td>
                <td>${sale.customer_name || 'Walk-in'}</td>
                <td>${sale.items?.length || 0}</td>
                <td>${formatMoney(safeNumber(sale.subtotal))}</td>
                <td>${formatMoney(safeNumber(sale.discount_amount))}</td>
                <td><strong>${formatMoney(safeNumber(sale.total_amount))}</strong></td>
                <td class="text-nowrap">
                    <button class="btn btn-sm btn-outline-info me-1" onclick="viewSale(${sale.id})">View</button>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editSale(${sale.id})">Edit</button>
                    <button class="btn btn-sm btn-outline-danger me-1" onclick="deleteSale(${sale.id})">Delete</button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="downloadInvoice(${sale.id})">Invoice</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('salesTableBody').innerHTML =
            `<tr><td colspan="8" class="text-center text-danger">Failed to load sales: ${error.message}</td></tr>`;
    }
}

async function renderSalesSummary() {
    const params = getCurrentPeriodParams();
    try {
        const [pl, sr] = await Promise.all([
            api.getProfitLoss(params),
            api.getSalesReport(params)
        ]);
        const plData = pl?.data || pl || {};
        const srData = sr?.data || sr || {};

        const revenue = safeNumber(plData.revenue);
        const cogs = safeNumber(plData.cogs);
        const netProfit = safeNumber(plData.net_profit);
        const grossProfit = safeNumber(plData.gross_profit);
        const expenses = safeNumber(plData.expenses);
        const discount = safeNumber(plData.discount);
        const totalInvoices = safeNumber(srData.total_invoices);
        const avgSale = totalInvoices > 0 ? revenue / totalInvoices : 0;
        const margin = plData.margin_percent ?? (revenue > 0 ? ((netProfit / revenue) * 100).toFixed(1) : '0.0');

        setText('kpi-transactions', totalInvoices);
        setText('kpi-revenue', formatMoney(revenue));
        setText('kpi-cogs', formatMoney(cogs));
        setText('kpi-profit', formatMoney(netProfit));
        setText('kpi-avg', formatMoney(avgSale));
        setText('kpi-discounts', formatMoney(discount));
        setText('kpi-gross', formatMoney(grossProfit));
        setText('kpi-margin', margin + '%');
    } catch (e) {
        console.warn('Sales summary load failed', e);
    }
}

function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val ?? '0';
}

async function generateSalesReport() {
    const params = getCurrentPeriodParams();
    try {
        const [pl, sr] = await Promise.all([
            api.getProfitLoss(params),
            api.getSalesReport(params)
        ]);
        const plData = pl?.data || pl || {};
        const srData = sr?.data || sr || {};
        const periodInfo = srData.period || {};
        const daily = srData.daily || [];

        const existing = document.getElementById('salesReportCard');
        if (existing) existing.remove();

        const dailyRows = daily.length > 0
            ? daily.map(r => `<tr><td>${r.date}</td><td>${r.invoices}</td><td>${formatMoney(safeNumber(r.revenue))}</td></tr>`).join('')
            : '<tr><td colspan="3" class="text-center text-muted">No daily data for this period</td></tr>';

        const revenue = safeNumber(plData.revenue);
        const cogs = safeNumber(plData.cogs);
        const netProfit = safeNumber(plData.net_profit);

        document.getElementById('pageContent').insertAdjacentHTML('beforeend', `
            <div class="card mt-3 mb-4" id="salesReportCard">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span><i class="fas fa-file-alt me-2"></i>Sales Report (${periodInfo.from || '?'} to ${periodInfo.to || '?'})</span>
                    <div>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="printSalesReport()"><i class="fas fa-print me-1"></i>Print</button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="document.getElementById('salesReportCard').remove()">Close</button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row g-3 mb-3">
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${safeNumber(srData.total_invoices)}</div><div class="stat-label">Total Transactions</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(revenue)}</div><div class="stat-label">Total Revenue</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(cogs)}</div><div class="stat-label">COGS</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value text-success">${formatMoney(netProfit)}</div><div class="stat-label">Net Profit</div></div></div></div>
                    </div>
                    <div class="row g-3 mb-3">
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(safeNumber(plData.gross_profit))}</div><div class="stat-label">Gross Profit</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(safeNumber(plData.expenses))}</div><div class="stat-label">Expenses</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(safeNumber(plData.discount))}</div><div class="stat-label">Discounts</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${plData.margin_percent ?? '0.0'}%</div><div class="stat-label">Margin</div></div></div></div>
                    </div>
                    <h6 class="mt-3">Daily Breakdown</h6>
                    <div class="table-container"><table class="table table-sm"><thead><tr><th>Date</th><th>Invoices</th><th>Revenue</th></tr></thead><tbody>${dailyRows}</tbody></table></div>
                </div>
            </div>
        `);
        document.getElementById('salesReportCard').scrollIntoView({ behavior: 'smooth' });
    } catch (e) {
        SwalAlert.error('Failed to generate report: ' + e.message);
    }
}

function printSalesReport() {
    const card = document.getElementById('salesReportCard');
    if (!card) { SwalAlert.warning('Generate a report first.'); return; }

    const reportName = 'Sales Report';
    const periodText = card.querySelector('.card-header span')?.textContent || 'Sales Report';
    const rows = card.querySelectorAll('table tbody tr');
    let tableHtml = '';
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 2) {
            tableHtml += '<tr>' + Array.from(cells).map(c => '<td>' + c.textContent + '</td>').join('') + '</tr>';
        }
    });
    const thead = card.querySelector('table thead');
    const headerHtml = thead ? '<thead>' + thead.innerHTML + '</thead>' : '';

    const stats = card.querySelectorAll('.stat-value');
    const labels = card.querySelectorAll('.stat-label');
    let statsHtml = '<div style="display:flex;flex-wrap:wrap;gap:20px;margin:15px 0;">';
    for (let i = 0; i < stats.length; i++) {
        statsHtml += `<div style="flex:1;min-width:140px;"><strong>${labels[i]?.textContent || ''}:</strong> ${stats[i]?.textContent || ''}</div>`;
    }
    statsHtml += '</div>';

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>${reportName}</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 30px; color: #333; }
                h1 { text-align: center; font-size: 22px; margin-bottom: 4px; color: #1e3a5f; }
                .subtitle { text-align: center; color: #666; margin-bottom: 4px; }
                .date { text-align: center; color: #999; font-size: 12px; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }
                th, td { border: 1px solid #ddd; padding: 8px 10px; text-align: left; }
                th { background: #f5f5f5; font-weight: 600; text-transform: uppercase; font-size: 11px; }
                .footer { text-align: center; color: #999; font-size: 11px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }
                @media print { body { padding: 15px; } }
            </style>
        </head>
        <body>
            <h1>PharmaCare - Pharmacy Management System</h1>
            <p class="subtitle">${reportName}</p>
            <p class="subtitle">${periodText}</p>
            <p class="date">Generated: ${new Date().toLocaleString()}</p>
            ${statsHtml}
            <table>
                ${headerHtml}
                <tbody>${tableHtml}</tbody>
            </table>
            <div class="footer">PharmaCare Pharmacy Management System — Confidential</div>
            <script>window.onload=function(){window.print();}<\/script>
        </body>
        </html>
    `);
    printWindow.document.close();
}

async function exportSalesCSV() {
    const params = getCurrentPeriodParams();
    const period = params.period || 'custom';
    const qs = new URLSearchParams(params).toString();
    try {
        let url = `${window.location.origin || ''}/reports/export/sales?${qs}`;
        const token = api.token || localStorage.getItem('token');
        const headers = {};
        if (token) headers['Authorization'] = 'Bearer ' + token;
        const response = await fetch(url, { headers });
        if (!response.ok) throw new Error('Export failed (HTTP ' + response.status + ')');
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        const today = new Date().toISOString().split('T')[0];
        a.download = `pharmacy_sales_${today}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(blobUrl);
    } catch (e) {
        SwalAlert.error('Export failed: ' + e.message);
    }
}

// ============================================
// POS FORM — Create Sale
// ============================================

function openSaleModal() {
    saleItems = [];
    saleSubtotal = 0;
    document.getElementById('sale_customer').value = '';
    document.getElementById('sale_date').value = new Date().toISOString().split('T')[0];
    document.getElementById('sale_discount').value = 0;
    document.getElementById('sale_payment_method').value = 'cash';
    document.getElementById('sale_amount_paid').value = '';
    document.getElementById('sale_notes').value = '';
    document.getElementById('saleCart').innerHTML = '<p class="text-muted text-center">No items added yet. Search and add medicines above.</p>';
    document.getElementById('sale_subtotal').value = '0';
    document.getElementById('sale_total').value = '0';
    document.getElementById('sale_change').value = '0';
    document.getElementById('sale_amount_due').value = '0';
    document.getElementById('sale_search').value = '';
    document.getElementById('saleSearchResults').innerHTML = '';
    document.getElementById('sale_error').innerHTML = '';

    const modal = new bootstrap.Modal(document.getElementById('createSaleModal'));
    modal.show();
}

async function searchMedicinesForSale(query) {
    const resultsDiv = document.getElementById('saleSearchResults');
    if (!query || query.length < 2) {
        resultsDiv.innerHTML = '';
        return;
    }

    try {
        const medicines = await api.getPosMedicines(query);
        if (!medicines || medicines.length === 0) {
            resultsDiv.innerHTML = '<p class="text-muted">No medicines found with available stock</p>';
            return;
        }

        resultsDiv.innerHTML = `
            <div class="list-group" style="max-height:250px;overflow-y:auto;">
                ${medicines.map(m => {
                    const qty = m.quantity || 0;
                    const expiry = m.expiry_date ? new Date(m.expiry_date) : null;
                    const today = new Date();
                    const daysToExpiry = expiry ? Math.ceil((expiry - today) / 86400000) : 999;
                    const expiryBadge = daysToExpiry <= 0
                        ? '<span class="badge bg-danger ms-1">EXPIRED</span>'
                        : daysToExpiry <= 30
                            ? `<span class="badge bg-warning text-dark ms-1">Exp: ${daysToExpiry}d</span>`
                            : '';
                    return `
                        <button class="list-group-item list-group-item-action" onclick="addToCart(${m.id}, '${m.name.replace(/'/g, "\\'")}', ${m.price || 0}, ${qty})">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>${m.name}</strong>
                                    <small class="text-muted ms-1">${m.generic_name || ''}</small>
                                    ${expiryBadge}
                                </div>
                                <div class="text-end">
                                    <span class="badge bg-secondary">${qty} in stock</span>
                                    <div><small>${formatMoney(m.price || 0)}</small></div>
                                </div>
                            </div>
                        </button>
                    `;
                }).join('')}
            </div>
        `;
    } catch (error) {
        resultsDiv.innerHTML = `<p class="text-danger">Error searching: ${error.message}</p>`;
    }
}

function addToCart(medicineId, medicineName, price, availableStock) {
    const quantity = parseInt(document.getElementById('sale_quantity').value) || 1;

    if (quantity <= 0) {
        document.getElementById('sale_error').innerHTML = '<div class="alert alert-danger py-2">Quantity must be at least 1.</div>';
        return;
    }

    if (quantity > availableStock) {
        document.getElementById('sale_error').innerHTML = `<div class="alert alert-danger py-2">Not enough stock for ${medicineName}. Available: ${availableStock}, requested: ${quantity}.</div>`;
        return;
    }

    const existing = saleItems.find(item => item.medicine_id === medicineId);
    if (existing) {
        const newQty = existing.quantity + quantity;
        if (newQty > availableStock) {
            document.getElementById('sale_error').innerHTML = `<div class="alert alert-danger py-2">Cannot add more ${medicineName}. Total would be ${newQty}, but only ${availableStock} in stock.</div>`;
            return;
        }
        existing.quantity = newQty;
    } else {
        saleItems.push({
            medicine_id: medicineId,
            medicine_name: medicineName,
            quantity: quantity,
            selling_price: safeNumber(price),
            available_stock: availableStock
        });
    }

    updateSaleCart();
    document.getElementById('sale_search').value = '';
    document.getElementById('saleSearchResults').innerHTML = '';
    document.getElementById('sale_error').innerHTML = '';
}

function removeFromCart(index) {
    saleItems.splice(index, 1);
    updateSaleCart();
}

function updateSaleCart() {
    const cartDiv = document.getElementById('saleCart');
    saleSubtotal = saleItems.reduce((sum, item) => sum + (item.quantity * safeNumber(item.selling_price)), 0);

    if (saleItems.length === 0) {
        cartDiv.innerHTML = '<p class="text-muted text-center">No items added yet</p>';
        document.getElementById('sale_subtotal').value = '0';
        updateSaleTotals();
        return;
    }

    cartDiv.innerHTML = `
        <table class="table table-sm mb-0">
            <thead>
                <tr><th>Medicine</th><th>Qty</th><th>Unit Price</th><th>Total</th><th></th></tr>
            </thead>
            <tbody>
                ${saleItems.map((item, index) => `
                    <tr>
                        <td>${item.medicine_name}</td>
                        <td><input type="number" min="1" max="${item.available_stock || 999}" value="${item.quantity}" class="form-control form-control-sm" style="width:70px;display:inline-block;" onchange="updateCartItemQty(${index}, this.value)"></td>
                        <td>${formatMoney(item.selling_price)}</td>
                        <td><strong>${formatMoney(item.quantity * safeNumber(item.selling_price))}</strong></td>
                        <td><button class="btn btn-sm btn-outline-danger" onclick="removeFromCart(${index})">X</button></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    document.getElementById('sale_subtotal').value = formatMoney(saleSubtotal);
    updateSaleTotals();
}

function updateCartItemQty(index, newVal) {
    const qty = parseInt(newVal) || 1;
    if (qty <= 0) return;
    const item = saleItems[index];
    if (item && qty <= (item.available_stock || 999)) {
        item.quantity = qty;
        updateSaleCart();
    }
}

function updateSaleTotals() {
    const discount = safeNumber(document.getElementById('sale_discount')?.value);
    const total = Math.max(0, saleSubtotal - discount);
    const amountPaidRaw = document.getElementById('sale_amount_paid')?.value;
    const amountPaid = (amountPaidRaw === '' || amountPaidRaw === null || amountPaidRaw === undefined) ? 0 : safeNumber(amountPaidRaw);

    document.getElementById('sale_total').value = formatMoney(total);
    document.getElementById('sale_subtotal').value = formatMoney(saleSubtotal);

    if (amountPaid >= total) {
        document.getElementById('sale_change').value = formatMoney(amountPaid - total);
        document.getElementById('sale_amount_due').value = formatMoney(0);
    } else {
        document.getElementById('sale_change').value = formatMoney(0);
        document.getElementById('sale_amount_due').value = formatMoney(total - amountPaid);
    }
}

async function createSale() {
    if (saleItems.length === 0) {
        document.getElementById('sale_error').innerHTML = '<div class="alert alert-danger py-2">Please add at least one item to the sale.</div>';
        return;
    }

    const discount = safeNumber(document.getElementById('sale_discount').value);
    if (discount > saleSubtotal) {
        document.getElementById('sale_error').innerHTML = '<div class="alert alert-danger py-2">Discount cannot exceed subtotal.</div>';
        return;
    }

    const amountPaid = safeNumber(document.getElementById('sale_amount_paid').value);
    const total = Math.max(0, saleSubtotal - discount);

    const customerName = document.getElementById('sale_customer').value.trim() || 'Walk-in Customer';
    const data = {
        customer_name: customerName,
        sale_date: document.getElementById('sale_date').value || new Date().toISOString().split('T')[0],
        discount_amount: discount,
        items: saleItems.map(item => ({
            medicine_id: item.medicine_id,
            quantity: item.quantity
        }))
    };

    const btn = document.querySelector('#createSaleModal .btn-success');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...'; }

    try {
        const res = await api.createSale(data);
        if (res && res.success === false) {
            document.getElementById('sale_error').innerHTML = `<div class="alert alert-danger py-2">${res.message || 'Failed to create sale.'}</div>`;
            return;
        }
        const invoiceNum = res?.data?.invoice_number || 'N/A';
        bootstrap.Modal.getInstance(document.getElementById('createSaleModal')).hide();
        SwalAlert.success(`Sale completed successfully!\nInvoice: ${invoiceNum}\nTotal: ${formatMoney(total)}\nAmount Paid: ${formatMoney(amountPaid)}`);
        await renderSales();
    } catch (error) {
        document.getElementById('sale_error').innerHTML = `<div class="alert alert-danger py-2">Failed to create sale: ${error.message}</div>`;
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-check"></i> Complete Sale'; }
    }
}

// ============================================
// VIEW / EDIT / DELETE
// ============================================

async function viewSale(id) {
    try {
        const sale = await api.getSale(id);
        const items = (sale.items || []).map(it =>
            `  ${it.medicine_name || 'Medicine #' + it.medicine_id} x${it.quantity} @ ${formatMoney(it.selling_price)}`
        ).join('\n');
        SwalAlert.success(
            `Sale #${sale.invoice_number}\n` +
            `Customer: ${sale.customer_name}\n` +
            `Date: ${sale.sale_date}\n` +
            `Subtotal: ${formatMoney(safeNumber(sale.subtotal))}\n` +
            `Discount: ${formatMoney(safeNumber(sale.discount_amount))}\n` +
            `Total: ${formatMoney(safeNumber(sale.total_amount))}\n` +
            `Items (${sale.items?.length || 0}):\n${items}`
        );
    } catch (error) {
        SwalAlert.error('Failed to load sale: ' + error.message);
    }
}

async function downloadInvoice(saleId) {
    try {
        const blob = await api.downloadInvoice(saleId);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `invoice_${saleId}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
    } catch (error) {
        SwalAlert.error('Failed to download invoice: ' + error.message);
    }
}

async function editSale(id) {
    try {
        const sale = await api.getSale(id);
        document.getElementById('edit_sale_id').value = sale.id;
        document.getElementById('edit_sale_customer').value = sale.customer_name || '';
        document.getElementById('edit_sale_discount').value = sale.discount_amount || 0;
        new bootstrap.Modal(document.getElementById('editSaleModal')).show();
    } catch (error) {
        SwalAlert.error('Failed to load sale: ' + error.message);
    }
}

async function updateSale() {
    const id = document.getElementById('edit_sale_id').value;
    const discount = safeNumber(document.getElementById('edit_sale_discount').value);
    const data = {
        customer_name: document.getElementById('edit_sale_customer').value,
        discount_amount: discount
    };
    try {
        const res = await api.updateSale(id, data);
        if (res && res.success === false) {
            SwalAlert.warning('Failed: ' + (res.message || 'Unknown error'));
            return;
        }
        bootstrap.Modal.getInstance(document.getElementById('editSaleModal')).hide();
        SwalAlert.success('Sale updated successfully!');
        renderSales();
    } catch (error) {
        SwalAlert.error('Failed: ' + error.message);
    }
}

async function deleteSale(id) {
    const result = await SwalAlert.confirm('Delete this sale? Stock will be restored to the original batches.');
    if (!result.isConfirmed) return;
    try {
        const res = await api.deleteSale(id);
        if (res && res.success === false) {
            SwalAlert.warning('Failed: ' + (res.message || 'Unknown error'));
            return;
        }
        SwalAlert.success('Sale deleted. Stock restored.');
        renderSales();
    } catch (error) {
        SwalAlert.error('Failed: ' + error.message);
    }
}

console.log('Sales module loaded');
