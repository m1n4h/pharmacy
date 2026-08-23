// ============================================
// RETURNS MODULE
// ============================================

let returnSaleData = null;
let returnItems = [];

async function renderReturns() {
    const content = document.getElementById('pageContent');
    try {
        const returns = await api.getReturns();

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openReturnModal()">
                    <i class="fas fa-plus"></i> <span data-i18n="processReturn">Process Return</span>
                </button>
                <span class="text-muted">Total: ${returns.length} <span data-i18n="returns">returns</span></span>
            </div>
            <div class="table-container">
                <table class="table table-hover" id="returnsTable">
                    <thead>
                        <tr>
                            <th data-i18n="returnNumber">Return #</th>
                            <th data-i18n="saleInvoice">Sale Invoice</th>
                            <th data-i18n="customer">Customer</th>
                            <th data-i18n="totalRefund">Total Refund</th>
                            <th data-i18n="status">Status</th>
                            <th data-i18n="date">Date</th>
                        </tr>
                    </thead>
                    <tbody id="returnsTableBody">
                        ${returns.map(r => `
                            <tr>
                                <td><strong>${r.return_number || 'R-' + r.id}</strong></td>
                                <td>${r.sale_invoice_number || '-'}</td>
                                <td>${r.customer_name || 'Walk-in'}</td>
                                <td><strong>${formatMoney(r.total_refund || 0)}</strong></td>
                                <td>
                                    <span class="badge ${r.status === 'completed' ? 'bg-success' : r.status === 'pending' ? 'bg-warning text-dark' : 'bg-secondary'}">
                                        ${r.status || 'completed'}
                                    </span>
                                </td>
                                <td>${r.return_date ? new Date(r.return_date).toLocaleDateString() : '-'}</td>
                            </tr>
                        `).join('') || '<tr><td colspan="6" class="text-center text-muted">No returns found.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load returns: ${error.message}</div>`;
    }
}

function openReturnModal() {
    document.getElementById('returnForm').reset();
    returnSaleData = null;
    returnItems = [];
    document.getElementById('returnSearchResults').innerHTML = '';
    document.getElementById('returnItemsContainer').innerHTML = '<p class="text-muted text-center">Search for a sale invoice first.</p>';
    document.getElementById('returnSummary').innerHTML = '';
    const btn = document.getElementById('returnSaveBtn');
    if (btn) btn.disabled = true;
    new bootstrap.Modal(document.getElementById('returnModal')).show();
}

let returnSearchTimeout = null;

async function searchSaleForReturn(query) {
    const resultsDiv = document.getElementById('returnSearchResults');
    if (!query || query.length < 2) {
        resultsDiv.innerHTML = '';
        returnSaleData = null;
        returnItems = [];
        document.getElementById('returnItemsContainer').innerHTML = '<p class="text-muted text-center">Search for a sale invoice first.</p>';
        document.getElementById('returnSummary').innerHTML = '';
        return;
    }

    clearTimeout(returnSearchTimeout);
    returnSearchTimeout = setTimeout(async () => {
        try {
            const sales = await api.getSales(200);
            const matches = sales.filter(s =>
                (s.invoice_number && s.invoice_number.toLowerCase().includes(query.toLowerCase())) ||
                (s.customer_name && s.customer_name.toLowerCase().includes(query.toLowerCase()))
            );

            if (!matches || matches.length === 0) {
                resultsDiv.innerHTML = '<p class="text-muted">No sales found matching this query</p>';
                return;
            }

            resultsDiv.innerHTML = `
                <div class="list-group" style="max-height:200px;overflow-y:auto;">
                    ${matches.map(s => `
                        <button type="button" class="list-group-item list-group-item-action"
                            onclick="selectSaleForReturn(${s.id}, '${(s.invoice_number || '').replace(/'/g, "\\'")}')">
                            <strong>${s.invoice_number || 'Sale #' + s.id}</strong>
                            <small class="text-muted ms-2">${s.customer_name || 'Walk-in'} - ${formatMoney(s.total_amount || 0)}</small>
                        </button>
                    `).join('')}
                </div>
            `;
        } catch (e) {
            resultsDiv.innerHTML = '<p class="text-danger">Error searching sales</p>';
        }
    }, 300);
}

async function selectSaleForReturn(saleId, invoiceNumber) {
    document.getElementById('returnSearchResults').innerHTML = '';
    document.getElementById('return_invoice_search').value = invoiceNumber;

    try {
        const sale = await api.getSale(saleId);
        returnSaleData = sale;
        returnItems = [];

        const items = sale.items || [];
        if (items.length === 0) {
            document.getElementById('returnItemsContainer').innerHTML = '<p class="text-warning">This sale has no items to return.</p>';
            document.getElementById('returnSaveBtn').disabled = true;
            return;
        }

        document.getElementById('returnItemsContainer').innerHTML = `
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th><input type="checkbox" id="returnSelectAll" onchange="toggleAllReturnItems(this.checked)"></th>
                        <th data-i18n="medicine">Medicine</th>
                        <th data-i18n="quantity">Qty Sold</th>
                        <th data-i18n="price">Price</th>
                        <th data-i18n="returnQty">Return Qty</th>
                        <th data-i18n="reason">Reason</th>
                        <th data-i18n="condition">Condition</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map((item, idx) => `
                        <tr>
                            <td><input type="checkbox" class="return-item-check" data-idx="${idx}" onchange="updateReturnSummary()"></td>
                            <td>${item.medicine_name || 'Medicine #' + item.medicine_id}</td>
                            <td>${item.quantity}</td>
                            <td>${formatMoney(item.selling_price || 0)}</td>
                            <td><input type="number" min="1" max="${item.quantity}" value="1" class="form-control form-control-sm return-qty" style="width:70px;" data-idx="${idx}" onchange="updateReturnSummary()"></td>
                            <td><input type="text" class="form-control form-control-sm return-reason" style="width:120px;" data-idx="${idx}" placeholder="Reason"></td>
                            <td>
                                <select class="form-select form-select-sm return-condition" style="width:100px;" data-idx="${idx}">
                                    <option value="good">Good</option>
                                    <option value="damaged">Damaged</option>
                                    <option value="expired">Expired</option>
                                </select>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        document.getElementById('returnSaveBtn').disabled = false;
        updateReturnSummary();
    } catch (error) {
        SwalAlert.error('Failed to load sale details: ' + error.message);
    }
}

function toggleAllReturnItems(checked) {
    document.querySelectorAll('.return-item-check').forEach(cb => cb.checked = checked);
    updateReturnSummary();
}

function updateReturnSummary() {
    const checkboxes = document.querySelectorAll('.return-item-check');
    const items = returnSaleData?.items || [];
    let totalRefund = 0;
    let selectedCount = 0;

    checkboxes.forEach(cb => {
        if (cb.checked) {
            const idx = parseInt(cb.dataset.idx);
            const item = items[idx];
            if (!item) return;
            const qtyInput = document.querySelector(`.return-qty[data-idx="${idx}"]`);
            const qty = parseInt(qtyInput?.value) || 1;
            const maxQty = item.quantity || 1;
            if (qty > maxQty) qtyInput.value = maxQty;
            const actualQty = Math.min(qty, maxQty);
            totalRefund += actualQty * (item.selling_price || 0);
            selectedCount++;
        }
    });

    const summaryDiv = document.getElementById('returnSummary');
    if (selectedCount > 0) {
        summaryDiv.innerHTML = `
            <div class="alert alert-info py-2 mb-0">
                <strong>${selectedCount}</strong> item(s) selected — Total Refund: <strong>${formatMoney(totalRefund)}</strong>
            </div>
        `;
    } else {
        summaryDiv.innerHTML = '';
    }
}

async function saveReturn() {
    if (!returnSaleData) {
        SwalAlert.warning('Please select a sale invoice!');
        return;
    }

    const checkboxes = document.querySelectorAll('.return-item-check:checked');
    if (checkboxes.length === 0) {
        SwalAlert.warning('Please select at least one item to return!');
        return;
    }

    const items = [];
    checkboxes.forEach(cb => {
        const idx = parseInt(cb.dataset.idx);
        const saleItem = returnSaleData.items[idx];
        if (!saleItem) return;
        const qty = parseInt(document.querySelector(`.return-qty[data-idx="${idx}"]`)?.value) || 1;
        const reason = document.querySelector(`.return-reason[data-idx="${idx}"]`)?.value || '';
        const condition = document.querySelector(`.return-condition[data-idx="${idx}"]`)?.value || 'good';
        items.push({
            sale_item_id: saleItem.id,
            medicine_id: saleItem.medicine_id,
            quantity: qty,
            reason: reason,
            condition: condition
        });
    });

    const data = {
        sale_id: returnSaleData.id,
        items: items,
        notes: document.getElementById('return_notes')?.value || null
    };

    const btn = document.getElementById('returnSaveBtn');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...'; }

    try {
        await api.createReturn(data);
        bootstrap.Modal.getInstance(document.getElementById('returnModal')).hide();
        SwalAlert.success('Return processed successfully!');
        renderReturns();
    } catch (error) {
        SwalAlert.error(error.message);
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-save"></i> Process Return'; }
    }
}

console.log('Returns module loaded');
