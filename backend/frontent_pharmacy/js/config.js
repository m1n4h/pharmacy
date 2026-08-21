// ============================================
// FRONTEND CONFIGURATION
// ============================================
// apiBaseUrl:
//   - '' (tupu)       => frontend na backend ziko kwenye domain moja (same-origin).
//                        Inatumika mfumo unaposerved na backend yenyewe (production).
//   - 'http://x:8000' => frontend iko tofauti (mf. Amplify), weka URL kamili ya backend
// ============================================

window.APP_CONFIG = {
    apiBaseUrl: '',
    defaultCurrency: 'TZS',
    currencySymbol: 'TSh',
    currencyRates: { TZS: 1.0 }
};

// ============================================
// MONEY FORMATTING (TZS by default)
// ============================================
function formatMoney(amount) {
    const n = Number(amount) || 0;
    const sym = (window.APP_CONFIG && window.APP_CONFIG.currencySymbol) || 'TSh';
    return sym + ' ' + n.toLocaleString('en-US', { maximumFractionDigits: 0 });
}

// Convert a foreign-currency amount to TZS using stored rates
function convertToTZS(amount, currencyCode) {
    const n = Number(amount) || 0;
    const code = (currencyCode || 'TZS').toUpperCase();
    if (code === 'TZS') return n;
    const rates = (window.APP_CONFIG && window.APP_CONFIG.currencyRates) || {};
    const rate = rates[code] || 1;
    return n * rate;
}

// Format a foreign-currency amount with its symbol and TZS equivalent
function formatForeign(amount, currencyCode) {
    const n = Number(amount) || 0;
    const code = (currencyCode || 'TZS').toUpperCase();
    if (code === 'TZS') return formatMoney(n);
    const symbols = { USD: '$', ZMW: 'K', EUR: '€', GBP: '£', KES: 'KSh' };
    const sym = symbols[code] || code;
    const tzs = convertToTZS(n, code);
    return `${sym} ${n.toLocaleString('en-US')} ≈ ${formatMoney(tzs)}`;
}
