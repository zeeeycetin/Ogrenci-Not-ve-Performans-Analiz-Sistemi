/* ============================================================
   EduTrack — Ana JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initNotifications();
    initTooltips();
    initCountUp();
});

/* ── Sidebar ────────────────────────────────────────────────── */
function initSidebar() {
    const toggle  = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const main    = document.getElementById('mainContent');
    const overlay = document.getElementById('sidebarOverlay');
    if (!toggle || !sidebar) return;

    const isMobile = () => window.innerWidth < 768;

    function openMobile()  {
        sidebar.classList.add('open');
        overlay && overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    function closeMobile() {
        sidebar.classList.remove('open');
        overlay && overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    toggle.addEventListener('click', () => {
        if (isMobile()) {
            sidebar.classList.contains('open') ? closeMobile() : openMobile();
        } else {
            sidebar.classList.toggle('collapsed');
            main && main.classList.toggle('expanded');
        }
    });

    overlay && overlay.addEventListener('click', closeMobile);
    window.addEventListener('resize', () => { if (!isMobile()) closeMobile(); });
}

/* ── Notifications ──────────────────────────────────────────── */
function initNotifications() {
    const btn      = document.getElementById('notifToggle');
    const panel    = document.getElementById('notifPanel');
    const backdrop = document.getElementById('notifBackdrop');
    const close    = document.getElementById('notifClose');
    const dot      = document.getElementById('notifDot');
    if (!btn || !panel) return;

    let loaded = false;

    function openPanel() {
        panel.classList.add('open');
        backdrop.classList.add('active');
        if (!loaded) { loadNotifications(); loaded = true; }
    }
    function closePanel() {
        panel.classList.remove('open');
        backdrop.classList.remove('active');
    }

    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        panel.classList.contains('open') ? closePanel() : openPanel();
    });
    backdrop.addEventListener('click', closePanel);
    close && close.addEventListener('click', closePanel);
}

async function loadNotifications() {
    const body = document.getElementById('notifBody');
    const dot  = document.getElementById('notifDot');
    if (!body) return;

    try {
        const res  = await fetch('/api/notifications');
        const data = await res.json();
        const items = data.data || data || [];

        if (!items.length) {
            body.innerHTML = `<div class="empty-state py-4">
                <i class="bi bi-bell-slash"></i>
                <p>Bildirim bulunmuyor.</p>
            </div>`;
            return;
        }

        dot && dot.classList.add('visible');

        const typeMap = {
            attendance_warning: { icon: 'bi-calendar-x-fill', cls: 'ni-warning' },
            low_grade_risk:     { icon: 'bi-exclamation-triangle-fill', cls: 'ni-danger' },
            performance_drop:   { icon: 'bi-arrow-down-circle-fill', cls: 'ni-danger' },
            performance_rise:   { icon: 'bi-arrow-up-circle-fill', cls: 'ni-success' },
            study_plan:         { icon: 'bi-journal-bookmark-fill', cls: 'ni-info' },
            time_management:    { icon: 'bi-clock-fill', cls: 'ni-info' },
        };

        body.innerHTML = items.map(n => {
            const t = typeMap[n.notification_type] || { icon: 'bi-bell-fill', cls: 'ni-info' };
            return `<div class="notif-item">
                <div class="notif-icon ${t.cls}"><i class="bi ${t.icon}"></i></div>
                <div>
                    <div class="notif-title">${n.title}</div>
                    <div class="notif-msg">${n.message.substring(0, 80)}${n.message.length > 80 ? '…' : ''}</div>
                    <div class="notif-time">${formatTime(n.created_at)}</div>
                </div>
            </div>`;
        }).join('');
    } catch {
        body.innerHTML = `<div class="empty-state py-3"><p class="small">Bildirimler yüklenemedi.</p></div>`;
    }
}

function formatTime(isoStr) {
    if (!isoStr) return '';
    const d = new Date(isoStr);
    if (isNaN(d)) return '';
    const now = new Date();
    const diff = Math.floor((now - d) / 60000);
    if (diff < 1)  return 'Az önce';
    if (diff < 60) return `${diff} dk önce`;
    if (diff < 1440) return `${Math.floor(diff/60)} saat önce`;
    return d.toLocaleDateString('tr-TR');
}

/* ── Tooltips ───────────────────────────────────────────────── */
function initTooltips() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        new bootstrap.Tooltip(el);
    });
}

/* ── Count-up animation for stat values ─────────────────────── */
function initCountUp() {
    const els = document.querySelectorAll('.stat-value[data-count]');
    if (!els.length) return;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                countUp(e.target);
                observer.unobserve(e.target);
            }
        });
    }, { threshold: .5 });
    els.forEach(el => observer.observe(el));
}

function countUp(el) {
    const target = parseFloat(el.dataset.count);
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    const decimals = el.dataset.decimals ? parseInt(el.dataset.decimals) : 0;
    const duration = 800;
    const start = performance.now();
    const step = (now) => {
        const p = Math.min((now - start) / duration, 1);
        const v = target * (p < .5 ? 2*p*p : -1+(4-2*p)*p);
        el.textContent = prefix + v.toFixed(decimals) + suffix;
        if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

/* ── Toast notification ─────────────────────────────────────── */
function showToast(type, message) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const id = 'toast_' + Date.now();
    const icons = { success: 'check-circle-fill', danger: 'exclamation-triangle-fill',
                    warning: 'exclamation-circle-fill', info: 'info-circle-fill' };
    container.insertAdjacentHTML('beforeend', `
        <div id="${id}" class="toast align-items-center text-bg-${type} border-0 shadow" role="alert">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center gap-2">
                    <i class="bi bi-${icons[type]||'bell'}"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>`);
    const el = document.getElementById(id);
    const toast = new bootstrap.Toast(el, { delay: 3500 });
    toast.show();
    el.addEventListener('hidden.bs.toast', () => el.remove());
}

/* ── API helper ─────────────────────────────────────────────── */
async function apiCall(method, url, body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    return res.json();
}

/* ── Generate recommendations ───────────────────────────────── */
async function generateRecs(studentId) {
    const btn = event.target.closest('button');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Üretiliyor...';
    const result = await apiCall('POST', `/analytics/student/${studentId}/recommendations/generate`);
    showToast(result.success ? 'success' : 'danger', result.message || 'İşlem tamamlandı.');
    if (result.success) setTimeout(() => location.reload(), 1500);
    else {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-lightning-fill me-2"></i>Öneri Üret';
    }
}

/* ── Chart.js gradient helper ───────────────────────────────── */
function makeGradient(ctx, color1, color2, vertical = true) {
    const g = vertical
        ? ctx.createLinearGradient(0, 0, 0, 300)
        : ctx.createLinearGradient(0, 0, 300, 0);
    g.addColorStop(0, color1);
    g.addColorStop(1, color2);
    return g;
}
