// ============================================
// DARK MODE / LIGHT MODE THEME SYSTEM
// ============================================

window.ThemeManager = {
    STORAGE_KEY: 'pharmacy_theme',
    
    get current() {
        return localStorage.getItem(this.STORAGE_KEY) || 'light';
    },
    
    apply(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(this.STORAGE_KEY, theme);
        const btn = document.getElementById('themeToggle');
        if (btn) {
            btn.innerHTML = theme === 'dark' 
                ? '<i class="fas fa-sun"></i>' 
                : '<i class="fas fa-moon"></i>';
            btn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
        }
    },
    
    toggle() {
        const next = this.current === 'dark' ? 'light' : 'dark';
        this.apply(next);
    },
    
    init() {
        const saved = localStorage.getItem(this.STORAGE_KEY);
        if (!saved) {
            const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            this.apply(prefersDark ? 'dark' : 'light');
        } else {
            this.apply(saved);
        }
    }
};

console.log('Theme module loaded');
