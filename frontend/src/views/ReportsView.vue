<template>
  <div class="reports-page fade-in">
    <div class="reports-grid">
      <!-- Profit & Loss -->
      <div class="report-card">
        <div class="report-header">
          <h3>📊 Laporan Laba Rugi</h3>
          <p>Profit & Loss Statement</p>
        </div>
        <div class="report-filters">
          <input v-model="pnlStartDate" type="date" class="form-input">
          <span>s/d</span>
          <input v-model="pnlEndDate" type="date" class="form-input">
        </div>
        <button class="btn btn-primary w-full" @click="fetchPnL">Generate Report</button>
        <div v-if="pnlReport" class="report-result">
          <div class="report-section">
            <h4>Pendapatan</h4>
            <div v-for="item in pnlReport.income.items" :key="item.category" class="report-line">
              <span>{{ item.category }}</span>
              <span>{{ formatCurrency(item.amount) }}</span>
            </div>
            <div class="report-subtotal">
              <span>Total Pendapatan</span>
              <span class="text-success">{{ formatCurrency(pnlReport.income.total) }}</span>
            </div>
          </div>
          <div class="report-section">
            <h4>Pengeluaran</h4>
            <div v-for="item in pnlReport.expenses.items" :key="item.category" class="report-line">
              <span>{{ item.category }}</span>
              <span>{{ formatCurrency(item.amount) }}</span>
            </div>
            <div class="report-subtotal">
              <span>Total Pengeluaran</span>
              <span class="text-danger">{{ formatCurrency(pnlReport.expenses.total) }}</span>
            </div>
          </div>
          <div class="report-total">
            <span>Laba Bersih</span>
            <span :class="pnlReport.net_profit >= 0 ? 'text-success' : 'text-danger'">
              {{ formatCurrency(pnlReport.net_profit) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Cash Flow -->
      <div class="report-card">
        <div class="report-header">
          <h3>💸 Laporan Arus Kas</h3>
          <p>Cash Flow Statement</p>
        </div>
        <div class="report-filters">
          <select v-model="cfMonth" class="form-input form-select">
            <option v-for="m in 12" :key="m" :value="m">{{ monthName(m) }}</option>
          </select>
          <select v-model="cfYear" class="form-input form-select">
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <button class="btn btn-primary w-full" @click="fetchCashFlow">Generate Report</button>
        <div v-if="cashFlowReport" class="report-result">
          <div class="cf-summary">
            <div class="cf-item green">
              <span>Total Masuk</span>
              <strong>{{ formatCurrency(cashFlowReport.inflows.total) }}</strong>
            </div>
            <div class="cf-item red">
              <span>Total Keluar</span>
              <strong>{{ formatCurrency(cashFlowReport.outflows.total) }}</strong>
            </div>
            <div class="cf-item purple">
              <span>Arus Kas Bersih</span>
              <strong>{{ formatCurrency(cashFlowReport.net_cash_flow) }}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Balance Sheet -->
      <div class="report-card">
        <div class="report-header">
          <h3>📋 Neraca</h3>
          <p>Balance Sheet</p>
        </div>
        <div class="report-filters">
          <input v-model="bsDate" type="date" class="form-input w-full">
        </div>
        <button class="btn btn-primary w-full" @click="fetchBalanceSheet">Generate Report</button>
        <div v-if="balanceSheet" class="report-result">
          <div class="bs-section">
            <h4>Aset</h4>
            <p>Total: <strong class="text-success">{{ formatCurrency(balanceSheet.assets.total) }}</strong></p>
          </div>
          <div class="bs-section">
            <h4>Liabilitas</h4>
            <p>Total: <strong class="text-danger">{{ formatCurrency(balanceSheet.liabilities.total) }}</strong></p>
          </div>
          <div class="bs-section">
            <h4>Ekuitas</h4>
            <p>Total: <strong>{{ formatCurrency(balanceSheet.equity) }}</strong></p>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Section -->
    <div class="card mt-lg">
      <h3 class="card-title mb-md">📥 Export Data</h3>
      <div class="export-row">
        <div class="export-info">
          <p><strong>Export Transaksi ke CSV</strong></p>
          <p class="text-muted">Download semua transaksi dalam format CSV</p>
        </div>
        <button class="btn btn-secondary" @click="exportTransactions">Download CSV</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { reportsAPI } from '@/api'

const today = new Date()
const pnlStartDate = ref(new Date(today.getFullYear(), 0, 1).toISOString().slice(0, 10))
const pnlEndDate = ref(today.toISOString().slice(0, 10))
const cfMonth = ref(today.getMonth() + 1)
const cfYear = ref(today.getFullYear())
const bsDate = ref(today.toISOString().slice(0, 10))
const years = [2024, 2025]

const pnlReport = ref(null)
const cashFlowReport = ref(null)
const balanceSheet = ref(null)

const monthName = (m) => new Date(2024, m - 1).toLocaleDateString('id-ID', { month: 'long' })
const formatCurrency = (v) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v || 0)

const fetchPnL = async () => { pnlReport.value = (await reportsAPI.getProfitLoss(pnlStartDate.value, pnlEndDate.value)).data }
const fetchCashFlow = async () => { cashFlowReport.value = (await reportsAPI.getCashFlow(cfYear.value, cfMonth.value)).data }
const fetchBalanceSheet = async () => { balanceSheet.value = (await reportsAPI.getBalanceSheet(bsDate.value)).data }
const exportTransactions = async () => {
  const blob = (await reportsAPI.exportTransactions()).data
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `transactions_${today.toISOString().slice(0, 10)}.csv`
  a.click()
}
</script>

<style scoped>
.reports-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; }
.report-card { background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: 1rem; padding: 1.5rem; }
.report-header { margin-bottom: 1rem; }
.report-header h3 { font-size: 1.1rem; margin-bottom: 0.25rem; }
.report-header p { font-size: 0.85rem; color: var(--text-secondary); }
.report-filters { display: flex; gap: 0.5rem; align-items: center; margin-bottom: 1rem; }
.report-filters .form-input { flex: 1; }
.report-result { margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--glass-border); }
.report-section { margin-bottom: 1rem; }
.report-section h4 { font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem; }
.report-line { display: flex; justify-content: space-between; padding: 0.25rem 0; font-size: 0.9rem; }
.report-subtotal, .report-total { display: flex; justify-content: space-between; padding: 0.5rem 0; border-top: 1px solid var(--glass-border); font-weight: 600; }
.report-total { font-size: 1.1rem; margin-top: 0.5rem; }
.cf-summary { display: flex; flex-direction: column; gap: 0.75rem; }
.cf-item { display: flex; justify-content: space-between; padding: 0.75rem; border-radius: 0.5rem; }
.cf-item.green { background: var(--color-success-light); }
.cf-item.red { background: var(--color-danger-light); }
.cf-item.purple { background: rgba(139, 92, 246, 0.15); }
.bs-section { margin-bottom: 1rem; }
.bs-section h4 { font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.25rem; }
.export-row { display: flex; justify-content: space-between; align-items: center; }
.export-info p { margin: 0; }
</style>
