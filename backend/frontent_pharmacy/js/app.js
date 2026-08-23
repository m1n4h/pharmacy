// ============================================
// MAIN APPLICATION LOGIC
// ============================================

async function navigateTo(page) {
    console.log('Navigating to:', page);
    
    // Permission gate
    const allowed = window.userModules || [];
    if (!window.isAdmin && allowed.length > 0 && !allowed.includes(page)) {
        SwalAlert.warning('Huna ruhusa ya kufikia ukurasa huu.');
        return;
    }
    
    document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
    document.querySelector(`.menu-item[data-page="${page}"]`)?.classList.add('active');

    closeSidebar();
    
    const titles = {
        dashboard: { title: 'Dashboard', subtitle: 'Overview of your pharmacy operations' },
        medicines: { title: 'Medicines', subtitle: 'Manage your medicine inventory' },
        inventory: { title: 'Inventory', subtitle: 'Real-time stock tracking' },
        sales: { title: 'Sales', subtitle: 'Manage sales transactions' },
        purchases: { title: 'Purchases', subtitle: 'Track purchase orders' },
        suppliers: { title: 'Suppliers', subtitle: 'Manage supplier relationships' },
        reports: { title: 'Reports', subtitle: 'Analytics and insights' },
        profitloss: { title: 'Profit & Loss', subtitle: 'Revenue, costs and net profit' },
        expenses: { title: 'Expenses', subtitle: 'Track operating expenses' },
        expiry: { title: 'Expiry Monitor', subtitle: 'Monitor and manage expiring stock' },
        backup: { title: 'Backup & Restore', subtitle: 'Database backup management' },
        prescriptions: { title: 'Prescriptions', subtitle: 'Process and dispense prescriptions' },
        users: { title: 'Users & Roles', subtitle: 'Manage users and their roles' },
        permissions: { title: 'Permissions', subtitle: 'Manage module access per role' },
        activities: { title: 'Activities', subtitle: 'View all system activities' },
        settings: { title: 'Settings', subtitle: 'Configure system settings' },
        branches: { title: 'Branches', subtitle: 'Manage pharmacy branches' },
        categories: { title: 'Categories', subtitle: 'Manage medicine categories' },
        manufacturers: { title: 'Manufacturers', subtitle: 'Manage medicine manufacturers' },
        customers: { title: 'Customers', subtitle: 'Manage customer records' },
        stock_adjustments: { title: 'Stock Adjustments', subtitle: 'Track and reconcile inventory differences' },
        returns: { title: 'Returns', subtitle: 'Process sales returns and refunds' },
        stock_transfers: { title: 'Stock Transfers', subtitle: 'Transfer stock between branches' },
        disposals: { title: 'Disposal Register', subtitle: 'TMDA-compliant disposal tracking' }
    };
    
    const info = titles[page] || titles.dashboard;
    document.getElementById('pageTitle').textContent = info.title;
    document.getElementById('pageSubtitle').textContent = info.subtitle;
    
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary"></div>
            <p class="mt-3">Loading...</p>
        </div>
    `;
    
    try {
        switch(page) {
            case 'dashboard': await renderDashboard(); break;
            case 'medicines': await renderMedicines(); break;
            case 'inventory': await renderInventory(); break;
            case 'sales': await renderSales(); break;
            case 'purchases': await renderPurchases(); break;
            case 'suppliers': await renderSuppliers(); break;
            case 'reports': await renderReports(); break;
            case 'profitloss': await renderProfitLoss(); break;
            case 'expenses': await renderExpenses(); break;
            case 'expiry': await renderExpiry(); break;
            case 'backup': await renderBackup(); break;
            case 'prescriptions': await renderPrescriptions(); break;
            case 'users': await renderUsers(); break;
            case 'permissions': await renderPermissions(); break;
            case 'activities': await renderActivities(); break;
            case 'settings': await renderSettings(); break;
            case 'branches': await renderBranches(); break;
            case 'categories': await renderCategories(); break;
            case 'manufacturers': await renderManufacturers(); break;
            case 'customers': await renderCustomers(); break;
            case 'stock_adjustments': await renderStockAdjustments(); break;
            case 'returns': await renderReturns(); break;
            case 'stock_transfers': await renderStockTransfers(); break;
            case 'disposals': await renderDisposals(); break;
            default: await renderDashboard();
        }
        if (typeof applyTranslations === 'function') applyTranslations();
    } catch (e) {
        content.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
    }
}

function refreshData() {
    const active = document.querySelector('.menu-item.active');
    navigateTo(active?.dataset?.page || 'dashboard');
}

// ============================================
// RESPONSIVE SIDEBAR (mobile drawer)
// ============================================
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    if (!sidebar) return;
    const isOpen = sidebar.classList.contains('open');
    if (isOpen) {
        closeSidebar();
    } else {
        sidebar.classList.add('open');
        backdrop.classList.add('show');
    }
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    if (sidebar) sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('show');
}

window.addEventListener('resize', function() {
    if (window.innerWidth > 991) closeSidebar();
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeSidebar();
});

// Hide menu items the user is not allowed to access
function applyMenuPermissions(modules, isAdmin) {
    const allowed = isAdmin ? null : new Set(modules);
    document.querySelectorAll('.menu-item[data-page]').forEach(el => {
        const page = el.dataset.page;
        if (isAdmin || allowed.has(page)) {
            el.style.display = '';
        } else {
            el.style.display = 'none';
        }
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 App starting...');
    if (window.ThemeManager) ThemeManager.init();
    const savedLang = localStorage.getItem('pharmacy_lang') || 'en';
    window.I18N.lang = savedLang;
    const authenticated = await checkAuth();
    if (!authenticated) {
        document.getElementById('loadingSpinner').classList.add('hidden');
        document.getElementById('loginPage').style.display = 'flex';
        document.getElementById('mainApp').classList.add('d-none');
    } else {
        window.applyTranslations();
    }
});

console.log('App module loaded');