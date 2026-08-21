// ============================================
// SALES MODULE
// ============================================

let saleCart = [];
let saleSubtotal = 0;

async function renderSales() {
    const content = document.getElementById('pageContent');
    try {
        const sales = await api.getSales();
        const period = document.getElementById('salesPeriod')?.value || 'month';

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-success" onclick="openSaleModal()">
                    <i class="fas fa-plus"></i> New Sale
                </button>
                <div class="d-flex align-items-center gap-2 flex-wrap">
                    <label class="form-label mb-0">Report Period:</label>
                    <select id="salesPeriod" class="form-control" style="width:auto;" onchange="renderSales()">
                        <option value="today">Today</option>
                        <option value="week">This Week</option>
                        <option value="month" ${period==='month'?'selected':''}>This Month</option>
                        <option value="last_month">Last Month</option>
                        <option value="year">This Year</option>
                    </select>
                </div>
            </div>
            <div class="row g-3 mb-4" id="salesSummary">
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-primary"><i class="fas fa-receipt"></i></div><div class="stat-info"><div class="stat-value">...</div><div class="stat-label">Transactions</div></div></div></div>
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-success"><i class="fas fa-coins"></i></div><div class="stat-info"><div class="stat-value">...</div><div class="stat-label">Revenue</div></div></div></div>
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-info"><i class="fas fa-boxes"></i></div><div class="stat-info"><div class="stat-value">...</div><div class="stat-label">COGS</div></div></div></div>
                <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-icon bg-warning"><i class="fas fa-chart-line"></i></div><div class="stat-info"><div class="stat-value">...</div><div class="stat-label">Net Profit</div></div></div></div>
            </div>
            <div class="d-flex gap-2 mb-3 flex-wrap">
                <button class="btn btn-outline-primary btn-sm" onclick="generateSalesReport('${period}')"><i class="fas fa-file-alt me-1"></i>Generate Sales Report</button>
                <button class="btn btn-outline-success btn-sm" onclick="exportSalesReport('${period}')"><i class="fas fa-file-csv me-1"></i>Export CSV</button>
            </div>
            <div class="table-container">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Invoice #</th>
                            <th>Date</th>
                            <th>Customer</th>
                            <th>Items</th>
                            <th>Total</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${sales.map(sale => `
                            <tr>
                                <td><strong>${sale.invoice_number}</strong></td>
                                <td>${new Date(sale.sale_date).toLocaleDateString()}</td>
                                <td>${sale.customer_name || 'Walk-in'}</td>
                                <td>${sale.items?.length || 0}</td>
                                <td><strong>${formatMoney(sale.total_amount || 0)}</strong></td>
                                <td class="text-nowrap">
                                    <button class="btn btn-sm btn-outline-info me-1" onclick="viewSale(${sale.id})">View</button>
                                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editSale(${sale.id})">Edit</button>
                                    <button class="btn btn-sm btn-outline-danger me-1" onclick="deleteSale(${sale.id})">Delete</button>
                                    <button class="btn btn-sm btn-outline-secondary" onclick="downloadInvoice(${sale.id})">Invoice</button>
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="6" class="text-center text-muted">No sales yet</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
        loadSalesSummary(period);
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load sales: ${error.message}</div>`;
    }
}

async function loadSalesSummary(period) {
    try {
        const [pl, sr] = await Promise.all([
            api.getProfitLoss({ period }),
            api.getSalesReport({ period })
        ]);
        const cards = document.querySelectorAll('#salesSummary .stat-value');
        if (cards.length >= 4) {
            cards[0].textContent = sr.data.total_invoices ?? 0;
            cards[1].textContent = formatMoney(pl.data.revenue);
            cards[2].textContent = formatMoney(pl.data.cogs);
            cards[3].textContent = formatMoney(pl.data.net_profit);
        }
    } catch (e) {
        console.warn('Sales summary load failed', e);
    }
}

async function generateSalesReport(period) {
    try {
        const [pl, sr] = await Promise.all([
            api.getProfitLoss({ period }),
            api.getSalesReport({ period })
        ]);
        const d = pl.data;
        const items = (sr.data.daily || []).map(r => `
            <tr><td>${r.date}</td><td>${r.invoices}</td><td>${formatMoney(r.revenue)}</td></tr>
        `).join('') || '<tr><td colspan="3" class="text-center text-muted">No data</td></tr>';
        document.getElementById('pageContent').insertAdjacentHTML('beforeend', `
            <div class="card mt-3" id="salesReportCard">
                <div class="card-header d-flex justify-content-between"><span><i class="fas fa-file-alt me-2"></i>General Sales Report (${d.period.from} → ${d.period.to})</span><button class="btn btn-sm btn-outline-secondary" onclick="document.getElementById('salesReportCard').remove()">Close</button></div>
                <div class="card-body">
                    <div class="row g-3 mb-3">
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${sr.data.total_invoices}</div><div class="stat-label">Total Transactions</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(d.revenue)}</div><div class="stat-label">Total Revenue</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(d.cogs)}</div><div class="stat-label">COGS</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value text-success">${formatMoney(d.net_profit)}</div><div class="stat-label">Net Profit (Real P&L)</div></div></div></div>
                    </div>
                    <div class="row g-3 mb-3">
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(d.gross_profit)}</div><div class="stat-label">Gross Profit</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(d.expenses)}</div><div class="stat-label">Expenses</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${formatMoney(d.discount)}</div><div class="stat-label">Discounts</div></div></div></div>
                        <div class="col-6 col-lg-3"><div class="stat-card"><div class="stat-info"><div class="stat-value">${d.margin_percent}%</div><div class="stat-label">Margin</div></div></div></div>
                    </div>
                    <h6>Daily Breakdown</h6>
                    <div class="table-container"><table class="table table-sm"><thead><tr><th>Date</th><th>Invoices</th><th>Revenue</th></tr></thead><tbody>${items}</tbody></table></div>
                </div>
            </div>
        `);
        document.getElementById('salesReportCard').scrollIntoView({ behavior: 'smooth' });
    } catch (e) {
        alert('Failed to generate report: ' + e.message);
    }
}

async function exportSalesReport(period) {
    try {
        const blob = await api.exportReport('sales', { period });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sales_report.csv`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (e) {
        alert('Export failed: ' + e.message);
    }
}

function openSaleModal() {
    saleCart = [];
    saleSubtotal = 0;
    document.getElementById('sale_customer').value = 'Walk-in Customer';
    document.getElementById('sale_date').value = new Date().toISOString().split('T')[0];
    document.getElementById('sale_discount').value = 0;
    document.getElementById('sale_cart').innerHTML = '<p class="text-muted text-center">No items added yet</p>';
    document.getElementById('sale_subtotal').value = '0';
    document.getElementById('sale_total').value = '0';
    document.getElementById('sale_search').value = '';
    document.getElementById('saleSearchResults').innerHTML = '';
    
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
        
        if (medicines.length === 0) {
            resultsDiv.innerHTML = '<p class="text-muted">No medicines found</p>';
            return;
        }
        
        resultsDiv.innerHTML = `
            <div class="list-group">
                ${medicines.map(m => `
                    <button class="list-group-item list-group-item-action" onclick="addToCart(${m.id}, '${m.name}')">
                        <strong>${m.name}</strong> - ${m.generic_name || 'No generic'} 
                        <span class="badge bg-info float-end">${m.category || 'General'}</span>
                    </button>
                `).join('')}
            </div>
        `;
    } catch (error) {
        resultsDiv.innerHTML = `<p class="text-danger">Error searching: ${error.message}</p>`;
    }
}

async function addToCart(medicineId, medicineName) {
    const quantity = parseInt(document.getElementById('sale_quantity').value) || 1;
    
    try {
        const stock = await api.getMedicineStock(medicineId);
        if (stock.total_stock < quantity) {
            alert(`Not enough stock! Available: ${stock.total_stock}`);
            return;
        }
        
        const existing = saleCart.find(item => item.medicine_id === medicineId);
        if (existing) {
            existing.quantity += quantity;
        } else {
            saleCart.push({
                medicine_id: medicineId,
                medicine_name: medicineName,
                quantity: quantity,
                selling_price: stock.batches?.[0]?.selling_price || 0
            });
        }
        
        updateSaleCart();
        document.getElementById('sale_search').value = '';
        document.getElementById('saleSearchResults').innerHTML = '';
    } catch (error) {
        alert('Failed to add item: ' + error.message);
    }
}

function removeFromCart(index) {
    saleCart.splice(index, 1);
    updateSaleCart();
}

function updateSaleCart() {
    const cartDiv = document.getElementById('sale_cart');
    saleSubtotal = saleCart.reduce((sum, item) => sum + (item.quantity * item.selling_price), 0);
    
    if (saleCart.length === 0) {
        cartDiv.innerHTML = '<p class="text-muted text-center">No items added yet</p>';
        document.getElementById('sale_subtotal').value = '0';
        updateSaleTotal();
        return;
    }
    
    cartDiv.innerHTML = `
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Medicine</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Total</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                ${saleCart.map((item, index) => `
                    <tr>
                        <td>${item.medicine_name}</td>
                        <td>${item.quantity}</td>
                        <td>${formatMoney(item.selling_price)}</td>
                        <td>${formatMoney((item.quantity * item.selling_price))}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="removeFromCart(${index})">
                                <i class="fas fa-times"></i>
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    document.getElementById('sale_subtotal').value = saleSubtotal.toFixed(2);
    updateSaleTotal();
}

function updateSaleTotal() {
    const discount = parseFloat(document.getElementById('sale_discount').value) || 0;
    const total = saleSubtotal - discount;
    document.getElementById('sale_total').value = total.toFixed(2);
}

async function createSale() {
    if (saleCart.length === 0) {
        alert('Please add at least one item to the sale!');
        return;
    }
    
    const data = {
        customer_name: document.getElementById('sale_customer').value || 'Walk-in Customer',
        sale_date: document.getElementById('sale_date').value || new Date().toISOString().split('T')[0],
        discount_amount: parseFloat(document.getElementById('sale_discount').value) || 0,
        items: saleCart.map(item => ({
            medicine_id: item.medicine_id,
            quantity: item.quantity
        }))
    };
    
    try {
        await api.createSale(data);
        bootstrap.Modal.getInstance(document.getElementById('createSaleModal')).hide();
        alert('Sale completed successfully!');
        navigateTo('sales');
    } catch (error) {
        alert('Failed to create sale: ' + error.message);
    }
}

async function viewSale(id) {
    try {
        const sale = await api.getSale(id);
        alert(`Sale #${sale.invoice_number}\nCustomer: ${sale.customer_name}\nTotal: ${formatMoney(sale.total_amount)}\nItems: ${sale.items?.length || 0}`);
    } catch (error) {
        alert('Failed to load sale: ' + error.message);
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
        alert('Failed to download invoice: ' + error.message);
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
        alert('Failed to load sale: ' + error.message);
    }
}

async function updateSale() {
    const id = document.getElementById('edit_sale_id').value;
    const data = {
        customer_name: document.getElementById('edit_sale_customer').value,
        discount_amount: parseFloat(document.getElementById('edit_sale_discount').value) || 0
    };
    try {
        const res = await api.updateSale(id, data);
        if (res && res.success === false) {
            alert('Failed: ' + (res.message || 'Unknown error'));
            return;
        }
        bootstrap.Modal.getInstance(document.getElementById('editSaleModal')).hide();
        alert('Sale updated successfully!');
        renderSales();
    } catch (error) {
        alert('Failed: ' + error.message);
    }
}

async function deleteSale(id) {
    if (!confirm('Delete this sale? Stock itarejeshwa (restored) kwenye batch.')) return;
    try {
        const res = await api.deleteSale(id);
        if (res && res.success === false) {
            alert('Failed: ' + (res.message || 'Unknown error'));
            return;
        }
        alert('Sale deleted. Stock restored.');
        renderSales();
    } catch (error) {
        alert('Failed: ' + error.message);
    }
}

console.log('Sales module loaded');
