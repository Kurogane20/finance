import { defineStore } from 'pinia'
import { dashboardAPI, transactionsAPI } from '@/api'

export const useDashboardStore = defineStore('dashboard', {
    state: () => ({
        overview: null,
        charts: null,
        recentTransactions: [],
        period: 'month',
        loading: false,
        error: null
    }),

    getters: {
        kpiCards: (state) => {
            if (!state.overview) return []
            return [
                state.overview.total_revenue,
                state.overview.total_expense,
                state.overview.net_profit,
                state.overview.cash_on_hand
            ]
        }
    },

    actions: {
        async fetchOverview(period = 'month') {
            this.loading = true
            this.period = period

            try {
                const response = await dashboardAPI.getOverview(period)
                this.overview = response.data
            } catch (error) {
                this.error = error.response?.data?.detail || 'Gagal memuat data'
            } finally {
                this.loading = false
            }
        },

        async fetchCharts(period = 'month') {
            try {
                const response = await dashboardAPI.getCharts(period)
                this.charts = response.data
                this.recentTransactions = response.data.recent_transactions || []
            } catch (error) {
                this.error = error.response?.data?.detail || 'Gagal memuat chart'
            }
        },

        async fetchAll(period = 'month') {
            await Promise.all([
                this.fetchOverview(period),
                this.fetchCharts(period)
            ])
        }
    }
})
