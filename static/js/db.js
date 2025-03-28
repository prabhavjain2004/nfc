class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('access_token');
    }

    async _fetch(endpoint, options = {}) {
        try {
            const headers = {
                'Content-Type': 'application/json',
                ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
                ...options.headers
            };

            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                headers
            });

            if (response.status === 401) {
                // Token expired, try to refresh
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Retry the original request
                    return this._fetch(endpoint, options);
                } else {
                    // Refresh failed, redirect to login
                    window.location.href = '/';
                    throw new Error('Authentication failed');
                }
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'API request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.baseURL}/api/token/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh: refreshToken })
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            this.token = data.access;
            return true;
        } catch (error) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            return false;
        }
    }

    // User Operations
    async getCurrentUser() {
        return this._fetch('/api/users/me/');
    }

    async getUsers() {
        return this._fetch('/api/users/');
    }

    async createUser(userData) {
        return this._fetch('/api/users/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async updateUser(userId, userData) {
        return this._fetch(`/api/users/${userId}/`, {
            method: 'PATCH',
            body: JSON.stringify(userData)
        });
    }

    // Card Operations
    async getCards() {
        return this._fetch('/api/cards/');
    }

    async issueCard(cardData) {
        return this._fetch('/api/cards/', {
            method: 'POST',
            body: JSON.stringify(cardData)
        });
    }

    async linkCard(cardNumber) {
        return this._fetch('/api/cards/link_card/', {
            method: 'POST',
            body: JSON.stringify({ card_number: cardNumber })
        });
    }

    async rechargeCard(cardNumber, amount) {
        return this._fetch('/api/recharge/', {
            method: 'POST',
            body: JSON.stringify({
                card_number: cardNumber,
                amount: amount
            })
        });
    }

    // Transaction Operations
    async getTransactions() {
        return this._fetch('/api/transactions/');
    }

    async makePayment(cardNumber, amount, outletId) {
        return this._fetch('/api/transactions/make_payment/', {
            method: 'POST',
            body: JSON.stringify({
                card_number: cardNumber,
                amount: amount,
                outlet_id: outletId
            })
        });
    }

    // Settlement Operations
    async getSettlements() {
        return this._fetch('/api/settlements/');
    }

    async processSettlement(settlementId) {
        return this._fetch(`/api/settlements/${settlementId}/process/`, {
            method: 'POST'
        });
    }

    // Analytics Operations
    async getAnalytics() {
        return this._fetch('/api/analytics/');
    }
}

// Error handling utility
class APIError extends Error {
    constructor(message, status) {
        super(message);
        this.name = 'APIError';
        this.status = status;
    }
}

// Helper functions for common operations
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
};

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Example usage:
/*
const api = new APIClient();

// Get current user
async function getCurrentUser() {
    try {
        const user = await api.getCurrentUser();
        console.log('Current user:', user);
    } catch (error) {
        console.error('Error getting current user:', error);
    }
}

// Make a payment
async function processPayment(cardNumber, amount, outletId) {
    try {
        const transaction = await api.makePayment(cardNumber, amount, outletId);
        console.log('Payment processed:', transaction);
        return transaction;
    } catch (error) {
        console.error('Payment failed:', error);
        throw error;
    }
}

// Get analytics
async function getSystemAnalytics() {
    try {
        const analytics = await api.getAnalytics();
        console.log('System analytics:', analytics);
        return analytics;
    } catch (error) {
        console.error('Error fetching analytics:', error);
        throw error;
    }
}
*/
