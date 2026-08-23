// ============================================
// EXPENSES MODULE
// ============================================

let editingExpenseId = null;

async function renderExpenses() {
    const content = document.getElementById('pageContent');
    try {
        const [listRes, sumRes] = await Promise.all([
            api.listExpenses(),
            api.getExpenseSummary()
        ]);
        const expenses = listRes?.data?.items || [];
        const summary = sumRes?.data || { total: 0, by_category: {} };

        const catCards = Object.entries(summary.by_category || {})
            .sort((a, b) => b[1] - a[1])
            .map(([cat, amt]) => `
                <div class="stat-card" style="min-width:160px;">
                    <div class="stat-icon bg-warning"><i class="fas fa-tag"></i></div>
                    <div class="stat-info"><div class="stat-value">${formatMoney(amt)}</div><div class="stat-label">${cat}</div></div>
                </div>
            `).join('') || '<p class="text-muted">No expenses yet.</p>';

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-success" onclick="openExpenseModal()">
                    <i class="fas fa-plus"></i> Add Expense
                </button>
                <span class="text-muted">Total (all): <strong>${formatMoney(summary.total)}</strong></span>
            </div>
            <div class="d-flex flex-wrap gap-3 mb-4">${catCards}</div>
            <div class="table-container">
                <table class="table table-hover">
                    <thead>
                        <tr><th>Date</th><th>Category</th><th>Description</th><th>Payment</th><th>Amount</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                        ${expenses.map(e => `
                            <tr>
                                <td>${e.date}</td>
                                <td><span class="badge bg-warning text-dark">${e.category}</span></td>
                                <td>${e.description || '-'}</td>
                                <td>${e.payment_method || '-'}</td>
                                <td><strong>${formatMoney(e.amount)}</strong></td>
                                <td class="text-nowrap">
                                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editExpense(${e.id})">Edit</button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteExpense(${e.id})">Delete</button>
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="6" class="text-center text-muted">No expenses recorded.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load expenses: ${error.message}</div>`;
    }
}

function openExpenseModal() {
    editingExpenseId = null;
    document.getElementById('addExpenseForm').reset();
    document.getElementById('exp_date').value = new Date().toISOString().slice(0, 10);
    const btn = document.getElementById('expSaveBtn');
    if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Save Expense';
    new bootstrap.Modal(document.getElementById('addExpenseModal')).show();
}

async function editExpense(id) {
    try {
        const res = await api.listExpenses({});
        const e = (res.data.items || []).find(x => x.id === id);
        if (!e) { SwalAlert.error('Expense not found'); return; }
        editingExpenseId = id;
        document.getElementById('exp_category').value = e.category;
        document.getElementById('exp_description').value = e.description || '';
        document.getElementById('exp_amount').value = e.amount;
        document.getElementById('exp_date').value = e.date;
        document.getElementById('exp_payment').value = e.payment_method || 'Cash';
        document.getElementById('exp_reference').value = e.reference || '';
        document.getElementById('exp_notes').value = e.notes || '';
        const btn = document.getElementById('expSaveBtn');
        if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Update Expense';
        new bootstrap.Modal(document.getElementById('addExpenseModal')).show();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function saveExpense() {
    const data = {
        category: document.getElementById('exp_category').value,
        description: document.getElementById('exp_description').value || null,
        amount: parseFloat(document.getElementById('exp_amount').value),
        date: document.getElementById('exp_date').value,
        payment_method: document.getElementById('exp_payment').value,
        reference: document.getElementById('exp_reference').value || null,
        notes: document.getElementById('exp_notes').value || null
    };
    if (!data.amount || data.amount <= 0 || !data.date) {
        SwalAlert.warning('Jaza kiasi na tarehe sahihi!');
        return;
    }
    try {
        if (editingExpenseId) {
            await api.updateExpense(editingExpenseId, data);
        } else {
            await api.createExpense(data);
        }
        bootstrap.Modal.getInstance(document.getElementById('addExpenseModal')).hide();
        editingExpenseId = null;
        renderExpenses();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function deleteExpense(id) {
    const result = await SwalAlert.confirm('Futa gharama hii?');
    if (!result.isConfirmed) return;
    try {
        await api.deleteExpense(id);
        renderExpenses();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Expenses module loaded');
