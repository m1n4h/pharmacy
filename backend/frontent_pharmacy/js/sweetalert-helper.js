// ============================================
// SWEETALERT2 HELPER — Shows messages from backend
// ============================================

window.SwalAlert = {
    success(message) {
        return Swal.fire({
            icon: 'success',
            title: 'Success',
            text: message || 'Operation completed successfully',
            confirmButtonColor: '#10b981',
            timer: 3000,
            timerProgressBar: true
        });
    },

    error(message) {
        return Swal.fire({
            icon: 'error',
            title: 'Error',
            text: message || 'Something went wrong',
            confirmButtonColor: '#ef4444'
        });
    },

    warning(message) {
        return Swal.fire({
            icon: 'warning',
            title: 'Warning',
            text: message || 'Please check your input',
            confirmButtonColor: '#f59e0b'
        });
    },

    info(message) {
        return Swal.fire({
            icon: 'info',
            title: 'Info',
            text: message || '',
            confirmButtonColor: '#2563eb'
        });
    },

    confirm(message) {
        return Swal.fire({
            title: 'Are you sure?',
            text: message || 'This action cannot be undone',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#ef4444',
            cancelButtonColor: '#6b7280',
            confirmButtonText: 'Yes, proceed',
            cancelButtonText: 'Cancel'
        });
    },

    confirmDelete() {
        return Swal.fire({
            title: 'Delete?',
            text: 'This action cannot be undone',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#ef4444',
            cancelButtonColor: '#6b7280',
            confirmButtonText: 'Yes, delete it',
            cancelButtonText: 'Cancel'
        });
    },

    fromBackend(response) {
        if (response && response.success === false) {
            return this.error(response.message || 'Operation failed');
        }
        if (response && response.success === true) {
            return this.success(response.message || 'Operation completed');
        }
        return this.success('Operation completed');
    }
};

console.log('SweetAlert helper loaded');
