// ============================================
// SETTINGS MODULE
// ============================================

async function renderSettings() {
    const content = document.getElementById('pageContent');
    try {
        const [settingsRes, currenciesRes] = await Promise.all([
            api.getSettings().catch(() => null),
            api.getCurrencies().catch(() => null)
        ]);
        const s = settingsRes?.data || {};
        const currencies = currenciesRes?.data?.items || [];

        content.innerHTML = `
            <div class="row">
                <div class="col-lg-7 mb-4">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <i class="fas fa-cog me-2"></i>System Settings
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Pharmacy Name *</label>
                                <input type="text" id="set_pharmacy_name" class="form-control" value="${s.pharmacy_name || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Address</label>
                                <input type="text" id="set_address" class="form-control" value="${s.address || ''}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Phone</label>
                                <input type="text" id="set_phone" class="form-control" value="${s.phone || ''}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" id="set_email" class="form-control" value="${s.email || ''}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Invoice Footer</label>
                                <textarea id="set_invoice_footer" class="form-control" rows="2">${s.invoice_footer || ''}</textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Default Currency</label>
                                <select id="set_default_currency" class="form-control">
                                    ${currencies.map(c => `
                                        <option value="${c.code}" ${(s.default_currency || 'TZS') === c.code ? 'selected' : ''}>
                                            ${c.code} - ${c.name || ''}
                                        </option>
                                    `).join('') || '<option value="TZS">TZS</option>'}
                                </select>
                                <small class="text-muted">Fedha za kigeni zitabadilishwa kuwa TZS kulingana na exchange rates.</small>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Expiry Warning (days before expiry)</label>
                                <input type="number" id="set_expiry_warning_days" class="form-control" min="1" value="${s.expiry_warning_days || 30}">
                                <small class="text-muted">Dawa zitakazoisha kati ya siku hizi zitaonyeshwa kama "Expiring Soon".</small>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Low Stock Threshold</label>
                                <input type="number" id="set_low_stock_threshold" class="form-control" min="0" value="${s.low_stock_threshold || 10}">
                                <small class="text-muted">Dawa zilizo chini ya kiasi hiki zitaonyeshwa kama "Low Stock".</small>
                            </div>
                            <button class="btn btn-primary w-100" onclick="saveSettings()">
                                <i class="fas fa-save"></i> Save Settings
                            </button>
                        </div>
                    </div>
                </div>
                <div class="col-lg-5 mb-4">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <i class="fas fa-coins me-2"></i>Exchange Rates (1 unit = TZS)
                        </div>
                        <div class="card-body">
                            <div id="currencyRatesList">
                                ${currencies.map(c => `
                                    <div class="row align-items-center mb-2">
                                        <div class="col-4">
                                            <strong>${c.code}</strong>
                                            <small class="d-block text-muted">${c.symbol || ''}</small>
                                        </div>
                                        <div class="col-8">
                                            <input type="number" step="0.0001" min="0" class="form-control"
                                                   id="rate_${c.code}" value="${c.rate_to_tzs}" ${c.code === 'TZS' ? 'disabled' : ''}>
                                        </div>
                                    </div>
                                `).join('') || '<p class="text-muted">No currencies</p>'}
                            </div>
                            <button class="btn btn-success w-100 mt-2" onclick="saveCurrencyRates()">
                                <i class="fas fa-save"></i> Save Exchange Rates
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load settings: ${error.message}</div>`;
    }
}

async function saveSettings() {
    const data = {
        pharmacy_name: document.getElementById('set_pharmacy_name').value,
        address: document.getElementById('set_address').value,
        phone: document.getElementById('set_phone').value,
        email: document.getElementById('set_email').value,
        invoice_footer: document.getElementById('set_invoice_footer').value,
        default_currency: document.getElementById('set_default_currency').value,
        expiry_warning_days: parseInt(document.getElementById('set_expiry_warning_days').value) || 30,
        low_stock_threshold: parseInt(document.getElementById('set_low_stock_threshold').value) || 10
    };
    if (!data.pharmacy_name) {
        alert('Pharmacy name inahitajika!');
        return;
    }
    try {
        await api.updateSettings(data);
        if (window.APP_CONFIG) {
            window.APP_CONFIG.defaultCurrency = data.default_currency;
        }
        alert('Settings saved successfully!');
        await loadAppConfig();
        renderSettings();
    } catch (error) {
        alert('Failed to save settings: ' + error.message);
    }
}

async function saveCurrencyRates() {
    const rates = [];
    document.querySelectorAll('#currencyRatesList input[id^="rate_"]').forEach(inp => {
        const code = inp.id.replace('rate_', '');
        if (code === 'TZS') return;
        const val = parseFloat(inp.value);
        if (!isNaN(val) && val > 0) {
            rates.push({ code, rate_to_tzs: val });
        }
    });
    if (rates.length === 0) {
        alert('Hakuna exchange rates za kuhifadhi.');
        return;
    }
    try {
        const res = await api.updateCurrencyRates(rates);
        if (res && res.success === false) {
            alert('Imeshindikana: ' + (res.message || 'Unknown error'));
            return;
        }
        alert('Exchange rates zimehifadhiwa!');
        await loadAppConfig();
    } catch (error) {
        alert('Failed to save rates: ' + error.message);
    }
}

console.log('Settings module loaded');