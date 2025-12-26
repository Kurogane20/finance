<template>
  <div class="budgets-page fade-in">
    <div class="period-selector">
      <button class="btn btn-ghost" @click="changeMonth(-1)">← Sebelumnya</button>
      <h2 class="period-title">{{ formattedPeriod }}</h2>
      <button class="btn btn-ghost" @click="changeMonth(1)">Berikutnya →</button>
    </div>

    <div class="budget-summary">
      <div class="summary-item">
        <p class="summary-label">Total Dianggarkan</p>
        <p class="summary-value">{{ formatCurrency(summary.total_allocated) }}</p>
      </div>
      <div class="summary-item">
        <p class="summary-label">Total Terpakai</p>
        <p class="summary-value text-warning">{{ formatCurrency(summary.total_spent) }}</p>
      </div>
      <div class="summary-item">
        <p class="summary-label">Sisa Anggaran</p>
        <p class="summary-value text-success">{{ formatCurrency(summary.total_remaining) }}</p>
      </div>
      <div class="summary-item">
        <p class="summary-label">Penggunaan</p>
        <p class="summary-value">{{ summary.overall_percentage }}%</p>
      </div>
    </div>

    <div class="budget-grid">
      <div v-for="budget in budgets" :key="budget.id" class="budget-card" :class="budget.status">
        <div class="budget-header">
          <h3 class="budget-dept">{{ budget.department }}</h3>
          <span class="badge" :class="statusBadge(budget.status)">{{ statusLabel(budget.status) }}</span>
        </div>
        <div class="budget-progress">
          <div class="progress-bar">
            <div class="progress-fill" :class="budget.status" :style="{ width: Math.min(budget.percentage, 100) + '%' }"></div>
          </div>
          <span>{{ budget.percentage }}%</span>
        </div>
        <div class="budget-details">
          <div><span class="detail-label">Anggaran:</span> {{ formatCurrency(budget.allocated) }}</div>
          <div><span class="detail-label">Terpakai:</span> {{ formatCurrency(budget.spent) }}</div>
          <div><span class="detail-label">Sisa:</span> {{ formatCurrency(budget.remaining) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { budgetsAPI } from '@/api'

const currentPeriod = ref(new Date().toISOString().slice(0, 7))
const budgets = ref([])
const summary = ref({ total_allocated: 0, total_spent: 0, total_remaining: 0, overall_percentage: 0 })

const formattedPeriod = computed(() => {
  const [year, month] = currentPeriod.value.split('-')
  return new Date(year, month - 1).toLocaleDateString('id-ID', { year: 'numeric', month: 'long' })
})

const changeMonth = (delta) => {
  const [year, month] = currentPeriod.value.split('-').map(Number)
  const date = new Date(year, month - 1 + delta)
  currentPeriod.value = date.toISOString().slice(0, 7)
  fetchComparison()
}

const statusBadge = (s) => ({ on_track: 'badge-success', warning: 'badge-warning', over_budget: 'badge-danger' }[s] || 'badge-neutral')
const statusLabel = (s) => ({ on_track: 'On Track', warning: 'Warning', over_budget: 'Over Budget' }[s] || s)
const formatCurrency = (v) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(v || 0)

const fetchComparison = async () => {
  const { data } = await budgetsAPI.getComparison(currentPeriod.value)
  budgets.value = data.budgets
  summary.value = data.summary
}

onMounted(fetchComparison)
</script>

<style scoped>
.period-selector { display: flex; align-items: center; justify-content: center; gap: 2rem; margin-bottom: 2rem; }
.period-title { font-size: 1.5rem; font-weight: 700; }
.budget-summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; padding: 1.5rem; background: var(--bg-card); border-radius: 1rem; border: 1px solid var(--glass-border); }
.summary-item { text-align: center; }
.summary-label { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem; }
.summary-value { font-size: 1.5rem; font-weight: 700; }
.budget-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }
.budget-card { padding: 1.5rem; background: var(--bg-card); border-radius: 1rem; border: 1px solid var(--glass-border); }
.budget-card.over_budget { border-left: 4px solid var(--color-danger); }
.budget-card.warning { border-left: 4px solid var(--color-warning); }
.budget-card.on_track { border-left: 4px solid var(--color-success); }
.budget-header { display: flex; justify-content: space-between; margin-bottom: 1rem; }
.budget-dept { font-size: 1.1rem; font-weight: 600; }
.budget-progress { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
.progress-bar { flex: 1; height: 8px; background: var(--bg-tertiary); border-radius: 9999px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 9999px; }
.progress-fill.on_track { background: var(--color-success); }
.progress-fill.warning { background: var(--color-warning); }
.progress-fill.over_budget { background: var(--color-danger); }
.budget-details { display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.9rem; }
.detail-label { color: var(--text-muted); }
</style>
