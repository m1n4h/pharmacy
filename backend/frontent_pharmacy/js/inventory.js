// ============================================
// INVENTORY MODULE
// ============================================

async function renderInventory() {
    const content = document.getElementById('pageContent');
    try {
        const [inventory, lowStock, nearExpiry, expired] = await Promise.all([
            api.getInventory(),
            api.getLowStock(),
            api.getNearExpiry(),
            api.getExpired()
        ]);
        
        content.innerHTML = `
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="stat-card border-mint">
                        <div class="stat-value">${inventory.length || 0}</div>
                        <div class="stat-label">Total Items</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card border-orange">
                        <div class="stat-value">${lowStock.length || 0}</div>
                        <div class="stat-label">Low Stock</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card border-warning">
                        <div class="stat-value">${nearExpiry.length || 0}</div>
                        <div class="stat-label">Near Expiry (30 days)</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card border-red">
                        <div class="stat-value">${expired.length || 0}</div>
                        <div class="stat-label">Expired</div>
                    </div>
                </div>
            </div>
            
            <ul class="nav nav-tabs mb-3" id="inventoryTabs">
                <li class="nav-item"><a class="nav-link active" data-bs-toggle="tab" href="#allInventory">All</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#lowStockTab">Low Stock</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#nearExpiryTab">Near Expiry</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#expiredTab">Expired</a></li>
            </ul>
            
            <div class="tab-content">
                <div class="tab-pane fade show active" id="allInventory">
                    ${renderInventoryTable(inventory)}
                </div>
                <div class="tab-pane fade" id="lowStockTab">
                    ${renderInventoryTable(lowStock, 'danger')}
                </div>
                <div class="tab-pane fade" id="nearExpiryTab">
                    ${renderInventoryTable(nearExpiry, 'warning')}
                </div>
                <div class="tab-pane fade" id="expiredTab">
                    ${renderInventoryTable(expired, 'danger')}
                </div>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load inventory: ${error.message}</div>`;
    }
}

function renderInventoryTable(items, statusType = '') {
    if (!items || items.length === 0) {
        return '<div class="alert alert-info">No items found</div>';
    }
    
    return `
        <div class="table-container">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Medicine</th>
                        <th>Batch</th>
                        <th>Quantity</th>
                        <th>Expiry Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(item => `
                        <tr>
                            <td>${item.medicine_name || item.name || 'Unknown'}</td>
                            <td>${item.batch_no || item.batch_id || 'N/A'}</td>
                            <td><span class="badge ${item.quantity < 10 ? 'badge-danger' : 'badge-success'}">${item.quantity || 0}</span></td>
                            <td>${item.expiry_date || 'N/A'}</td>
                            <td>${getStatusBadge(item, statusType)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function getStatusBadge(item, statusType) {
    if (statusType === 'danger') return '<span class="badge badge-danger">Critical</span>';
    if (statusType === 'warning') return '<span class="badge badge-warning">Warning</span>';
    if (item.quantity < 10) return '<span class="badge badge-danger">Low Stock</span>';
    if (item.quantity < 50) return '<span class="badge badge-warning">Medium</span>';
    return '<span class="badge badge-success">OK</span>';
}

console.log('Inventory module loaded');
