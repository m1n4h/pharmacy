// ============================================
// NOTIFICATION CENTER
// ============================================

async function loadNotifications() {
    try {
        const res = await api.getNotifications({ limit: 15 });
        const data = res.data || {};
        const items = data.items || [];
        const unread = data.unread_count || 0;
        const badge = document.getElementById('notifBadge');
        if (badge) {
            if (unread > 0) {
                badge.textContent = unread;
                badge.classList.remove('d-none');
            } else {
                badge.classList.add('d-none');
            }
        }
        const list = document.getElementById('notificationList');
        if (list) {
            list.innerHTML = items.length ? items.map(n => `
                <div class="p-3 border-bottom ${n.is_read ? '' : 'bg-light'}" style="cursor:pointer;" onclick="openNotification(${n.id}, ${n.reference_id || 'null'}, '${n.module || ''}')">
                    <div class="d-flex justify-content-between">
                        <strong class="${n.is_read ? 'text-muted' : ''}">${n.title}</strong>
                        ${n.is_read ? '' : '<span class="badge bg-primary">New</span>'}
                    </div>
                    <div class="small text-muted">${n.message || ''}</div>
                    <div class="small text-muted">${n.created_at}</div>
                </div>
            `).join('') : '<p class="text-muted text-center p-3">No notifications.</p>';
        }
    } catch (e) {
        console.warn('Notification load failed', e);
    }
}

function toggleNotificationPanel() {
    const panel = document.getElementById('notificationPanel');
    const backdrop = document.getElementById('notifBackdrop');
    if (!panel) return;
    const open = panel.classList.contains('open');
    if (open) {
        panel.classList.remove('open');
        backdrop.classList.remove('show');
    } else {
        panel.classList.add('open');
        backdrop.classList.add('show');
        loadNotifications();
    }
}

async function openNotification(id, refId, module) {
    try {
        await api.markNotificationRead(id);
    } catch (e) {}
    loadNotifications();
    // If reference available, could navigate; keep simple for now.
}

async function markAllNotificationsRead() {
    // mark all read via read-all endpoint then reload
    try {
        await api.markAllNotificationsRead();
    } catch (e) {}
    loadNotifications();
}

console.log('Notifications module loaded');
