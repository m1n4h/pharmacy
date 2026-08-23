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
                            <i class="fas fa-cog me-2"></i>Pharmacy Profile
                        </div>
                        <div class="card-body">
                            <div class="row g-3">
                                <div class="col-md-8">
                                    <label class="form-label required">Pharmacy Name</label>
                                    <input type="text" id="set_pharmacy_name" class="form-control" value="${s.pharmacy_name || ''}" required>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">Registration No.</label>
                                    <input type="text" id="set_registration_number" class="form-control" value="${s.registration_number || ''}">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Region</label>
                                    <input type="text" id="set_region" class="form-control" value="${s.region || ''}">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">District</label>
                                    <input type="text" id="set_district" class="form-control" value="${s.district || ''}">
                                </div>
                                <div class="col-12">
                                    <label class="form-label">Address</label>
                                    <input type="text" id="set_address" class="form-control" value="${s.address || ''}">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Phone</label>
                                    <input type="text" id="set_phone" class="form-control" value="${s.phone || ''}">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Email</label>
                                    <input type="email" id="set_email" class="form-control" value="${s.email || ''}">
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card mt-3">
                        <div class="card-header bg-info text-white">
                            <i class="fas fa-sliders-h me-2"></i>System Configuration
                        </div>
                        <div class="card-body">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label">Default Currency</label>
                                    <select id="set_default_currency" class="form-select">
                                        ${currencies.map(c => `
                                            <option value="${c.code}" ${(s.default_currency || 'TZS') === c.code ? 'selected' : ''}>
                                                ${c.code} - ${c.name || ''}
                                            </option>
                                        `).join('') || '<option value="TZS">TZS</option>'}
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Tax/VAT Rate (%)</label>
                                    <input type="number" id="set_tax_rate" class="form-control" min="0" max="100" step="0.1" value="${s.tax_rate || 0}">
                                    <small class="text-muted">Applied to sales if > 0</small>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Expiry Warning (days)</label>
                                    <input type="number" id="set_expiry_warning_days" class="form-control" min="1" value="${s.expiry_warning_days || 30}">
                                    <small class="text-muted">Medicines expiring within this period shown as warnings</small>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Low Stock Threshold</label>
                                    <input type="number" id="set_low_stock_threshold" class="form-control" min="0" value="${s.low_stock_threshold || 10}">
                                    <small class="text-muted">Medicines below this quantity shown as low stock</small>
                                </div>
                                <div class="col-12">
                                    <label class="form-label">Invoice Footer</label>
                                    <textarea id="set_invoice_footer" class="form-control" rows="2">${s.invoice_footer || ''}</textarea>
                                </div>
                            </div>
                        </div>
                    </div>

                    <button class="btn btn-primary w-100 mt-3" onclick="saveSettings()">
                        <i class="fas fa-save me-1"></i>Save All Settings
                    </button>
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
        low_stock_threshold: parseInt(document.getElementById('set_low_stock_threshold').value) || 10,
        tax_rate: parseFloat(document.getElementById('set_tax_rate').value) || 0,
        registration_number: document.getElementById('set_registration_number').value,
        region: document.getElementById('set_region').value,
        district: document.getElementById('set_district').value,
    };
    if (!data.pharmacy_name) {
        SwalAlert.warning('Pharmacy name is required');
        return;
    }
    try {
        await api.updateSettings(data);
        if (window.APP_CONFIG) {
            window.APP_CONFIG.defaultCurrency = data.default_currency;
        }
        SwalAlert.success('Settings saved successfully!');
        await loadAppConfig();
        renderSettings();
    } catch (error) {
        SwalAlert.error('Failed to save settings: ' + error.message);
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
        SwalAlert.warning('No exchange rates to save');
        return;
    }
    try {
        const res = await api.updateCurrencyRates(rates);
        if (res && res.success === false) {
            SwalAlert.error('Failed: ' + (res.message || 'Unknown error'));
            return;
        }
        SwalAlert.success('Exchange rates saved!');
        await loadAppConfig();
    } catch (error) {
        SwalAlert.error('Failed to save rates: ' + error.message);
    }
}

console.log('Settings module loaded');
