// ============================================
// DISPOSAL MODULE — TMDA Compliance
// ============================================

async function renderDisposals() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
        <div class="page-header">
            <div>
                <h4><i class="fas fa-biohazard me-2"></i>Disposal Register</h4>
                <p class="mb-0">TMDA-compliant medicine disposal tracking</p>
            </div>
            <button class="btn btn-danger" onclick="openDisposalModal()">
                <i class="fas fa-plus me-1"></i>Record Disposal
            </button>
        </div>
        <div class="table-container">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Disposal #</th>
                        <th>Medicine</th>
                        <th>Batch</th>
                        <th>Qty</th>
                        <th>Method</th>
                        <th>Value</th>
                        <th>Witness</th>
                        <th>Status</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody id="disposalTableBody">
                    <tr><td colspan="9" class="text-center py-4"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>
                </tbody>
            </table>
        </div>
        <div class="modal fade" id="disposalModal" tabindex="-1"><div class="modal-dialog modal-lg"><div class="modal-content">
            <div class="modal-header"><h5 class="modal-title">Record Disposal</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
            <div class="modal-body">
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label required">Medicine</label>
                        <input type="text" class="form-control" id="dispMedicineSearch" placeholder="Search medicine..." oninput="searchMedicineForDisposal(this.value)">
                        <div id="dispMedicineResults" class="list-group" style="position:absolute;z-index:9999;display:none;max-height:200px;overflow-y:auto;"></div>
                        <input type="hidden" id="dispMedicineId">
                        <input type="hidden" id="dispBatchId">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Batch Info</label>
                        <input type="text" class="form-control" id="dispBatchInfo" readonly placeholder="Select medicine first">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label required">Quantity</label>
                        <input type="number" class="form-control" id="dispQuantity" min="1" value="1">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label required">Disposal Method</label>
                        <select class="form-select" id="dispMethod">
                            <option value="incineration">Incineration</option>
                            <option value="landfill">Landfill</option>
                            <option value="return_to_supplier">Return to Supplier</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Estimated Value (TSh)</label>
                        <input type="number" class="form-control" id="dispValue" value="0">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Reason</label>
                        <textarea class="form-control" id="dispReason" rows="2" placeholder="Reason for disposal..."></textarea>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Notes</label>
                        <textarea class="form-control" id="dispNotes" rows="2" placeholder="Additional notes..."></textarea>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Witness Name</label>
                        <input type="text" class="form-control" id="dispWitness" placeholder="Witness name">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Witness Title</label>
                        <input type="text" class="form-control" id="dispWitnessTitle" placeholder="e.g. Pharmacist">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Certificate Number</label>
                        <input type="text" class="form-control" id="dispCertNo" placeholder="TMDA cert no.">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">TMDA Reference</label>
                        <input type="text" class="form-control" id="dispTmdaRef" placeholder="TMDA reference">
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button class="btn btn-danger" onclick="submitDisposal()"><i class="fas fa-biohazard me-1"></i>Record Disposal</button>
            </div>
        </div></div></div>
    `;
    await loadDisposals();
}

async function loadDisposals() {
    try {
        const res = await api.getExpiryActions();
        const items = res?.data?.items || [];
        const tbody = document.getElementById('disposalTableBody');
        if (!items.length) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-3">No disposal records</td></tr>';
            return;
        }
        tbody.innerHTML = items.map(d => `
            <tr>
                <td><strong>${d.action_type?.toUpperCase() || '-'}</strong></td>
                <td>${d.medicine_name || '-'}</td>
                <td>${d.batch_no || '-'}</td>
                <td>${d.quantity}</td>
                <td><span class="badge bg-secondary">${d.action_type || '-'}</span></td>
                <td>-</td>
                <td>${d.responsible_person || '-'}</td>
                <td><span class="badge bg-success">Recorded</span></td>
                <td>${d.created_at ? new Date(d.created_at).toLocaleDateString() : '-'}</td>
            </tr>
        `).join('');
    } catch (e) {
        console.error('Load disposals error:', e);
    }
}

let dispSearchTimeout = null;
async function searchMedicineForDisposal(query) {
    clearTimeout(dispSearchTimeout);
    const resultsDiv = document.getElementById('dispMedicineResults');
    if (!query || query.length < 2) { resultsDiv.style.display = 'none'; return; }
    dispSearchTimeout = setTimeout(async () => {
        try {
            const medicines = await api.searchMedicines(query, 5);
            if (!medicines.length) { resultsDiv.style.display = 'none'; return; }
            resultsDiv.innerHTML = medicines.map(m => `
                <button type="button" class="list-group-item list-group-item-action" onclick="selectMedicineForDisposal(${m.id}, '${(m.name || '').replace(/'/g, "\\'")}')">
                    ${m.name} ${m.strength ? '- ' + m.strength : ''}
                </button>
            `).join('');
            resultsDiv.style.display = 'block';
        } catch (e) { resultsDiv.style.display = 'none'; }
    }, 300);
}

async function selectMedicineForDisposal(medId, name) {
    document.getElementById('dispMedicineId').value = medId;
    document.getElementById('dispMedicineSearch').value = name;
    document.getElementById('dispMedicineResults').style.display = 'none';
    try {
        const batches = await api.getBatches(medId);
        if (batches.length) {
            const b = batches[0];
            document.getElementById('dispBatchId').value = b.id;
            document.getElementById('dispBatchInfo').value = `Batch: ${b.batch_no} | Qty: ${b.quantity} | Exp: ${b.expiry_date}`;
            document.getElementById('dispValue').value = b.purchase_price * b.quantity;
        }
    } catch (e) {}
}

async function submitDisposal() {
    const medicineId = document.getElementById('dispMedicineId').value;
    const batchId = document.getElementById('dispBatchId').value;
    if (!medicineId || !batchId) { SwalAlert.warning('Please select a medicine and batch'); return; }
    try {
        await api.createExpiryAction({
            action_type: document.getElementById('dispMethod').value,
            medicine_id: parseInt(medicineId),
            medicine_name: document.getElementById('dispMedicineSearch').value,
            batch_id: parseInt(batchId),
            batch_no: document.getElementById('dispBatchInfo').value.split('Batch: ')[1]?.split(' |')[0] || '',
            quantity: parseInt(document.getElementById('dispQuantity').value),
            reason: document.getElementById('dispReason').value,
            responsible_person: document.getElementById('dispWitness').value,
            notes: document.getElementById('dispNotes').value,
        });
        SwalAlert.success('Disposal recorded successfully');
        bootstrap.Modal.getInstance(document.getElementById('disposalModal')).hide();
        await loadDisposals();
    } catch (e) {
        SwalAlert.error('Failed to record disposal: ' + e.message);
    }
}

console.log('Disposal module loaded');
