// ============================================
// AUTHENTICATION MODULE - FIXED
// ============================================

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const alertDiv = document.getElementById('loginAlert');
    const errorMessage = document.getElementById('loginErrorMessage');
    
    // Hide previous alerts
    alertDiv.classList.add('d-none');
    
    try {
        // Show loading state
        const btn = document.querySelector('.login-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Signing in...';
        btn.disabled = true;
        
        // Attempt login
        const result = await api.login(email, password);
        
        console.log('Login result:', result); // Debug log
        
        // Check if login was successful
        if (result.success && result.data && result.data.access_token) {
            // Login successful - get user data from response
            const userData = result.data.user;
            const accessToken = result.data.access_token;
            
            // Store token and user info
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('userRole', userData.role || 'staff');
            localStorage.setItem('userEmail', userData.email);
            localStorage.setItem('userName', userData.full_name || 'User');
            
            // Update UI
            document.getElementById('userName').textContent = userData.full_name || 'Admin';
            
            // Show success
            btn.innerHTML = '<i class="fas fa-check me-2"></i>Welcome!';
            btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            
            setTimeout(() => {
                // Show main app
                document.getElementById('loginPage').style.display = 'none';
                document.getElementById('mainApp').classList.remove('d-none');
                document.getElementById('loadingSpinner').classList.add('hidden');
                
                // Load dashboard
                navigateTo('dashboard');
            }, 500);
        } else {
            throw new Error(result.message || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        
        // Show error
        alertDiv.classList.remove('d-none');
        errorMessage.textContent = error.message || 'Login failed. Please check your credentials.';
        
        // Reset button
        const btn = document.querySelector('.login-btn');
        btn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Sign In';
        btn.disabled = false;
        btn.style.background = '';
        
        // Shake animation
        const form = document.getElementById('loginForm');
        form.style.animation = 'shake 0.5s ease';
        setTimeout(() => {
            form.style.animation = '';
        }, 500);
    }
}

// Handle logout
async function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        try {
            await api.logout();
        } catch (error) {
            console.error('Logout error:', error);
        }
        // Clear local storage
        localStorage.removeItem('accessToken');
        localStorage.removeItem('userRole');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userName');
        // Reload to login page
        window.location.reload();
    }
}

// Check if user is already logged in
async function checkAuth() {
    const token = localStorage.getItem('accessToken');
    if (token) {
        try {
            api.setToken(token);
            const result = await api.getMe();
            console.log('Auth check result:', result);
            
            if (result.success && result.data) {
                const userData = result.data;
                document.getElementById('userName').textContent = userData.full_name || 'Admin';
                localStorage.setItem('userRole', userData.role || 'staff');
                localStorage.setItem('userEmail', userData.email);
                localStorage.setItem('userName', userData.full_name || 'User');
                
                // Show main app
                document.getElementById('loginPage').style.display = 'none';
                document.getElementById('mainApp').classList.remove('d-none');
                document.getElementById('loadingSpinner').classList.add('hidden');
                
                // Load dashboard
                navigateTo('dashboard');
                return true;
            } else {
                // Invalid response
                api.clearToken();
                return false;
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            api.clearToken();
            return false;
        }
    }
    return false;
}

// Add shake animation if not already present
if (!document.getElementById('shakeStyle')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'shakeStyle';
    styleSheet.textContent = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-8px); }
            20%, 40%, 60%, 80% { transform: translateX(8px); }
        }
    `;
    document.head.appendChild(styleSheet);
}
