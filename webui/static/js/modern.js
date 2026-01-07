/**
 * Modern UI JavaScript - Router Phase 1
 * Common functionality for the new UI phase
 */

// Global utilities
const UI = {
    // Theme management
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    },

    getTheme() {
        return localStorage.getItem('theme') || 'light';
    },

    initTheme() {
        const theme = this.getTheme();
        this.setTheme(theme);
    },

    // Toast notifications
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        document.body.appendChild(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }

        return toast;
    },

    // Modal management
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    },

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    },

    // Loading states
    showLoading(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.classList.add('loading');
        }
    },

    hideLoading(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.classList.remove('loading');
        }
    },

    // Form validation
    validateForm(form) {
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });

        return isValid;
    },

    showFieldError(input, message) {
        this.clearFieldError(input);

        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;

        input.classList.add('error');
        input.parentElement.appendChild(errorDiv);
    },

    clearFieldError(input) {
        input.classList.remove('error');
        const errorDiv = input.parentElement.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    },

    // API helpers
    async apiRequest(endpoint, options = {}) {
        const token = localStorage.getItem('accessToken');

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };

        const response = await fetch(endpoint, { ...defaultOptions, ...options });

        if (response.status === 401) {
            // Token expired, redirect to login
            window.location.href = '/login';
            return;
        }

        return response;
    },

    // Keyboard shortcuts
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K: Focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('input[type="search"], .search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            }

            // Escape: Close modals
            if (e.key === 'Escape') {
                const openModals = document.querySelectorAll('.modal[style*="display: flex"]');
                openModals.forEach(modal => {
                    modal.style.display = 'none';
                    document.body.style.overflow = '';
                });
            }
        });
    },

    // Responsive utilities
    isMobile() {
        return window.innerWidth < 768;
    },

    isTablet() {
        return window.innerWidth >= 768 && window.innerWidth < 1024;
    },

    isDesktop() {
        return window.innerWidth >= 1024;
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    UI.initTheme();
    UI.initKeyboardShortcuts();

    // Add loading class to body initially
    document.body.classList.add('loaded');

    // Initialize tooltips if any
    initTooltips();

    // Initialize popovers if any
    initPopovers();
});

function initTooltips() {
    // Simple tooltip system
    const tooltipElements = document.querySelectorAll('[data-tooltip]');

    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });

    function showTooltip(e) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = e.target.dataset.tooltip;

        document.body.appendChild(tooltip);

        const rect = e.target.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';

        tooltip.classList.add('show');
    }

    function hideTooltip() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.classList.remove('show');
            setTimeout(() => tooltip.remove(), 200);
        }
    }
}

function initPopovers() {
    // Placeholder for popover system
    const popoverElements = document.querySelectorAll('[data-popover]');

    popoverElements.forEach(el => {
        el.addEventListener('click', togglePopover);
    });

    function togglePopover(e) {
        // Implement popover toggle logic
        console.log('Popover clicked:', e.target.dataset.popover);
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown date';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function formatRelativeTime(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

    return formatDate(dateString);
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            UI.showToast('Copied to clipboard', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        UI.showToast('Copied to clipboard', 'success');
    }
}

function downloadFile(content, filename, contentType = 'text/plain') {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Global Navigation Component
class GlobalNav {
    constructor() {
        this.init();
    }

    init() {
        this.createNav();
        this.setupEventListeners();
        this.updateActiveState();
    }

    createNav() {
        // Only add nav if it doesn't exist
        if (document.querySelector('.global-nav')) return;

        const nav = document.createElement('nav');
        nav.className = 'global-nav';
        nav.innerHTML = `
            <div class="nav-container">
                <div class="nav-brand">
                    <a href="/" class="brand-link">
                        <span class="brand-icon">🔬</span>
                        <span class="brand-text">Router Phase 1</span>
                    </a>
                </div>
                <div class="nav-links">
                    <a href="/" class="nav-link" data-page="home">
                        <span class="nav-icon">🏠</span>
                        <span class="nav-text">Home</span>
                    </a>
                    <a href="/dashboard" class="nav-link" data-page="dashboard">
                        <span class="nav-icon">📊</span>
                        <span class="nav-text">Dashboard</span>
                    </a>
                    <a href="/chat" class="nav-link" data-page="chat">
                        <span class="nav-icon">💬</span>
                        <span class="nav-text">Chat</span>
                    </a>
                    <a href="/research" class="nav-link" data-page="research">
                        <span class="nav-icon">🔬</span>
                        <span class="nav-text">Research</span>
                    </a>
                    <a href="/knowledge" class="nav-link" data-page="knowledge">
                        <span class="nav-icon">📚</span>
                        <span class="nav-text">Knowledge</span>
                    </a>
                    <a href="/search" class="nav-link" data-page="search">
                        <span class="nav-icon">🔍</span>
                        <span class="nav-text">Search</span>
                    </a>
                </div>
                <div class="nav-actions">
                    <button class="nav-btn" id="themeToggle" title="Toggle theme">
                        🌙
                    </button>
                    <button class="nav-btn" id="notificationsBtn" title="Notifications">
                        🔔
                    </button>
                    <div class="user-menu">
                        <button class="user-btn" id="userMenuBtn">
                            <span class="user-avatar">👤</span>
                        </button>
                        <div class="user-dropdown" id="userDropdown">
                            <a href="/profile" class="dropdown-item">
                                <span class="dropdown-icon">👤</span>
                                Profile
                            </a>
                            <a href="/settings" class="dropdown-item">
                                <span class="dropdown-icon">⚙️</span>
                                Settings
                            </a>
                            <a href="/help" class="dropdown-item">
                                <span class="dropdown-icon">❓</span>
                                Help
                            </a>
                            <div class="dropdown-divider"></div>
                            <a href="#" class="dropdown-item" id="logoutBtn">
                                <span class="dropdown-icon">🚪</span>
                                Logout
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Insert at the top of the body
        document.body.insertBefore(nav, document.body.firstChild);

        // Add CSS for the nav
        this.addNavStyles();
    }

    addNavStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .global-nav {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: var(--card-bg);
                border-bottom: 1px solid var(--border-color);
                box-shadow: var(--shadow-sm);
                z-index: 1000;
                backdrop-filter: blur(10px);
            }

            .nav-container {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 var(--spacing-lg);
                height: 60px;
                max-width: var(--max-width);
                margin: 0 auto;
            }

            .nav-brand .brand-link {
                display: flex;
                align-items: center;
                gap: var(--spacing-sm);
                text-decoration: none;
                color: var(--text-primary);
                font-weight: 600;
            }

            .brand-icon {
                font-size: var(--font-size-xl);
            }

            .nav-links {
                display: flex;
                gap: var(--spacing-lg);
            }

            .nav-link {
                display: flex;
                align-items: center;
                gap: var(--spacing-xs);
                padding: var(--spacing-sm) var(--spacing-md);
                text-decoration: none;
                color: var(--text-secondary);
                border-radius: var(--radius-md);
                transition: all var(--transition-fast);
            }

            .nav-link:hover {
                background: var(--surface-color);
                color: var(--text-primary);
            }

            .nav-link.active {
                background: var(--primary-color);
                color: white;
            }

            .nav-actions {
                display: flex;
                align-items: center;
                gap: var(--spacing-sm);
            }

            .nav-btn {
                background: none;
                border: none;
                padding: var(--spacing-sm);
                border-radius: var(--radius-md);
                cursor: pointer;
                font-size: var(--font-size-lg);
                transition: background-color var(--transition-fast);
            }

            .nav-btn:hover {
                background: var(--surface-color);
            }

            .user-menu {
                position: relative;
            }

            .user-btn {
                background: none;
                border: none;
                padding: var(--spacing-xs);
                border-radius: 50%;
                cursor: pointer;
                transition: background-color var(--transition-fast);
            }

            .user-btn:hover {
                background: var(--surface-color);
            }

            .user-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                background: var(--primary-color);
                color: white;
                font-size: var(--font-size-sm);
            }

            .user-dropdown {
                position: absolute;
                top: 100%;
                right: 0;
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-lg);
                min-width: 200px;
                opacity: 0;
                visibility: hidden;
                transform: translateY(-10px);
                transition: all var(--transition-fast);
            }

            .user-dropdown.show {
                opacity: 1;
                visibility: visible;
                transform: translateY(0);
            }

            .dropdown-item {
                display: flex;
                align-items: center;
                gap: var(--spacing-sm);
                padding: var(--spacing-md);
                text-decoration: none;
                color: var(--text-primary);
                transition: background-color var(--transition-fast);
            }

            .dropdown-item:hover {
                background: var(--surface-color);
            }

            .dropdown-divider {
                height: 1px;
                background: var(--border-color);
                margin: var(--spacing-xs) 0;
            }

            .dropdown-icon {
                width: 16px;
                text-align: center;
            }

            /* Mobile responsive */
            @media (max-width: 768px) {
                .nav-links {
                    display: none;
                }

                .nav-brand .brand-text {
                    display: none;
                }

                .nav-container {
                    padding: 0 var(--spacing-md);
                }
            }

            /* Adjust main content for fixed nav */
            .main-content {
                padding-top: 80px;
            }

            .landing-page .main-content {
                padding-top: 0;
            }

            .auth-page .main-content {
                padding-top: 0;
            }
        `;
        document.head.appendChild(style);
    }

    setupEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = UI.getTheme();
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                UI.setTheme(newTheme);
                this.updateThemeIcon(newTheme);
            });
            this.updateThemeIcon(UI.getTheme());
        }

        // User menu
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');

        if (userMenuBtn && userDropdown) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('show');
            });

            document.addEventListener('click', () => {
                userDropdown.classList.remove('show');
            });
        }

        // Logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                localStorage.removeItem('accessToken');
                window.location.href = '/login';
            });
        }

        // Notifications (placeholder)
        const notificationsBtn = document.getElementById('notificationsBtn');
        if (notificationsBtn) {
            notificationsBtn.addEventListener('click', () => {
                UI.showToast('Notifications coming soon!', 'info');
            });
        }
    }

    updateThemeIcon(theme) {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
            themeToggle.title = `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`;
        }
    }

    updateActiveState() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            const page = link.dataset.page;
            const href = link.getAttribute('href');

            if (href === currentPath || (page === 'home' && currentPath === '/')) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
}

// Initialize global navigation
document.addEventListener('DOMContentLoaded', function() {
    // Only add global nav if not on landing or auth pages
    const isLandingPage = document.body.classList.contains('landing-page');
    const isAuthPage = document.body.classList.contains('auth-page');

    if (!isLandingPage && !isAuthPage) {
        window.globalNav = new GlobalNav();
    }
});

// Export for use in other scripts
window.UI = UI;
window.debounce = debounce;
window.throttle = throttle;
window.formatDate = formatDate;
window.formatRelativeTime = formatRelativeTime;
window.copyToClipboard = copyToClipboard;
window.downloadFile = downloadFile;