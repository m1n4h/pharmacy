// ============================================
// SUPPLIERS MODULE
// ============================================

async function renderSuppliers() {
    const content = document.getElementById('pageContent');
    try {
        const suppliers = await api.getSuppliers();
        
        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openAddSupplierModal()">
                    <i class="fas fa-plus"></i> ${t('Add Supplier')}
                </button>
                <span class="text-muted">Total: ${suppliers.length} ${t('Suppliers')}</span>
            </div>
            <div class="row">
                ${suppliers.map(supplier => `
                    <div class="col-md-4 mb-3">
                        <div class="card h-100">
                            <div class="card-body">
                                <h5 class="card-title">
                                    <i class="fas fa-building me-2"></i>${supplier.name}
                                </h5>
                                ${supplier.company_name ? `<p class="text-muted"><small>${supplier.company_name}</small></p>` : ''}
                                <p class="card-text">
                                    ${supplier.phone ? `<i class="fas fa-phone me-1"></i>${supplier.phone}<br>` : ''}
                                    ${supplier.email ? `<i class="fas fa-envelope me-1"></i>${supplier.email}<br>` : ''}
                                    ${supplier.address ? `<i class="fas fa-map-marker me-1"></i>${supplier.address}` : ''}
                                </p>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">${t('Failed to load')}: ${error.message}</div>`;
    }
}

function openAddSupplierModal() {
    document.getElementById('addSupplierForm').reset();
    const modal = new bootstrap.Modal(document.getElementById('addSupplierModal'));
    modal.show();
}

async function saveSupplier() {
    const data = {
        name: document.getElementById('sup_name').value,
        company_name: document.getElementById('sup_company').value,
        phone: document.getElementById('sup_phone').value,
        email: document.getElementById('sup_email').value,
        address: document.getElementById('sup_address').value
    };
    
    if (!data.name) {
        SwalAlert.warning(t('Supplier name is required'));
        return;
    }
    
    try {
        await api.createSupplier(data);
        bootstrap.Modal.getInstance(document.getElementById('addSupplierModal')).hide();
        SwalAlert.success(t('Supplier added successfully'));
        navigateTo('suppliers');
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Suppliers module loaded');
