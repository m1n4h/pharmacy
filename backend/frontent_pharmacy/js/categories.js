// ============================================
// CATEGORIES MODULE
// ============================================

let editingCategoryId = null;

async function renderCategories() {
    const content = document.getElementById('pageContent');
    try {
        const categories = await api.getCategories();

        content.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openCategoryModal()">
                    <i class="fas fa-plus"></i> <span data-i18n="addCategory">Add Category</span>
                </button>
                <span class="text-muted">Total: ${categories.length} <span data-i18n="categories">categories</span></span>
            </div>
            <div class="table-container">
                <table class="table table-hover" id="categoriesTable">
                    <thead>
                        <tr>
                            <th data-i18n="name">Name</th>
                            <th data-i18n="description">Description</th>
                            <th data-i18n="actions">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="categoriesTableBody">
                        ${categories.map(c => `
                            <tr>
                                <td><strong>${c.name}</strong></td>
                                <td>${c.description || '-'}</td>
                                <td class="text-nowrap">
                                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editCategory(${c.id})">
                                        <i class="fas fa-edit"></i> <span data-i18n="edit">Edit</span>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteCategory(${c.id})">
                                        <i class="fas fa-trash"></i> <span data-i18n="delete">Delete</span>
                                    </button>
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="3" class="text-center text-muted">No categories found.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Failed to load categories: ${error.message}</div>`;
    }
}

function openCategoryModal() {
    editingCategoryId = null;
    document.getElementById('categoryForm').reset();
    const btn = document.getElementById('categorySaveBtn');
    if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Save Category';
    new bootstrap.Modal(document.getElementById('categoryModal')).show();
}

async function editCategory(id) {
    try {
        const categories = await api.getCategories();
        const c = categories.find(x => x.id === id);
        if (!c) { SwalAlert.error('Category not found'); return; }
        editingCategoryId = id;
        document.getElementById('category_name').value = c.name || '';
        document.getElementById('category_description').value = c.description || '';
        const btn = document.getElementById('categorySaveBtn');
        if (btn) btn.innerHTML = '<i class="fas fa-save"></i> Update Category';
        new bootstrap.Modal(document.getElementById('categoryModal')).show();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function saveCategory() {
    const data = {
        name: document.getElementById('category_name').value,
        description: document.getElementById('category_description').value || null
    };

    if (!data.name) {
        SwalAlert.warning('Category name is required!');
        return;
    }

    try {
        if (editingCategoryId) {
            await api.updateCategory(editingCategoryId, data);
            SwalAlert.success('Category updated successfully!');
        } else {
            await api.createCategory(data);
            SwalAlert.success('Category added successfully!');
        }
        editingCategoryId = null;
        bootstrap.Modal.getInstance(document.getElementById('categoryModal')).hide();
        renderCategories();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

async function deleteCategory(id) {
    const result = await SwalAlert.confirm('Delete this category? This action cannot be undone.');
    if (!result.isConfirmed) return;
    try {
        await api.deleteCategory(id);
        SwalAlert.success('Category deleted successfully!');
        renderCategories();
    } catch (error) {
        SwalAlert.error(error.message);
    }
}

console.log('Categories module loaded');
