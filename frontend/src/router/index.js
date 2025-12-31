import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/LoginView.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/transactions',
        name: 'Transactions',
        component: () => import('@/views/TransactionsView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/accounts',
        name: 'Accounts',
        component: () => import('@/views/AccountsView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/budgets',
        name: 'Budgets',
        component: () => import('@/views/BudgetsView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/reports',
        name: 'Reports',
        component: () => import('@/views/ReportsView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/users',
        name: 'Users',
        component: () => import('@/views/UsersView.vue'),
        meta: { requiresAuth: true, requiredRole: ['admin'] }
    },
    {
        path: '/audit-logs',
        name: 'AuditLogs',
        component: () => import('@/views/AuditLogsView.vue'),
        meta: { requiresAuth: true, requiredRole: ['admin', 'approver'] }
    },
    {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/invoices',
        name: 'Invoices',
        component: () => import('@/views/InvoicesView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/SettingsView.vue'),
        meta: { requiresAuth: true, requiredRole: ['admin'] }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const user = JSON.parse(localStorage.getItem('user') || '{}')

    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.path === '/login' && token) {
        next('/')
    } else if (to.meta.requiredRole && !to.meta.requiredRole.includes(user.role?.name)) {
        next('/')
    } else {
        next()
    }
})

export default router
