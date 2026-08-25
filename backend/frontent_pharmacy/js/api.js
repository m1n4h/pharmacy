// ============================================
// API SERVICE LAYER - COMPLETE
// ============================================

// API URL inatokana na config.js — '' (tupu) inamaanisha same-origin (frontend inaserved na backend).
// Kwa frontend tofauti (mf. Amplify), weka URL kamili kwenye config.js.
const API_BASE_URL = (window.APP_CONFIG && window.APP_CONFIG.apiBaseUrl) || '';

class PharmacyAPI {
    constructor() {
        this.token = localStorage.getItem('accessToken');
        this._refreshing = null;
        console.log('API initialized');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('accessToken', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('accessToken');
    }

    getHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    _isAuthEndpoint(url) {
        return url.includes('/auth/login') || url.includes('/auth/refresh');
    }

    // Refresh access token using the httpOnly refresh_token cookie.
    // Returns true on success, false otherwise.
    async _refreshAccessToken() {
        if (this._refreshing) return this._refreshing;
        this._refreshing = (async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include'
                });
                const data = await response.json();
                if (response.ok && data.data?.access_token) {
                    this.setToken(data.data.access_token);
                    return true;
                }
                this.clearToken();
                return false;
            } catch (e) {
                this.clearToken();
                return false;
            } finally {
                this._refreshing = null;
            }
        })();
        return this._refreshing;
    }

    // Fetch wrapper: attaches headers, auto-refreshes access token on 401 and retries once.
    async _authFetch(url, options = {}) {
        let response = await fetch(url, { ...options, headers: { ...this.getHeaders(), ...(options.headers || {}) } });

        if (response.status === 401 && this.token && !this._isAuthEndpoint(url)) {
            const refreshed = await this._refreshAccessToken();
            if (refreshed) {
                response = await fetch(url, { ...options, headers: { ...this.getHeaders(), ...(options.headers || {}) } });
            } else {
                // Session expired - back to login
                window.location.reload();
            }
        }
        return this.handleResponse(response);
    }

    async handleResponse(response) {
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = typeof errorData.detail === 'string' ? errorData.detail : 
                                  errorData.detail.message || errorData.detail.error || JSON.stringify(errorData.detail);
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }
            } catch (e) {}
            throw new Error(errorMessage);
        }
        return response.json();
    }

    // Extracts list items from API response (handles items / data / raw array)
    _extractItems(data) {
        return data?.data?.items || data?.data || data || [];
    }

    // Extracts a single object from API response
    _extractData(data) {
        return data?.data || data || {};
    }

    // ========== AUTH ==========
    async login(email, password) {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        const data = await this.handleResponse(response);
        if (data.data?.access_token) this.setToken(data.data.access_token);
        return data;
    }

    async getMe() {
        return this._authFetch(`${API_BASE_URL}/auth/me`);
    }

    async logout() {
        try {
            return await this._authFetch(`${API_BASE_URL}/auth/logout`, { method: 'POST' });
        } finally {
            this.clearToken();
        }
    }

    // ========== MEDICINES ==========
    async getMedicines(limit = 100) {
        return this._extractItems(await this._authFetch(`${API_BASE_URL}/medicines/?limit=${limit}`));
    }

    async createMedicine(data) {
        return this._authFetch(`${API_BASE_URL}/medicines/`, { method: 'POST', body: JSON.stringify(data) });
    }

    async updateMedicine(id, data) {
        return this._authFetch(`${API_BASE_URL}/medicines/${id}`, { method: 'PUT', body: JSON.stringify(data) });
    }

    async getMedicine(id) {
        return this._extractData(await this._authFetch(`${API_BASE_URL}/medicines/${id}`));
    }

    async deleteMedicine(id) {
        return this._authFetch(`${API_BASE_URL}/medicines/${id}`, { method: 'DELETE' });
    }

    // ========== INVENTORY ==========
    async getInventory(limit = 100) {
        return this._extractItems(await this._authFetch(`${API_BASE_URL}/inventory/?limit=${limit}`));
    }

    async getLowStock() {
        return this._extractItems(await this._authFetch(`${API_BASE_URL}/inventory/low`));
    }

    async getNearExpiry() {
        return this._extractItems(await this._authFetch(`${API_BASE_URL}/inventory/near-expiry`));
    }

    async getExpired() {
        return this._extractItems(await this._authFetch(`${API_BASE_URL}/inventory/expired`));
    }

    async getMedicineStock(medicineId) {
        return this._extractData(await this._authFetch(`${API_BASE_URL}/inventory/medicine/${medicineId}`));
    }

    // ========== SALES ==========
    async getSales(limit = 100) {
        return this._extractItems(await this._authFetch(`${API_BASE_URL}/sales/?limit=${limit}`));
    }

    async createSale(data) {
        return this._authFetch(`${API_BASE_URL}/sales/create`, { method: 'POST', body: JSON.stringify(data) });
    }

    async getSale(id) {
        return this._extractData(await this._authFetch(`${API_BASE_URL}/sales/${id}`));
    }
    async updateSale(id, data) {
        return this._authFetch(`${API_BASE_URL}/sales/${id}`, { method: 'PUT', body: JSON.stringify(data) });
    }
    async deleteSale(id) {
        return this._authFetch(`${API_BASE_URL}/sales/${id}`, { method: 'DELETE' });
    }

    async getPosMedicines(search = '', limit = 20) {
        const url = `${API_BASE_URL}/sales/pos/medicines?search=${encodeURIComponent(search)}&limit=${limit}`;
        return this._extractItems(await this._authFetch(url));
    }

    // ========== SALES UPLOAD ==========
    async uploadSalesDocument(file) {
        const formData = new FormData();
        formData.append('file', file);
        return this._authFetch(`${API_BASE_URL}/uploads/upload-document`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${this.token}` },
            body: formData
        });
    }

    async processUpload(uploadId) {
        return this._authFetch(`${API_BASE_URL}/uploads/process-upload/${uploadId}`, { method: 'POST' });
    }

    async getUploadLogs(page = 1, limit = 20) {
        return this._extractData(await this._authFetch(`${API_BASE_URL}/uploads/upload-logs?page=${page}&limit=${limit}`));
    }

    // ========== PURCHASES ==========
    async getPurchases(limit = 100) {
        return this._extractItems(await this._authFetch(`${API_BASE_URL}/purchases/?limit=${limit}`));
    }

    async createPurchase(data) {
        return this._authFetch(`${API_BASE_URL}/purchases/create`, { method: 'POST', body: JSON.stringify(data) });
    }

    async getPurchase(id) {
        return this._extractData(await this._authFetch(`${API_BASE_URL}/purchases/${id}`));
    }

    // ========== SUPPLIERS ==========
    async getSuppliers(limit = 100, search = '') {
        const qs = search ? `limit=${limit}&search=${encodeURIComponent(search)}` : `limit=${limit}`;
        return this._extractItems(await this._authFetch(`${API_BASE_URL}/suppliers/?${qs}`));
    }

    async searchMedicines(search = '', limit = 10) {
        return this._extractItems(await this._authFetch(`${API_BASE_URL}/medicines/?search=${encodeURIComponent(search)}&limit=${limit}`));
    }

    async createSupplier(data) {
        return this._authFetch(`${API_BASE_URL}/suppliers/create`, { method: 'POST', body: JSON.stringify(data) });
    }

    // ========== DASHBOARD ==========
    async getDashboardTotals() {
        return this._extractData(await this._authFetch(`${API_BASE_URL}/dashboard/`));
    }

    async getDashboardToday() {
        return this._extractData(await this._authFetch(`${API_BASE_URL}/dashboard/today`));
    }

    async getDashboardInventory() {
        return this._extractData(await this._authFetch(`${API_BASE_URL}/dashboard/inventory`));
    }

    // ========== REPORTS ==========
    async getSalesReportDaily(date) {
        return this._extractData(await this._authFetch(`${API_BASE_URL}/reports/sales/daily?date=${date}`));
    }

    async getSalesReportMonthly(year, month) {
        return this._extractData(await this._authFetch(`${API_BASE_URL}/reports/sales/monthly?year=${year}&month=${month}`));
    }

    async getSalesReportLast7Days() {
        return this._extractItems(await this._authFetch(`${API_BASE_URL}/reports/sales/sales-7-days`));
    }

    // ========== BATCHES ==========
    async getBatches(medicineId) {
        const url = medicineId ? `${API_BASE_URL}/batches/medicine/${medicineId}` : `${API_BASE_URL}/batches/`;
        return this._extractItems(await this._authFetch(url));
    }

    async createBatch(data) {
        return this._authFetch(`${API_BASE_URL}/batches/create`, { method: 'POST', body: JSON.stringify(data) });
    }

    // ========== USERS ==========
    async getUsers() {
        return this._authFetch(`${API_BASE_URL}/users/`);
    }

    async createUser(data) {
        return this._authFetch(`${API_BASE_URL}/users/create`, { method: 'POST', body: JSON.stringify(data) });
    }

    async toggleUserActive(userId) {
        return this._authFetch(`${API_BASE_URL}/users/${userId}/toggle-active`, { method: 'POST' });
    }

    async deleteUser(userId) {
        return this._authFetch(`${API_BASE_URL}/users/${userId}`, { method: 'DELETE' });
    }

    // ========== CURRENCIES ==========
    async getCurrencies() {
        return this._authFetch(`${API_BASE_URL}/currencies/`);
    }

    async updateCurrencyRates(rates) {
        return this._authFetch(`${API_BASE_URL}/currencies/update`, { method: 'PUT', body: JSON.stringify({ rates }) });
    }

    async convertCurrency(amount, currencyCode) {
        return this._authFetch(`${API_BASE_URL}/currencies/convert`, {
            method: 'POST', body: JSON.stringify({ amount, currency_code: currencyCode })
        });
    }

    // ========== AI MEDICINE SUGGESTION ==========
    async aiSuggestMedicine(name, strength = '', category = '', genericName = '') {
        return this._authFetch(`${API_BASE_URL}/medicines/ai-suggest`, {
            method: 'POST', body: JSON.stringify({
                name, strength, category, generic_name: genericName
            })
        });
    }

    // ========== SETTINGS ==========
    async getSettings() {
        return this._authFetch(`${API_BASE_URL}/settings/`);
    }

    async updateSettings(data) {
        return this._authFetch(`${API_BASE_URL}/settings/`, { method: 'PUT', body: JSON.stringify(data) });
    }

    // ========== ACTIVITIES ==========
    async getActivities(page = 1, limit = 50, module = '', action = '', search = '') {
        let url = `${API_BASE_URL}/activities/?page=${page}&limit=${limit}`;
        if (module) url += `&module=${encodeURIComponent(module)}`;
        if (action) url += `&action=${encodeURIComponent(action)}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        return this._authFetch(url);
    }

    // ========== PRESCRIPTIONS ==========
    async getPrescriptions(status = '', search = '') {
        let url = `${API_BASE_URL}/prescriptions/?limit=100`;
        if (status) url += `&status=${encodeURIComponent(status)}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        return this._authFetch(url);
    }

    async createPrescription(data) {
        return this._authFetch(`${API_BASE_URL}/prescriptions/create`, { method: 'POST', body: JSON.stringify(data) });
    }

    async getPrescription(id) {
        return this._authFetch(`${API_BASE_URL}/prescriptions/${id}`);
    }

    async dispensePrescription(id) {
        return this._authFetch(`${API_BASE_URL}/prescriptions/${id}/dispense`, { method: 'POST' });
    }

    async cancelPrescription(id) {
        return this._authFetch(`${API_BASE_URL}/prescriptions/${id}/cancel`, { method: 'POST' });
    }
    async updatePrescription(id, data) {
        return this._authFetch(`${API_BASE_URL}/prescriptions/${id}`, { method: 'PUT', body: JSON.stringify(data) });
    }
    async deletePrescription(id) {
        return this._authFetch(`${API_BASE_URL}/prescriptions/${id}`, { method: 'DELETE' });
    }

    // ========== PERMISSIONS ==========
    async getMyPermissions() {
        return this._authFetch(`${API_BASE_URL}/permissions/mine`);
    }

    async getAllPermissions() {
        return this._authFetch(`${API_BASE_URL}/permissions/`);
    }

    async updatePermissions(data) {
        return this._authFetch(`${API_BASE_URL}/permissions/update`, { method: 'POST', body: JSON.stringify(data) });
    }

    // ========== EXPENSES ==========
    async createExpense(data) {
        return this._authFetch(`${API_BASE_URL}/expenses/create`, { method: 'POST', body: JSON.stringify(data) });
    }
    async listExpenses(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this._authFetch(`${API_BASE_URL}/expenses/?${qs}`);
    }
    async getExpenseSummary(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this._authFetch(`${API_BASE_URL}/expenses/summary?${qs}`);
    }
    async deleteExpense(id) {
        return this._authFetch(`${API_BASE_URL}/expenses/${id}`, { method: 'DELETE' });
    }
    async updateExpense(id, data) {
        return this._authFetch(`${API_BASE_URL}/expenses/${id}`, { method: 'PUT', body: JSON.stringify(data) });
    }

    // ========== REPORTS ==========
    async getProfitLoss(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this._authFetch(`${API_BASE_URL}/reports/profit-loss?${qs}`);
    }
    async getSalesReport(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this._authFetch(`${API_BASE_URL}/reports/sales?${qs}`);
    }
    async getInventoryReport() {
        return this._authFetch(`${API_BASE_URL}/reports/inventory`);
    }
    async getPurchasesReport(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this._authFetch(`${API_BASE_URL}/reports/purchases?${qs}`);
    }
    async getExpiryReport() {
        return this._authFetch(`${API_BASE_URL}/reports/expiry`);
    }
    async getTopSelling(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this._authFetch(`${API_BASE_URL}/reports/top-selling?${qs}`);
    }
    async getExpenseTrending(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this._authFetch(`${API_BASE_URL}/reports/expense-trending?${qs}`);
    }
    async exportReport(reportType, params = {}) {
        const qs = new URLSearchParams(params).toString();
        let response = await fetch(`${API_BASE_URL}/reports/export/${reportType}?${qs}`, { headers: this.getHeaders() });
        if (!response.ok) throw new Error('Export failed');
        return response.blob();
    }

    // ========== EXPIRY ==========
    async getExpiryDashboard() {
        return this._authFetch(`${API_BASE_URL}/expiry/dashboard`);
    }
    async getExpiryList(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this._authFetch(`${API_BASE_URL}/expiry/?${qs}`);
    }
    async createExpiryAction(data) {
        return this._authFetch(`${API_BASE_URL}/expiry/action`, { method: 'POST', body: JSON.stringify(data) });
    }
    async getExpiryActions() {
        return this._authFetch(`${API_BASE_URL}/expiry/actions`);
    }

    // ========== NOTIFICATIONS ==========
    async getNotifications(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this._authFetch(`${API_BASE_URL}/notifications/?${qs}`);
    }
    async markNotificationRead(id) {
        return this._authFetch(`${API_BASE_URL}/notifications/${id}/read`, { method: 'POST' });
    }
    async markAllNotificationsRead() {
        return this._authFetch(`${API_BASE_URL}/notifications/read-all`, { method: 'POST' });
    }
    async deleteNotification(id) {
        return this._authFetch(`${API_BASE_URL}/notifications/${id}`, { method: 'DELETE' });
    }

    // ========== BACKUP ==========
    async createBackup() {
        return this._authFetch(`${API_BASE_URL}/backup/create`, { method: 'POST' });
    }
    async listBackups() {
        return this._authFetch(`${API_BASE_URL}/backup/list`);
    }
    async restoreBackup(filename) {
        return this._authFetch(`${API_BASE_URL}/backup/restore`, { method: 'POST', body: JSON.stringify({ filename }) });
    }

    // ========== INVOICE ==========
    async downloadInvoice(saleId) {
        let response = await fetch(`${API_BASE_URL}/invoice/sale/${saleId}`, { headers: this.getHeaders() });
        if (response.status === 401 && this.token) {
            const refreshed = await this._refreshAccessToken();
            if (refreshed) {
                response = await fetch(`${API_BASE_URL}/invoice/sale/${saleId}`, { headers: this.getHeaders() });
            } else {
                window.location.reload();
            }
        }
        if (!response.ok) throw new Error('Failed to download invoice');
        return response.blob();
    }

    // ========== BRANCHES ==========
    async createBranch(data) { return this._authFetch(`${API_BASE_URL}/branches/create`, { method: 'POST', body: JSON.stringify(data) }); }
    async getBranches(search = '') { const qs = search ? `?search=${encodeURIComponent(search)}` : ''; return this._extractItems(await this._authFetch(`${API_BASE_URL}/branches/${qs}`)); }
    async updateBranch(id, data) { return this._authFetch(`${API_BASE_URL}/branches/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }
    async deleteBranch(id) { return this._authFetch(`${API_BASE_URL}/branches/${id}`, { method: 'DELETE' }); }

    // ========== CATEGORIES ==========
    async createCategory(data) { return this._authFetch(`${API_BASE_URL}/categories/create`, { method: 'POST', body: JSON.stringify(data) }); }
    async getCategories() { return this._extractItems(await this._authFetch(`${API_BASE_URL}/categories/`)); }
    async updateCategory(id, data) { return this._authFetch(`${API_BASE_URL}/categories/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }
    async deleteCategory(id) { return this._authFetch(`${API_BASE_URL}/categories/${id}`, { method: 'DELETE' }); }

    // ========== MANUFACTURERS ==========
    async createManufacturer(data) { return this._authFetch(`${API_BASE_URL}/manufacturers/create`, { method: 'POST', body: JSON.stringify(data) }); }
    async getManufacturers() { return this._extractItems(await this._authFetch(`${API_BASE_URL}/manufacturers/`)); }
    async updateManufacturer(id, data) { return this._authFetch(`${API_BASE_URL}/manufacturers/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }
    async deleteManufacturer(id) { return this._authFetch(`${API_BASE_URL}/manufacturers/${id}`, { method: 'DELETE' }); }

    // ========== CUSTOMERS ==========
    async createCustomer(data) { return this._authFetch(`${API_BASE_URL}/customers/create`, { method: 'POST', body: JSON.stringify(data) }); }
    async getCustomers(search = '') { const qs = search ? `?search=${encodeURIComponent(search)}` : ''; return this._extractItems(await this._authFetch(`${API_BASE_URL}/customers/${qs}`)); }
    async getCustomer(id) { return this._extractData(await this._authFetch(`${API_BASE_URL}/customers/${id}`)); }
    async updateCustomer(id, data) { return this._authFetch(`${API_BASE_URL}/customers/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }
    async deleteCustomer(id) { return this._authFetch(`${API_BASE_URL}/customers/${id}`, { method: 'DELETE' }); }

    // ========== STOCK ADJUSTMENTS ==========
    async createStockAdjustment(data) { return this._authFetch(`${API_BASE_URL}/stock-adjustments/create`, { method: 'POST', body: JSON.stringify(data) }); }
    async getStockAdjustments(status = '') { const qs = status ? `?status=${status}` : ''; return this._extractItems(await this._authFetch(`${API_BASE_URL}/stock-adjustments/${qs}`)); }
    async approveStockAdjustment(id) { return this._authFetch(`${API_BASE_URL}/stock-adjustments/${id}/approve`, { method: 'POST' }); }
    async rejectStockAdjustment(id) { return this._authFetch(`${API_BASE_URL}/stock-adjustments/${id}/reject`, { method: 'POST' }); }

    // ========== RETURNS ==========
    async createReturn(data) { return this._authFetch(`${API_BASE_URL}/returns/create`, { method: 'POST', body: JSON.stringify(data) }); }
    async getReturns() { return this._extractItems(await this._authFetch(`${API_BASE_URL}/returns/`)); }

    // ========== STOCK TRANSFERS ==========
    async createStockTransfer(data) { return this._authFetch(`${API_BASE_URL}/stock-transfers/create`, { method: 'POST', body: JSON.stringify(data) }); }
    async getStockTransfers(status = '') { const qs = status ? `?status=${status}` : ''; return this._extractItems(await this._authFetch(`${API_BASE_URL}/stock-transfers/${qs}`)); }
    async approveStockTransfer(id) { return this._authFetch(`${API_BASE_URL}/stock-transfers/${id}/approve`, { method: 'POST' }); }
    async rejectStockTransfer(id) { return this._authFetch(`${API_BASE_URL}/stock-transfers/${id}/reject`, { method: 'POST' }); }

    // ========== SUPPLIER (update/delete) ==========
    async updateSupplier(id, data) { return this._authFetch(`${API_BASE_URL}/suppliers/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }
    async deleteSupplier(id) { return this._authFetch(`${API_BASE_URL}/suppliers/${id}`, { method: 'DELETE' }); }

    // ========== PURCHASE (update/delete) ==========
    async updatePurchase(id, data) { return this._authFetch(`${API_BASE_URL}/purchases/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }
    async deletePurchase(id) { return this._authFetch(`${API_BASE_URL}/purchases/${id}`, { method: 'DELETE' }); }

    // ========== ADVANCED REPORTS ==========
    async getSlowMoving(days = 30) { return this._extractData(await this._authFetch(`${API_BASE_URL}/reports/slow-moving?days=${days}`)); }
    async getReorderSuggestions() { return this._extractData(await this._authFetch(`${API_BASE_URL}/reports/reorder-suggestions`)); }
    async getOverstock() { return this._extractData(await this._authFetch(`${API_BASE_URL}/reports/overstock`)); }
    async getSupplierPerformance(params = {}) { const qs = new URLSearchParams(params).toString(); return this._extractData(await this._authFetch(`${API_BASE_URL}/reports/supplier-performance?${qs}`)); }
}

const api = new PharmacyAPI();
console.log('API Service loaded');