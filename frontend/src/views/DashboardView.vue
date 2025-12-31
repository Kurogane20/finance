<template>
  <div class="dashboard fade-in">
    <!-- Period Filter -->
    <div class="dashboard-filters">
      <div class="filter-group">
        <button
          v-for="p in periods"
          :key="p.value"
          class="chart-filter-btn"
          :class="{ active: period === p.value }"
          @click="changePeriod(p.value)"
        >
          {{ p.label }}
        </button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <KPICard
        v-for="kpi in dashboardStore.kpiCards"
        :key="kpi.title"
        :title="kpi.title"
        :value="kpi.value"
        :change-percent="kpi.change_percent"
        :change-type="kpi.change_type"
        :icon="kpi.icon"
        :color="kpi.color"
      />
    </div>

    <!-- Quick Stats -->
    <div class="quick-stats" v-if="dashboardStore.overview">
      <div class="stat-item warning">
        <span class="stat-icon">⏳</span>
        <span class="stat-value">{{ dashboardStore.overview.pending_invoices }}</span>
        <span class="stat-label">Invoice Pending</span>
      </div>
      <div class="stat-item danger">
        <span class="stat-icon">⚠️</span>
        <span class="stat-value">{{ dashboardStore.overview.overdue_invoices }}</span>
        <span class="stat-label">Invoice Overdue</span>
      </div>
    </div>

    <!-- Main Content Grid: Analytics + Charts -->
    <div class="dashboard-main-grid">
      <!-- Left Column: Analytics Insights -->
      <div class="analytics-column">
        <AnalyticsInsights ref="analyticsRef" />
      </div>
      
      <!-- Right Column: Charts -->
      <div class="charts-column">
        <!-- Revenue vs Expense Chart -->
        <ChartCard 
          title="Pendapatan vs Pengeluaran"
          class="chart-card-full"
        >
          <Line 
            v-if="revenueExpenseData"
            :data="revenueExpenseData" 
            :options="lineChartOptions" 
          />
        </ChartCard>

        <!-- Category Charts Row -->
        <div class="category-charts-row">
          <!-- Expense by Category -->
          <ChartCard title="Pengeluaran per Kategori">
            <Doughnut 
              v-if="expenseCategoryData"
              :data="expenseCategoryData" 
              :options="doughnutOptions" 
            />
          </ChartCard>

          <!-- Income by Category -->
          <ChartCard title="Pendapatan per Kategori">
            <Doughnut 
              v-if="incomeCategoryData"
              :data="incomeCategoryData" 
              :options="doughnutOptions" 
            />
          </ChartCard>
        </div>
      </div>
    </div>

    <!-- Recent Transactions -->
    <div class="card mt-lg">
      <div class="card-header">
        <h3 class="card-title">Transaksi Terbaru</h3>
        <router-link to="/transactions" class="btn btn-ghost">
          Lihat Semua →
        </router-link>
      </div>
      <DataTable :columns="transactionColumns" :data="dashboardStore.recentTransactions">
        <template #type="{ value }">
          <span :class="value === 'credit' ? 'text-success' : 'text-danger'">
            {{ value === 'credit' ? '↑ Masuk' : '↓ Keluar' }}
          </span>
        </template>
        <template #amount="{ row }">
          <span :class="row.type === 'credit' ? 'text-success' : 'text-danger'">
            {{ formatCurrency(row.amount) }}
          </span>
        </template>
        <template #status="{ value }">
          <span class="badge" :class="statusClass(value)">{{ value }}</span>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import KPICard from '@/components/common/KPICard.vue'
import ChartCard from '@/components/common/ChartCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import AnalyticsInsights from '@/components/common/AnalyticsInsights.vue'
import { Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const dashboardStore = useDashboardStore()
const analyticsRef = ref(null)

const period = ref('month')
const periods = [
  { label: 'Minggu', value: 'week' },
  { label: 'Bulan', value: 'month' },
  { label: 'Kuartal', value: 'quarter' },
  { label: 'Tahun', value: 'year' }
]

const transactionColumns = [
  { key: 'date', label: 'Tanggal', type: 'date' },
  { key: 'description', label: 'Deskripsi' },
  { key: 'category', label: 'Kategori' },
  { key: 'type', label: 'Tipe' },
  { key: 'amount', label: 'Jumlah', type: 'currency' },
  { key: 'status', label: 'Status' }
]

const changePeriod = async (newPeriod) => {
  period.value = newPeriod
  await dashboardStore.fetchAll(newPeriod)
}

// Chart data
const revenueExpenseData = computed(() => {
  if (!dashboardStore.charts?.revenue_expense) return null
  const data = dashboardStore.charts.revenue_expense
  return {
    labels: data.labels,
    datasets: [
      {
        label: 'Pendapatan',
        data: data.revenue.map(v => Number(v)),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Pengeluaran',
        data: data.expense.map(v => Number(v)),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }
})

const expenseCategoryData = computed(() => {
  if (!dashboardStore.charts?.expense_by_category?.length) return null
  const data = dashboardStore.charts.expense_by_category
  return {
    labels: data.map(c => c.category),
    datasets: [{
      data: data.map(c => Number(c.amount)),
      backgroundColor: data.map(c => c.color),
      borderWidth: 0
    }]
  }
})

const incomeCategoryData = computed(() => {
  if (!dashboardStore.charts?.income_by_category?.length) return null
  const data = dashboardStore.charts.income_by_category
  return {
    labels: data.map(c => c.category),
    datasets: [{
      data: data.map(c => Number(c.amount)),
      backgroundColor: data.map(c => c.color),
      borderWidth: 0
    }]
  }
})

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: { color: '#a1a1aa' }
    }
  },
  scales: {
    x: {
      grid: { color: 'rgba(255,255,255,0.05)' },
      ticks: { color: '#71717a' }
    },
    y: {
      grid: { color: 'rgba(255,255,255,0.05)' },
      ticks: { 
        color: '#71717a',
        callback: (value) => formatCompact(value)
      }
    }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#a1a1aa', padding: 15 }
    }
  },
  cutout: '60%'
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(value)
}

const formatCompact = (value) => {
  if (value >= 1000000000) return (value / 1000000000).toFixed(1) + 'M'
  if (value >= 1000000) return (value / 1000000).toFixed(1) + 'Jt'
  if (value >= 1000) return (value / 1000).toFixed(0) + 'Rb'
  return value
}

const statusClass = (status) => {
  const classes = {
    completed: 'badge-success',
    pending: 'badge-warning',
    cancelled: 'badge-danger'
  }
  return classes[status] || 'badge-neutral'
}

onMounted(() => {
  dashboardStore.fetchAll(period.value)
})
</script>

<style scoped>
/* Animations */
.fade-in {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}

/* Filter Buttons */
.chart-filter-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.8rem;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.chart-filter-btn:hover {
  color: var(--text-primary);
  background: rgba(0, 0, 0, 0.05);
}

.chart-filter-btn.active {
  background: var(--primary-color);
  color: white;
}

.dashboard-filters {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--spacing-lg);
}

.filter-group {
  display: flex;
  gap: var(--spacing-sm);
  background: var(--bg-card);
  padding: var(--spacing-xs);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.quick-stats {
  display: flex;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
}

.stat-item.warning { border-left: 3px solid var(--color-warning); }
.stat-item.danger { border-left: 3px solid var(--color-danger); }

.stat-icon { font-size: 1.5rem; }
.stat-value { font-size: 1.25rem; font-weight: 700; }
.stat-label { color: var(--text-secondary); font-size: 0.875rem; }

/* Main Dashboard Grid */
.dashboard-main-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

.analytics-column {
  display: flex;
  flex-direction: column;
}

.charts-column {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.chart-card-full {
  flex: 1;
}

.category-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

/* Legacy charts-grid for compatibility */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.chart-wide {
  grid-column: span 1;
}

/* Responsive Design */
@media (max-width: 1400px) {
  .dashboard-main-grid {
    grid-template-columns: 1fr 1.2fr;
  }
}

@media (max-width: 1200px) {
  .dashboard-main-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-column {
    order: 2;
  }
  
  .charts-column {
    order: 1;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-wide {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .quick-stats {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .category-charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
