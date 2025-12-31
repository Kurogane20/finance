import { defineStore } from 'pinia';
import api from '../api/axios';

export const useAccountingStore = defineStore('accounting', {
    state: () => ({
        accounts: [],
        journals: [],
        isLoading: false,
        error: null,
    }),

    getters: {
        accountsByCode: (state) => {
            const map = {};
            state.accounts.forEach(acc => map[acc.code] = acc);
            return map;
        },
        flattenedAccounts: (state) => {
            // If nested, flatten or just return list suited for Select
            return state.accounts.map(acc => ({
                value: acc.id,
                label: `${acc.code} - ${acc.name}`,
                type: acc.type
            }));
        }
    },

    actions: {
        async fetchAccounts() {
            this.isLoading = true;
            try {
                const response = await api.get('/accounting/accounts');
                this.accounts = response.data;
            } catch (err) {
                this.error = 'Failed to load accounts';
                console.error(err);
            } finally {
                this.isLoading = false;
            }
        },

        async createJournalEntry(entryData) {
            this.isLoading = true;
            try {
                const response = await api.post('/accounting/journals', entryData);
                this.journals.unshift(response.data); // Add to top
                return response.data;
            } catch (err) {
                this.error = err.response?.data?.detail || 'Failed to create journal';
                throw err;
            } finally {
                this.isLoading = false;
            }
        }
    }
});
