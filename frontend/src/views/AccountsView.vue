<template>
  <div class="accounts-page fade-in">
    <!-- Accounts Summary -->
    <div class="accounts-grid">
      <div 
        v-for="account in accounts" 
        :key="account.id"
        class="account-card"
        :class="{ 'negative': Number(account.balance) < 0 }"
      >
        <div class="account-icon">
          {{ accountIcon(account.type) }}
        </div>
        <div class="account-info">
          <p class="account-name">{{ account.name }}</p>
          <p class="account-type">{{ account.bank_name || account.type }}</p>
        </div>
        <div class="account-balance">
          <p class="balance-label">Saldo</p>
          <p class="balance-value" :class="{ 'text-danger': Number(account.balance) < 0 }">
            {{ formatCurrency(account.balance) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Total Balance -->
    <div class="total-balance-card">
      <div class="total-balance-content">
        <p class="total-label">Total Saldo Keseluruhan</p>
        <p class="total-value">{{ formatCurrency(totalBalance) }}</p>
      </div>
    </div>

    <!-- AR/AP Section -->
    <div class="grid-2 mt-lg">
      <!-- Aging Receivable -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">📥 Aging Piutang (AR)</h3>
          <span class="badge badge-info">{{ agingReceivable.total_invoices }} Invoice</span>
        </div>
        <div class="aging-chart">
          <div 
            v-for="(data, key) in agingReceivable.aging" 
            :key="key"
            class="aging-bar"
          >
            <div class="aging-label">{{ agingLabels[key] }}</div>
            <div class="aging-bar-container">
              <div 
                class="aging-bar-fill"
                :class="agingColorClass(key)"
                :style="{ width: agingPercentage(data.amount, agingReceivable.total_outstanding) + '%' }"
              ></div>
            </div>
            <div class="aging-amount">{{ formatCurrency(data.amount) }}</div>
          </div>
        </div>
        <div class="aging-total">
          <span>Total Outstanding:</span>
          <strong>{{ formatCurrency(agingReceivable.total_outstanding) }}</strong>
        </div>
      </div>

      <!-- Aging Payable -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">📤 Aging Hutang (AP)</h3>
          <span class="badge badge-warning">{{ agingPayable.total_invoices }} Invoice</span>
        </div>
        <div class="aging-chart">
          <div 
            v-for="(data, key) in agingPayable.aging" 
            :key="key"
            class="aging-bar"
          >
            <div class="aging-label">{{ agingLabels[key] }}</div>
            <div class="aging-bar-container">
              <div 
                class="aging-bar-fill"
                :class="agingColorClass(key)"
                :style="{ width: agingPercentage(data.amount, agingPayable.total_outstanding) + '%' }"
              ></div>
            </div>
            <div class="aging-amount">{{ formatCurrency(data.amount) }}</div>
          </div>
        </div>
        <div class="aging-total">
          <span>Total Outstanding:</span>
          <strong>{{ formatCurrency(agingPayable.total_outstanding) }}</strong>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { accountsAPI } from '@/api'

const accounts = ref([])
const agingReceivable = ref({ aging: {}, total_outstanding: 0, total_invoices: 0 })
const agingPayable = ref({ aging: {}, total_outstanding: 0, total_invoices: 0 })

const agingLabels = {
  current: 'Belum Jatuh Tempo',
  '1_30': '1-30 hari',
  '31_60': '31-60 hari',
  '61_90': '61-90 hari',
  over_90: '> 90 hari'
}

const totalBalance = computed(() => {
  return accounts.value.reduce((sum, acc) => sum + Number(acc.balance), 0)
})

const accountIcon = (type) => {
  const icons = {
    bank: '🏦',
    cash: '💵',
    credit_card: '💳'
  }
  return icons[type] || '💰'
}

const agingColorClass = (key) => {
  const colors = {
    current: 'green',
    '1_30': 'yellow',
    '31_60': 'orange',
    '61_90': 'red',
    over_90: 'dark-red'
  }
  return colors[key]
}

const agingPercentage = (amount, total) => {
  if (!total || total === 0) return 0
  return Math.min(100, (amount / total) * 100)
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(value || 0)
}

const fetchAccounts = async () => {
  try {
    const response = await accountsAPI.getAll()
    accounts.value = response.data
  } catch (error) {
    console.error('Error fetching accounts:', error)
  }
}

const fetchAging = async () => {
  try {
    const [receivable, payable] = await Promise.all([
      accountsAPI.getAging('receivable'),
      accountsAPI.getAging('payable')
    ])
    agingReceivable.value = receivable.data
    agingPayable.value = payable.data
  } catch (error) {
    console.error('Error fetching aging:', error)
  }
}

onMounted(() => {
  fetchAccounts()
  fetchAging()
})
</script>

<style scoped>
.accounts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.account-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--glass-border);
  transition: all var(--transition-normal);
}

.account-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.account-card.negative {
  border-left: 3px solid var(--color-danger);
}

.account-icon {
  font-size: 2rem;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border-radius: var(--radius-lg);
}

.account-info {
  flex: 1;
}

.account-name {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: var(--spacing-xs);
}

.account-type {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.account-balance {
  text-align: right;
}

.balance-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: var(--spacing-xs);
}

.balance-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-success);
}

.total-balance-card {
  background: var(--gradient-primary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  text-align: center;
}

.total-label {
  font-size: 1rem;
  opacity: 0.9;
  margin-bottom: var(--spacing-sm);
}

.total-value {
  font-size: 2.5rem;
  font-weight: 800;
}

/* Aging Chart */
.aging-chart {
  margin: var(--spacing-lg) 0;
}

.aging-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.aging-label {
  width: 130px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.aging-bar-container {
  flex: 1;
  height: 24px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.aging-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.5s ease;
}

.aging-bar-fill.green { background: var(--color-success); }
.aging-bar-fill.yellow { background: #eab308; }
.aging-bar-fill.orange { background: #f97316; }
.aging-bar-fill.red { background: var(--color-danger); }
.aging-bar-fill.dark-red { background: #991b1b; }

.aging-amount {
  width: 120px;
  text-align: right;
  font-size: 0.9rem;
  font-weight: 600;
}

.aging-total {
  display: flex;
  justify-content: space-between;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--glass-border);
  font-size: 0.95rem;
}
</style>
