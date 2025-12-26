import { defineStore } from 'pinia'
import { authAPI } from '@/api'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: JSON.parse(localStorage.getItem('user') || 'null'),
        token: localStorage.getItem('token') || null,
        loading: false,
        error: null
    }),

    getters: {
        isAuthenticated: (state) => !!state.token,
        userRole: (state) => state.user?.role?.name || 'viewer',
        userName: (state) => state.user?.full_name || 'User',
        userInitials: (state) => {
            if (!state.user?.full_name) return 'U'
            return state.user.full_name
                .split(' ')
                .map(n => n[0])
                .join('')
                .toUpperCase()
                .slice(0, 2)
        },
        canEdit: (state) => ['admin', 'editor', 'approver'].includes(state.user?.role?.name),
        canApprove: (state) => ['admin', 'approver'].includes(state.user?.role?.name),
        isAdmin: (state) => state.user?.role?.name === 'admin'
    },

    actions: {
        async login(email, password) {
            this.loading = true
            this.error = null

            try {
                const response = await authAPI.login(email, password)
                const { access_token, user } = response.data

                this.token = access_token
                this.user = user

                localStorage.setItem('token', access_token)
                localStorage.setItem('user', JSON.stringify(user))

                return true
            } catch (error) {
                this.error = error.response?.data?.detail || 'Login gagal'
                return false
            } finally {
                this.loading = false
            }
        },

        async logout() {
            try {
                await authAPI.logout()
            } catch (e) {
                // Ignore logout errors
            }

            this.token = null
            this.user = null

            localStorage.removeItem('token')
            localStorage.removeItem('user')
        },

        async fetchUser() {
            if (!this.token) return

            try {
                const response = await authAPI.me()
                this.user = response.data
                localStorage.setItem('user', JSON.stringify(response.data))
            } catch (error) {
                this.logout()
            }
        }
    }
})
