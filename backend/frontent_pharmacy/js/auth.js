// ============================================
// AUTHENTICATION MODULE
// ============================================

// Fetch the current user's permissions and gate the menu
async function loadMyPermissions() {
    try {
        const result = await api.getMyPermissions();
        const data = result?.data || {};
        window.isAdmin = !!data.is_admin;
        window.userModules = data.modules || [];
        applyMenuPermissions(window.userModules, window.isAdmin);
    } catch (error) {
        window.isAdmin = false;
        window.userModules = [];
    }
}

// Load settings (default currency) and exchange rates into APP_CONFIG
async function loadAppConfig() {
    try {
        const [settings, currencies] = await Promise.all([
            api.getSettings().catch(() => null),
            api.getCurrencies().catch(() => null)
        ]);
        if (settings?.data?.default_currency) {
            window.APP_CONFIG.defaultCurrency = settings.data.default_currency;
        }
        const symbols = { TZS: 'TSh', USD: '$', ZMW: 'K', EUR: '€', GBP: '£', KES: 'KSh' };
        if (settings?.data?.default_currency) {
            window.APP_CONFIG.currencySymbol = symbols[settings.data.default_currency] || 'TSh';
        }
        const rates = {};
        (currencies?.data?.items || []).forEach(c => {
            rates[c.code] = c.rate_to_tzs;
            if (c.code === (window.APP_CONFIG.defaultCurrency || 'TZS')) {
                window.APP_CONFIG.currencySymbol = c.symbol || symbols[c.code] || 'TSh';
            }
        });
        window.APP_CONFIG.currencyRates = rates;
    } catch (e) {
        console.warn('Could not load app config', e);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    console.log('Login form submitted');
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const alertDiv = document.getElementById('loginAlert');
    
    alertDiv.classList.add('d-none');
    alertDiv.className = 'alert alert-danger d-none';
    
    try {
        const btn = document.querySelector('.login-btn');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Signing in...';
        btn.disabled = true;
        
        console.log('Calling login API...');
        const result = await api.login(email, password);
        console.log('Login result:', result);
        
        if (result.success && result.data) {
            const userData = result.data.user;
            
            // Store user info
            localStorage.setItem('userRole', userData.role || 'staff');
            localStorage.setItem('userEmail', userData.email);
            localStorage.setItem('userName', userData.full_name || 'User');
            
            // Update UI
            document.getElementById('userName').textContent = userData.full_name || 'Admin';
            document.getElementById('userRole').textContent = userData.role || 'Admin';
            
            btn.innerHTML = '<i class="fas fa-check me-2"></i>Welcome!';
            btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            
            setTimeout(() => {
                document.getElementById('loginPage').style.display = 'none';
                document.getElementById('mainApp').classList.remove('d-none');
                document.getElementById('loadingSpinner').classList.add('hidden');
                loadAppConfig();
                loadMyPermissions();
                loadNotifications();
                navigateTo('dashboard');
            }, 500);
        } else {
            throw new Error(result.message || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        alertDiv.classList.remove('d-none');
        alertDiv.textContent = '❌ ' + (error.message || 'Login failed. Please check your credentials.');
        
        const btn = document.querySelector('.login-btn');
        btn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Sign In';
        btn.disabled = false;
        btn.style.background = '';
    }
}

async function handleLogout() {
    const result = await SwalAlert.confirm('Are you sure you want to logout?');
    if (!result.isConfirmed) return;
    try {
        await api.logout();
    } catch (error) {
        console.error('Logout error:', error);
    }
    localStorage.clear();
    window.location.reload();
}

async function checkAuth() {
    const token = localStorage.getItem('accessToken');
    console.log('Checking auth, token exists:', !!token);
    
    if (token) {
        try {
            api.setToken(token);
            const result = await api.getMe();
            console.log('Auth check result:', result);
            
            if (result.success && result.data) {
                const userData = result.data;
                document.getElementById('userName').textContent = userData.full_name || 'Admin';
                document.getElementById('userRole').textContent = userData.role || 'Staff';
                localStorage.setItem('userRole', userData.role || 'staff');
                localStorage.setItem('userEmail', userData.email);
                localStorage.setItem('userName', userData.full_name || 'User');
                
                document.getElementById('loginPage').style.display = 'none';
                document.getElementById('mainApp').classList.remove('d-none');
                document.getElementById('loadingSpinner').classList.add('hidden');
                await loadAppConfig();
                await loadMyPermissions();
                loadNotifications();
                navigateTo('dashboard');
                return true;
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            api.clearToken();
        }
    }
    return false;
}

console.log('Auth module loaded');
