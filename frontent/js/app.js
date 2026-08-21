// ============================================
// MAIN APPLICATION LOGIC - FIXED
// ============================================

// Navigation function
async function navigateTo(page) {
    // Update sidebar
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeItem = document.querySelector(`.menu-item[data-page="${page}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
    
    // Update page title
    const titles = {
        dashboard: { title: 'Dashboard', subtitle: 'Overview of your pharmacy operations' },
        medicines: { title: 'Medicines', subtitle: 'Manage your medicine inventory' },
        inventory: { title: 'Inventory', subtitle: 'Real-time stock tracking' },
        sales: { title: 'Sales', subtitle: 'Manage sales transactions' },
        purchases: { title: 'Purchases', subtitle: 'Track purchase orders' },
        suppliers: { title: 'Suppliers', subtitle: 'Manage supplier relationships' },
        reports: { title: 'Reports', subtitle: 'Analytics and insights' }
    };
    
    const info = titles[page] || titles.dashboard;
    document.getElementById('pageTitle').textContent = info.title;
    document.getElementById('pageSubtitle').textContent = info.subtitle;
    
    // Load page content
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Loading ${info.title}...</p>
        </div>
    `;
    
    // Render appropriate page
    try {
        switch(page) {
            case 'dashboard':
                await renderDashboard();
                break;
            case 'medicines':
                await renderMedicines();
                break;
            case 'inventory':
                await renderInventory();
                break;
            case 'sales':
                await renderSales();
                break;
            case 'purchases':
                await renderPurchases();
                break;
            case 'suppliers':
                await renderSuppliers();
                break;
            case 'reports':
                await renderReports();
                break;
            default:
                await renderDashboard();
        }
    } catch (error) {
        console.error('Navigation error:', error);
        content.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i>
                Failed to load page: ${error.message}
            </div>
        `;
    }
}

// Placeholder functions for now - will be implemented
async function renderMedicines() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            Medicines module - Coming soon!
        </div>
    `;
}

async function renderInventory() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            Inventory module - Coming soon!
        </div>
    `;
}

async function renderSales() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            Sales module - Coming soon!
        </div>
    `;
}

async function renderPurchases() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            Purchases module - Coming soon!
        </div>
    `;
}

async function renderSuppliers() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            Suppliers module - Coming soon!
        </div>
    `;
}

async function renderReports() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            Reports module - Coming soon!
        </div>
    `;
}

function refreshData() {
    const currentPage = document.querySelector('.menu-item.active')?.dataset?.page || 'dashboard';
    navigateTo(currentPage);
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', async function() {
    console.log('App initializing...');
    // Check if user is authenticated
    const isAuthenticated = await checkAuth();
    
    if (!isAuthenticated) {
        document.getElementById('loadingSpinner').classList.add('hidden');
        document.getElementById('loginPage').style.display = 'flex';
        document.getElementById('mainApp').classList.add('d-none');
    }
});
