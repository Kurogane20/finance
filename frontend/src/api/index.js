import axios from 'axios'

// Use VITE_API_URL from environment, fallback to /api for development
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor to handle errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default api

// Auth API
export const authAPI = {
    login: (email, password) => api.post('/auth/login', { email, password }),
    me: () => api.get('/auth/me'),
    logout: () => api.post('/auth/logout')
}

// Dashboard API
export const dashboardAPI = {
    getOverview: (period = 'month') => api.get('/dashboard/overview', { params: { period } }),
    getCharts: (period = 'month') => api.get('/dashboard/charts', { params: { period } })
}

// Transactions API
export const transactionsAPI = {
    getAll: (params = {}) => api.get('/transactions', { params }),
    getSummary: () => api.get('/transactions/summary'),
    getCategories: (type) => api.get('/transactions/categories', { params: { type } }),
    getById: (id) => api.get(`/transactions/${id}`),
    create: (data) => api.post('/transactions', data),
    update: (id, data) => api.put(`/transactions/${id}`, data),
    delete: (id) => api.delete(`/transactions/${id}`),
    importCSV: (formData) => api.post('/transactions/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
}

// Accounts API
export const accountsAPI = {
    getAll: (params = {}) => api.get('/accounts', { params }),
    getSummary: () => api.get('/accounts/summary'),
    getAging: (type = 'receivable') => api.get('/accounts/aging', { params: { type } }),
    getById: (id) => api.get(`/accounts/${id}`),
    create: (data) => api.post('/accounts', data),
    update: (id, data) => api.put(`/accounts/${id}`, data)
}

// Budgets API
export const budgetsAPI = {
    getAll: (params = {}) => api.get('/budgets', { params }),
    getComparison: (period) => api.get('/budgets/comparison', { params: { period } }),
    getDepartments: () => api.get('/budgets/departments'),
    create: (data) => api.post('/budgets', data),
    update: (id, data) => api.put(`/budgets/${id}`, data),
    delete: (id) => api.delete(`/budgets/${id}`)
}

// Reports API
export const reportsAPI = {
    getProfitLoss: (startDate, endDate) => api.get('/reports/profit-loss', { params: { start_date: startDate, end_date: endDate } }),
    getCashFlow: (year, month) => api.get('/reports/cash-flow', { params: { year, month } }),
    getBalanceSheet: (asOfDate) => api.get('/reports/balance-sheet', { params: { as_of_date: asOfDate } }),
    exportTransactions: (startDate, endDate) => api.get('/reports/export/transactions', { params: { start_date: startDate, end_date: endDate }, responseType: 'blob' })
}

// Users API
export const usersAPI = {
    getAll: (params = {}) => api.get('/users', { params }),
    getRoles: () => api.get('/users/roles'),
    getById: (id) => api.get(`/users/${id}`),
    create: (data) => api.post('/users', data),
    update: (id, data) => api.put(`/users/${id}`, data),
    delete: (id) => api.delete(`/users/${id}`),
    getAuditLogs: (params = {}) => api.get('/users/audit-logs/all', { params }),
    // Profile
    getProfile: () => api.get('/users/profile/me'),
    updateProfile: (data) => api.put('/users/profile/me', data),
    changePassword: (currentPassword, newPassword) => api.post('/users/profile/change-password', { current_password: currentPassword, new_password: newPassword })
}

// Invoices API
export const invoicesAPI = {
    getAll: (params = {}) => api.get('/accounts/invoices', { params }),
    getById: (id) => api.get(`/accounts/invoices/${id}`),
    create: (data) => api.post('/accounts/invoices', data),
    update: (id, data) => api.put(`/accounts/invoices/${id}`, data),
    delete: (id) => api.delete(`/accounts/invoices/${id}`)
}

// Settings API
export const settingsAPI = {
    getCompany: () => api.get('/settings/company'),
    updateCompany: (data) => api.put('/settings/company', data),
    getPreferences: () => api.get('/settings/preferences'),
    updatePreferences: (data) => api.put('/settings/preferences', data)
}
