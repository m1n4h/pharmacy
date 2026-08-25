// ============================================
// UPLOAD SALES — Document Upload & Processing
// ============================================

let uploadSalesData = [];
let uploadId = null;

function openUploadSalesModal() {
    uploadSalesData = [];
    uploadId = null;
    const modal = document.getElementById('uploadSalesModal');
    if (!modal) createUploadSalesModal();
    resetUploadForm();
    new bootstrap.Modal(document.getElementById('uploadSalesModal')).show();
}

function createUploadSalesModal() {
    const div = document.createElement('div');
    div.innerHTML = `
    <div class="modal fade" id="uploadSalesModal" tabindex="-1" aria-labelledby="uploadSalesModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-xl">
            <div class="modal-content upload-modal-content">
                <div class="modal-header upload-modal-header">
                    <h5 class="modal-title" id="uploadSalesModalLabel">
                        <i class="fas fa-cloud-upload-alt me-2"></i><span data-i18n="Upload Sales Document">Upload Sales Document</span>
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <!-- Step 1: File Selection -->
                    <div id="uploadStep1">
                        <div class="text-center mb-4">
                            <div id="uploadDropZone" class="upload-drop-zone border border-3 border-dashed rounded-4 p-5 text-center">
                                <i class="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                                <h5 data-i18n="Drag & drop your file here">Drag & drop your file here</h5>
                                <p class="text-muted mb-3" data-i18n="or click to browse">or click to browse</p>
                                <p class="text-muted mb-3"><small data-i18n="Supported formats: CSV, Excel, PDF, DOCX, PNG, JPG">Supported formats: CSV, Excel, PDF, DOCX, PNG, JPG</small></p>
                                <input type="file" id="uploadFileInput" accept=".csv,.xlsx,.xls,.pdf,.docx,.png,.jpg,.jpeg" style="display:none;" onchange="handleUploadFileSelect(event)">
                                <button class="btn btn-outline-primary btn-sm" onclick="document.getElementById('uploadFileInput').click()">
                                    <i class="fas fa-folder-open me-1"></i> <span data-i18n="Choose File">Choose File</span>
                                </button>
                            </div>
                            <div id="uploadFileInfo" class="mt-3 d-none">
                                <div class="d-flex align-items-center justify-content-center gap-3">
                                    <i class="fas fa-file-alt fa-2x text-primary"></i>
                                    <div class="text-start">
                                        <div id="uploadFileName" class="fw-bold"></div>
                                        <small id="uploadFileSize" class="text-muted"></small>
                                    </div>
                                    <button class="btn btn-sm btn-outline-danger" onclick="clearUploadFile()">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="text-center">
                            <button class="btn btn-primary px-4" id="uploadParseBtn" onclick="parseUploadDocument()" disabled>
                                <i class="fas fa-cog me-1"></i> <span data-i18n="Parse Document">Parse Document</span>
                            </button>
                        </div>
                    </div>

                    <!-- Step 2: Preview & Validate -->
                    <div id="uploadStep2" class="d-none">
                        <div class="row mb-3">
                            <div class="col-md-4">
                                <div class="upload-stat-card text-center p-3 rounded-3">
                                    <div class="upload-stat-value text-primary" id="uploadStatTotal">0</div>
                                    <div class="upload-stat-label text-muted" data-i18n="Total Records">Total Records</div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="upload-stat-card text-center p-3 rounded-3">
                                    <div class="upload-stat-value text-success" id="uploadStatValid">0</div>
                                    <div class="upload-stat-label text-muted" data-i18n="Valid Records">Valid Records</div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="upload-stat-card text-center p-3 rounded-3">
                                    <div class="upload-stat-value text-danger" id="uploadStatIssues">0</div>
                                    <div class="upload-stat-label text-muted" data-i18n="Issues Found">Issues Found</div>
                                </div>
                            </div>
                        </div>

                        <div class="alert alert-info mb-3">
                            <i class="fas fa-info-circle me-1"></i>
                            <span id="uploadSummary"></span>
                        </div>

                        <div id="uploadPreviewAccordion"></div>
                        <div id="uploadItemErrors" class="d-none mt-3"></div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" data-i18n="Cancel">Cancel</button>
                    <button type="button" class="btn btn-outline-secondary d-none" id="uploadBackBtn" onclick="backToUploadStep1()">
                        <i class="fas fa-arrow-left me-1"></i> <span data-i18n="Back">Back</span>
                    </button>
                    <button type="button" class="btn btn-success d-none" id="uploadConfirmBtn" onclick="confirmUploadSales()">
                        <i class="fas fa-check me-1"></i> <span data-i18n="Confirm & Create Sales">Confirm & Create Sales</span>
                    </button>
                </div>
            </div>
        </div>
    </div>`;
    document.body.appendChild(div);

    const dropZone = document.getElementById('uploadDropZone');
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            document.getElementById('uploadFileInput').files = e.dataTransfer.files;
            handleUploadFileSelect({ target: { files: e.dataTransfer.files } });
        }
    });
    dropZone.addEventListener('click', () => document.getElementById('uploadFileInput').click());
}

function handleUploadFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    const allowed = ['.csv', '.xlsx', '.xls', '.pdf', '.docx', '.png', '.jpg', '.jpeg'];
    if (!allowed.includes(ext)) {
        SwalAlert.error(t('Invalid file type'));
        return;
    }
    if (file.size > 10 * 1024 * 1024) {
        SwalAlert.error(t('File too large'));
        return;
    }
    document.getElementById('uploadFileName').textContent = file.name;
    document.getElementById('uploadFileSize').textContent = formatFileSize(file.size);
    document.getElementById('uploadFileInfo').classList.remove('d-none');
    document.getElementById('uploadDropZone').classList.add('d-none');
    document.getElementById('uploadParseBtn').disabled = false;
}

function clearUploadFile() {
    document.getElementById('uploadFileInput').value = '';
    document.getElementById('uploadFileInfo').classList.add('d-none');
    document.getElementById('uploadDropZone').classList.remove('d-none');
    document.getElementById('uploadParseBtn').disabled = true;
}

function resetUploadForm() {
    document.getElementById('uploadStep1')?.classList.remove('d-none');
    document.getElementById('uploadStep2')?.classList.add('d-none');
    document.getElementById('uploadBackBtn')?.classList.add('d-none');
    document.getElementById('uploadConfirmBtn')?.classList.add('d-none');
    clearUploadFile();
}

function backToUploadStep1() {
    document.getElementById('uploadStep1').classList.remove('d-none');
    document.getElementById('uploadStep2').classList.add('d-none');
    document.getElementById('uploadBackBtn').classList.add('d-none');
    document.getElementById('uploadConfirmBtn').classList.add('d-none');
}

async function parseUploadDocument() {
    const fileInput = document.getElementById('uploadFileInput');
    if (!fileInput.files.length) return;
    const file = fileInput.files[0];

    Swal.showLoading({ title: t('Parsing document...'), allowOutsideClick: false });

    try {
        const data = await api.uploadSalesDocument(file);
        Swal.close();

        if (!data.success) {
            SwalAlert.error(data.message || t('Failed to parse document'));
            return;
        }

        uploadId = data.data.upload_id;
        uploadSalesData = data.data.records || [];

        if (uploadSalesData.length === 0) {
            SwalAlert.warning(t('No sale records found'));
            return;
        }

        showUploadPreview(data.data);
    } catch (err) {
        Swal.close();
        SwalAlert.error(t('Error parsing document') + ': ' + (err.message || ''));
    }
}

function showUploadPreview(result) {
    document.getElementById('uploadStep1').classList.add('d-none');
    document.getElementById('uploadStep2').classList.remove('d-none');
    document.getElementById('uploadBackBtn').classList.remove('d-none');
    document.getElementById('uploadConfirmBtn').classList.remove('d-none');

    let totalItems = 0;
    let validRecords = 0;
    let issueRecords = 0;
    let allIssueItems = [];

    result.records.forEach((rec, rIdx) => {
        let recHasIssue = false;
        (rec.items || []).forEach((item, iIdx) => {
            totalItems++;
            if (item.stock_status === 'ok') {
                // valid
            } else {
                recHasIssue = true;
                allIssueItems.push({ recordIdx: rIdx, itemIdx: iIdx, item: item });
            }
        });
        if (recHasIssue) issueRecords++;
        else validRecords++;
    });

    document.getElementById('uploadStatTotal').textContent = result.records.length;
    document.getElementById('uploadStatValid').textContent = validRecords;
    document.getElementById('uploadStatIssues').textContent = issueRecords;

    document.getElementById('uploadSummary').innerHTML =
        t('Found records in file').replace('{count}', `<strong>${result.records.length}</strong>`).replace('{file}', `<strong>${result.filename}</strong>`);

    let accordionHtml = '';
    result.records.forEach((rec, idx) => {
        const total = rec.items ? rec.items.reduce((s, i) => s + (i.quantity * (i.selling_price || i.price || 0)), 0) : 0;
        const hasIssue = (rec.items || []).some(i => i.stock_status !== 'ok');
        const badgeClass = hasIssue ? 'bg-warning text-dark' : 'bg-success';
        const badgeText = hasIssue ? t('Has Issues') : t('Valid');

        let itemsTable = `<table class="table table-sm table-bordered mb-0 upload-item-table">
            <thead class="upload-item-thead">
                <tr><th>${t('Medicine')}</th><th>${t('Quantity')}</th><th>${t('Unit Price')}</th><th>${t('Total')}</th><th>${t('Status')}</th></tr>
            </thead><tbody>`;

        (rec.items || []).forEach((item) => {
            let statusBadge = '';
            let noteText = '';
            if (item.stock_status === 'ok') {
                statusBadge = '<span class="badge bg-success"><i class="fas fa-check me-1"></i>' + t('OK') + '</span>';
            } else if (item.stock_status === 'insufficient') {
                statusBadge = '<span class="badge bg-warning text-dark"><i class="fas fa-exclamation-triangle me-1"></i>' + t('Low Stock') + '</span>';
                noteText = `<br><small class="text-muted">${item.stock_note || ''}</small>`;
            } else if (item.stock_status === 'out_of_stock') {
                statusBadge = '<span class="badge bg-danger"><i class="fas fa-times-circle me-1"></i>' + t('Out of Stock') + '</span>';
                noteText = `<br><small class="text-muted">${item.stock_note || ''}</small>`;
            } else {
                statusBadge = '<span class="badge bg-danger"><i class="fas fa-question-circle me-1"></i>' + t('Not Found') + '</span>';
                noteText = `<br><small class="text-muted">${item.stock_note || ''}</small>`;
            }

            const itemTotal = item.quantity * (item.selling_price || item.price || 0);
            const matchedName = item.matched_name || item.medicine_name;
            itemsTable += `<tr>
                <td>${escapeHtml(matchedName)}${noteText}</td>
                <td>${item.quantity}</td>
                <td>${formatMoney(item.selling_price || item.price || 0)}</td>
                <td>${formatMoney(itemTotal)}</td>
                <td>${statusBadge}</td>
            </tr>`;
        });

        itemsTable += '</tbody></table>';

        accordionHtml += `
        <div class="accordion mb-2" id="uploadAcc${idx}">
            <div class="accordion-item upload-accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed upload-accordion-btn" type="button"
                        data-bs-toggle="collapse" data-bs-target="#uploadAccBody${idx}">
                        <span class="badge ${badgeClass} me-2">${badgeText}</span>
                        <strong class="me-2">#${idx + 1}</strong>
                        <span class="me-2">${escapeHtml(rec.customer_name || t('Walk-in Customer'))}</span>
                        <span class="text-muted me-2">${rec.sale_date || t('Today')}</span>
                        <span class="text-muted me-2">(${(rec.items || []).length} ${t('items')})</span>
                        <span class="fw-bold ms-auto">${formatMoney(total)}</span>
                    </button>
                </h2>
                <div id="uploadAccBody${idx}" class="accordion-collapse collapse" data-bs-parent="#uploadAcc${idx}">
                    <div class="accordion-body p-0">${itemsTable}</div>
                </div>
            </div>
        </div>`;
    });

    document.getElementById('uploadPreviewAccordion').innerHTML = accordionHtml;

    if (allIssueItems.length > 0) {
        let errHtml = `<div class="alert alert-warning"><h6><i class="fas fa-exclamation-triangle me-1"></i> ${t('Items with issues')}</h6><ul class="mb-0">`;
        allIssueItems.forEach(({ item }) => {
            errHtml += `<li><strong>${escapeHtml(item.matched_name || item.medicine_name)}</strong>: ${item.stock_note || t('Not available')}</li>`;
        });
        errHtml += '</ul></div>';
        document.getElementById('uploadItemErrors').innerHTML = errHtml;
        document.getElementById('uploadItemErrors').classList.remove('d-none');
    } else {
        document.getElementById('uploadItemErrors').classList.add('d-none');
    }
}

async function confirmUploadSales() {
    if (!uploadId) return;

    const confirmed = await SwalAlert.confirm(
        t('This will create sale records and deduct stock').replace('{count}', uploadSalesData.length)
    );

    if (!confirmed.isConfirmed) return;

    Swal.showLoading({ title: t('Creating sales...'), allowOutsideClick: false });

    try {
        const data = await api.processUpload(uploadId);
        Swal.close();

        if (!data.success) {
            SwalAlert.error(data.message || t('Failed to process upload'));
            return;
        }

        let msg = t('sale(s) created successfully').replace('{count}', data.data.sales_created);
        if (data.data.errors && data.data.errors.length > 0) {
            msg += '\n\n' + t('error(s) occurred').replace('{count}', data.data.errors.length);
        }
        SwalAlert.success(msg);

        bootstrap.Modal.getInstance(document.getElementById('uploadSalesModal'))?.hide();
        renderSales();
    } catch (err) {
        Swal.close();
        SwalAlert.error(t('Error processing upload') + ': ' + (err.message || ''));
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text || '';
    return d.innerHTML;
}

// ============================================
// UPLOAD HISTORY
// ============================================
async function showUploadHistory() {
    try {
        const result = await api.getUploadLogs(1, 50);
        const logs = result?.items || [];

        let html = '';
        if (logs.length === 0) {
            html = `<div class="text-center text-muted py-4"><i class="fas fa-inbox fa-2x mb-2"></i><p>${t('No data found')}</p></div>`;
        } else {
            html = `<div class="table-responsive"><table class="table table-sm table-hover">
                <thead class="table-light">
                    <tr>
                        <th>${t('File Name')}</th>
                        <th>${t('File Type')}</th>
                        <th>${t('File Size')}</th>
                        <th>${t('Rows Extracted')}</th>
                        <th>${t('Sales Created')}</th>
                        <th>${t('Status')}</th>
                        <th>${t('Date')}</th>
                    </tr>
                </thead>
                <tbody>`;
            logs.forEach(log => {
                const statusBadge = log.status === 'processed'
                    ? '<span class="badge bg-success">Processed</span>'
                    : log.status === 'failed'
                        ? '<span class="badge bg-danger">Failed</span>'
                        : '<span class="badge bg-warning text-dark">Processing</span>';
                html += `<tr>
                    <td><i class="fas fa-file me-1"></i>${escapeHtml(log.filename)}</td>
                    <td>${escapeHtml(log.file_type)}</td>
                    <td>${formatFileSize(log.file_size)}</td>
                    <td>${log.rows_extracted || 0}</td>
                    <td>${log.sales_created || 0}</td>
                    <td>${statusBadge}</td>
                    <td>${log.created_at ? new Date(log.created_at).toLocaleString() : '-'}</td>
                </tr>`;
            });
            html += '</tbody></table></div>';
        }

        Swal.fire({
            title: `<i class="fas fa-history me-2"></i>${t('Upload History')}`,
            html: html,
            width: '900px',
            confirmButtonText: t('Close'),
            confirmButtonColor: '#6b7280'
        });
    } catch (err) {
        SwalAlert.error(t('Failed to load') + ': ' + (err.message || ''));
    }
}
