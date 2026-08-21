// ============================================
// API SERVICE LAYER - FIXED
// ============================================

// Backend routes are at /auth, /medicines, /dashboard, etc. (no /api/v1 prefix)
// API URL inatokana na config.js — '' (tupu) inamaanisha same-origin (frontend inaserved na backend).
// Kwa frontend tofauti (mf. Amplify), weka URL kamili kwenye config.js.
const API_BASE_URL = (window.APP_CONFIG && window.APP_CONFIG.apiBaseUrl) || '';

class PharmacyAPI {
    constructor() {
        this.token = localStorage.getItem('accessToken');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('accessToken', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async handleResponse(response) {
        if (!response.ok) {
            let errorDetail = `HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    if (typeof errorData.detail === 'object' && errorData.detail.message) {
                        errorDetail = errorData.detail.message;
                    } else if (typeof errorData.detail === 'string') {
                        errorDetail = errorData.detail;
                    }
                } else if (errorData.message) {
                    errorDetail = errorData.message;
                }
            } catch (e) {
                // If response is not JSON
            }
            throw new Error(errorDetail);
        }
        return response.json();
    }

    // ============================================
    // AUTH ENDPOINTS
    // ============================================
    
    async login(email, password) {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        const data = await this.handleResponse(response);
        // Store token if present
        if (data.data && data.data.access_token) {
            this.setToken(data.data.access_token);
        }
        return data;
    }

    async getMe() {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: this.getHeaders(),
            credentials: 'include'
        });
        return this.handleResponse(response);
    }

    async logout() {
        const response = await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: this.getHeaders(),
            credentials: 'include'
        });
        this.clearToken();
        return this.handleResponse(response);
    }

    // ============================================
    // MEDICINES ENDPOINTS
    // ============================================
    
    async getMedicines() {
        const response = await fetch(`${API_BASE_URL}/medicines/`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data?.items || data.data || data || [];
    }

    async createMedicine(data) {
        const response = await fetch(`${API_BASE_URL}/medicines/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    async updateMedicine(id, data) {
        const response = await fetch(`${API_BASE_URL}/medicines/${id}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    async deleteMedicine(id) {
        const response = await fetch(`${API_BASE_URL}/medicines/${id}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    // ============================================
    // INVENTORY ENDPOINTS
    // ============================================
    
    async getInventory() {
        const response = await fetch(`${API_BASE_URL}/inventory/`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data?.items || data.data || data || [];
    }

    async getLowStock() {
        const response = await fetch(`${API_BASE_URL}/inventory/low`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data?.items || data.data || data || [];
    }

    async getNearExpiry() {
        const response = await fetch(`${API_BASE_URL}/inventory/near-expiry`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data?.items || data.data || data || [];
    }

    async getExpired() {
        const response = await fetch(`${API_BASE_URL}/inventory/expired`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data?.items || data.data || data || [];
    }

    // ============================================
    // SALES ENDPOINTS
    // ============================================
    
    async getSales() {
        const response = await fetch(`${API_BASE_URL}/sales/`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data?.items || data.data || data || [];
    }

    async createSale(data) {
        const response = await fetch(`${API_BASE_URL}/sales/create`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    // ============================================
    // PURCHASES ENDPOINTS
    // ============================================
    
    async getPurchases() {
        const response = await fetch(`${API_BASE_URL}/purchases/`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data?.items || data.data || data || [];
    }

    async createPurchase(data) {
        const response = await fetch(`${API_BASE_URL}/purchases/create`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    // ============================================
    // SUPPLIERS ENDPOINTS
    // ============================================
    
    async getSuppliers() {
        const response = await fetch(`${API_BASE_URL}/suppliers/`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data?.items || data.data || data || [];
    }

    async createSupplier(data) {
        const response = await fetch(`${API_BASE_URL}/suppliers/create`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    // ============================================
    // DASHBOARD ENDPOINTS
    // ============================================
    
    async getDashboardTotals() {
        const response = await fetch(`${API_BASE_URL}/dashboard/`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data || data || {};
    }

    async getDashboardToday() {
        const response = await fetch(`${API_BASE_URL}/dashboard/today`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data || data || {};
    }

    async getDashboardInventory() {
        const response = await fetch(`${API_BASE_URL}/dashboard/inventory`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data || data || {};
    }

    // ============================================
    // REPORTS ENDPOINTS
    // ============================================
    
    async getSalesReport() {
        const response = await fetch(`${API_BASE_URL}/reports/sales/`, {
            headers: this.getHeaders()
        });
        const data = await this.handleResponse(response);
        return data.data || data || {};
    }
}
// Create global API instance
const api = new PharmacyAPI();
