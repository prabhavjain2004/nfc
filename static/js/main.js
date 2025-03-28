// Initialize API client
const api = new APIClient();

// Authentication state management
class AuthManager {
    static isAuthenticated() {
        return !!localStorage.getItem('access_token');
    }

    static getToken() {
        return localStorage.getItem('access_token');
    }

    static logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/';
    }

    static async checkAuthAndRedirect() {
        if (!this.isAuthenticated()) {
            window.location.href = '/';
            return false;
        }

        try {
            const user = await api.getCurrentUser();
            return this.handleUserRole(user);
        } catch (error) {
            console.error('Auth check failed:', error);
            this.logout();
            return false;
        }
    }

    static handleUserRole(user) {
        const currentPath = window.location.pathname;
        let correctPath;

        switch (user.role) {
            case 'CUSTOMER':
                correctPath = '/dashboard/customer/';
                break;
            case 'OUTLET':
                correctPath = '/dashboard/outlet/';
                break;
            case 'ADMIN':
                correctPath = '/dashboard/admin/';
                break;
            default:
                this.logout();
                return false;
        }

        if (currentPath !== correctPath) {
            window.location.href = correctPath;
            return false;
        }

        return true;
    }
}

// UI Components
class UIComponents {
    static showLoading() {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.id = 'loadingSpinner';
        document.body.appendChild(spinner);
    }

    static hideLoading() {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.remove();
        }
    }

    static showAlert(message, type = 'success') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        
        const container = document.querySelector('.main-content');
        container.insertBefore(alert, container.firstChild);

        setTimeout(() => alert.remove(), 5000);
    }

    static showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
        }
    }

    static hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }

    static updateTable(tableId, data, columns) {
        const table = document.getElementById(tableId);
        if (!table) return;

        const tbody = table.querySelector('tbody');
        tbody.innerHTML = '';

        data.forEach(item => {
            const row = document.createElement('tr');
            columns.forEach(column => {
                const cell = document.createElement('td');
                cell.innerHTML = column.render ? column.render(item) : item[column.key];
                row.appendChild(cell);
            });
            tbody.appendChild(row);
        });
    }
}

// NFC Payment Handler
class NFCPaymentHandler {
    constructor() {
        this.nfcReader = new NFCReader({
            onCardDetected: this.handleCardDetected.bind(this),
            onReading: this.handleReading.bind(this),
            onError: this.handleError.bind(this)
        });
    }

    async initialize() {
        try {
            await this.nfcReader.init();
            UIComponents.showAlert('NFC Reader initialized successfully');
            return true;
        } catch (error) {
            UIComponents.showAlert('Failed to initialize NFC Reader', 'danger');
            return false;
        }
    }

    handleCardDetected(card) {
        document.dispatchEvent(new CustomEvent('nfcCardDetected', { detail: card }));
    }

    handleReading({ serialNumber, message }) {
        document.dispatchEvent(new CustomEvent('nfcCardRead', {
            detail: { serialNumber, message }
        }));
    }

    handleError(error) {
        UIComponents.showAlert(`NFC Error: ${error.message}`, 'danger');
    }

    stop() {
        this.nfcReader.stop();
    }
}

// Form Handlers
class FormHandler {
    static async handleSubmit(event, endpoint, successMessage) {
        event.preventDefault();
        UIComponents.showLoading();

        try {
            const formData = new FormData(event.target);
            const data = Object.fromEntries(formData.entries());

            const response = await api._fetch(endpoint, {
                method: 'POST',
                body: JSON.stringify(data)
            });

            UIComponents.showAlert(successMessage);
            return response;
        } catch (error) {
            UIComponents.showAlert(error.message, 'danger');
            throw error;
        } finally {
            UIComponents.hideLoading();
        }
    }

    static setupForm(formId, endpoint, successMessage, onSuccess) {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', async (event) => {
                try {
                    const response = await this.handleSubmit(event, endpoint, successMessage);
                    if (onSuccess) {
                        onSuccess(response);
                    }
                } catch (error) {
                    console.error('Form submission error:', error);
                }
            });
        }
    }
}

// Data Refresh Manager
class DataRefreshManager {
    constructor(refreshInterval = 30000) {
        this.refreshInterval = refreshInterval;
        this.refreshFunctions = new Map();
        this.intervalId = null;
    }

    addRefreshFunction(key, func) {
        this.refreshFunctions.set(key, func);
    }

    removeRefreshFunction(key) {
        this.refreshFunctions.delete(key);
    }

    start() {
        this.refresh();
        this.intervalId = setInterval(() => this.refresh(), this.refreshInterval);
    }

    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    async refresh() {
        for (const [key, func] of this.refreshFunctions) {
            try {
                await func();
            } catch (error) {
                console.error(`Error refreshing ${key}:`, error);
            }
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    if (!await AuthManager.checkAuthAndRedirect()) {
        return;
    }

    // Setup logout handlers
    document.querySelectorAll('#logout').forEach(button => {
        button.addEventListener('click', () => AuthManager.logout());
    });

    // Initialize data refresh
    const refreshManager = new DataRefreshManager();
    
    // Add specific initialization based on page type
    const path = window.location.pathname;
    if (path.includes('/dashboard/outlet/')) {
        const nfcHandler = new NFCPaymentHandler();
        await nfcHandler.initialize();
    }

    // Start periodic refresh
    refreshManager.start();
});

// Export for use in other scripts
window.AuthManager = AuthManager;
window.UIComponents = UIComponents;
window.FormHandler = FormHandler;
window.api = api;
