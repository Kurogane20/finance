<template>
  <div class="accounts-page fade-in">
    <!-- Page Header with Add Button -->
    <div class="page-header mb-lg">
      <div>
        <h1 class="page-title">Chart of Accounts</h1>
        <p class="page-subtitle">Kelola akun kas dan bank perusahaan</p>
      </div>
      <button v-if="authStore.canEdit" class="btn btn-primary" @click="openCreateModal">
        ➕ Tambah Akun
      </button>
    </div>

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
          <p class="account-type">{{ account.bank_name || accountTypeLabel(account.type) }}</p>
        </div>
        <div class="account-balance">
          <p class="balance-label">Saldo</p>
          <p class="balance-value" :class="{ 'text-danger': Number(account.balance) < 0 }">
            {{ formatCurrency(account.balance) }}
          </p>
        </div>
        <div class="account-actions" v-if="authStore.canEdit">
          <button class="btn-icon" @click="openEditModal(account)" title="Edit">✏️</button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="accounts.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">🏦</div>
        <h3>Belum ada akun</h3>
        <p>Tambahkan akun kas atau bank pertama Anda</p>
        <button v-if="authStore.canEdit" class="btn btn-primary mt-md" @click="openCreateModal">
          ➕ Tambah Akun
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>Memuat akun...</span>
    </div>

    <!-- Total Balance -->
    <div class="total-balance-card" v-if="accounts.length > 0">
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

    <!-- Create/Edit Account Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingAccount ? 'Edit Akun' : 'Tambah Akun Baru' }}</h3>
          <button class="btn btn-ghost btn-icon" @click="showModal = false">✕</button>
        </div>
        <form @submit.prevent="saveAccount" class="modal-body">
          <div class="form-group">
            <label class="form-label">Nama Akun *</label>
            <input 
              v-model="accountForm.name" 
              type="text" 
              class="form-input" 
              placeholder="Contoh: Bank BCA Operasional"
              required
            >
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Tipe Akun *</label>
              <select v-model="accountForm.type" class="form-input form-select" required>
                <option value="bank">🏦 Bank</option>
                <option value="cash">💵 Kas</option>
                <option value="credit_card">💳 Kartu Kredit</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Mata Uang</label>
              <select v-model="accountForm.currency" class="form-input form-select">
                <option value="IDR">IDR - Rupiah</option>
                <option value="USD">USD - Dollar</option>
                <option value="EUR">EUR - Euro</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nama Bank</label>
              <input 
                v-model="accountForm.bank_name" 
                type="text" 
                class="form-input" 
                placeholder="Contoh: Bank Central Asia"
              >
            </div>
            <div class="form-group">
              <label class="form-label">Nomor Rekening</label>
              <input 
                v-model="accountForm.account_number" 
                type="text" 
                class="form-input" 
                placeholder="Contoh: 1234567890"
              >
            </div>
          </div>
          <div class="form-group" v-if="!editingAccount">
            <label class="form-label">Saldo Awal (Rp)</label>
            <input 
              v-model.number="accountForm.balance" 
              type="number" 
              class="form-input" 
              placeholder="0"
              min="0"
            >
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showModal = false">Batal</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Menyimpan...' : (editingAccount ? 'Update' : 'Simpan') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      <span>{{ toast.message }}</span>
      <button @click="toast.show = false">✕</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { accountsAPI } from '@/api'

const authStore = useAuthStore()

const accounts = ref([])
const agingReceivable = ref({ aging: {}, total_outstanding: 0, total_invoices: 0 })
const agingPayable = ref({ aging: {}, total_outstanding: 0, total_invoices: 0 })
const loading = ref(true)
const showModal = ref(false)
const saving = ref(false)
const editingAccount = ref(null)

const toast = reactive({
  show: false,
  message: '',
  type: 'success'
})

const accountForm = reactive({
  name: '',
  type: 'bank',
  account_number: '',
  bank_name: '',
  currency: 'IDR',
  balance: 0
})

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

const accountTypeLabel = (type) => {
  const labels = {
    bank: 'Rekening Bank',
    cash: 'Kas Tunai',
    credit_card: 'Kartu Kredit'
  }
  return labels[type] || type
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

const showToast = (message, type = 'success') => {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

const openCreateModal = () => {
  editingAccount.value = null
  Object.assign(accountForm, {
    name: '',
    type: 'bank',
    account_number: '',
    bank_name: '',
    currency: 'IDR',
    balance: 0
  })
  showModal.value = true
}

const openEditModal = (account) => {
  editingAccount.value = account
  Object.assign(accountForm, {
    name: account.name,
    type: account.type,
    account_number: account.account_number || '',
    bank_name: account.bank_name || '',
    currency: account.currency || 'IDR',
    balance: Number(account.balance)
  })
  showModal.value = true
}

const saveAccount = async () => {
  saving.value = true
  try {
    if (editingAccount.value) {
      // Update existing account
      await accountsAPI.update(editingAccount.value.id, {
        name: accountForm.name,
        type: accountForm.type,
        account_number: accountForm.account_number,
        bank_name: accountForm.bank_name
      })
      showToast('Akun berhasil diupdate')
    } else {
      // Create new account
      await accountsAPI.create({
        name: accountForm.name,
        type: accountForm.type,
        account_number: accountForm.account_number,
        bank_name: accountForm.bank_name,
        currency: accountForm.currency,
        balance: accountForm.balance
      })
      showToast('Akun berhasil ditambahkan')
    }
    showModal.value = false
    await fetchAccounts()
  } catch (error) {
    showToast(error.response?.data?.detail || 'Gagal menyimpan akun', 'error')
  } finally {
    saving.value = false
  }
}

const fetchAccounts = async () => {
  loading.value = true
  try {
    const response = await accountsAPI.getAll()
    accounts.value = response.data
  } catch (error) {
    showToast('Gagal memuat akun', 'error')
  } finally {
    loading.value = false
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
    // Aging is not critical, don't show error toast
  }
}

onMounted(() => {
  fetchAccounts()
  fetchAging()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.accounts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
  border: 1px solid var(--border-color);
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
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
}

.account-info {
  flex: 1;
}

.account-name {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: var(--spacing-xs);
  color: var(--text-primary);
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

.account-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.btn-icon {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.btn-icon:hover {
  background: var(--bg-tertiary);
}

.total-balance-card {
  background: var(--gradient-primary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  text-align: center;
  color: white;
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

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--spacing-xl) * 2;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 2px dashed var(--border-color);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
}

.empty-state h3 {
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.empty-state p {
  color: var(--text-secondary);
}

/* Loading State */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  padding: var(--spacing-xl);
  color: var(--text-secondary);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Form Row */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
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
  color: var(--text-primary);
}

.aging-total {
  display: flex;
  justify-content: space-between;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-color);
  font-size: 0.95rem;
  color: var(--text-primary);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-body {
  padding: var(--spacing-lg);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  padding-top: var(--spacing-lg);
}

.form-group {
  margin-bottom: var(--spacing-md);
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  color: white;
  font-weight: 500;
  z-index: 2000;
  animation: slideIn 0.3s ease;
  box-shadow: var(--shadow-lg);
}

.toast.success {
  background: var(--color-success);
}

.toast.error {
  background: var(--color-danger);
}

.toast button {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  opacity: 0.8;
}

.toast button:hover {
  opacity: 1;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Grid Layout */
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
}

.mb-lg {
  margin-bottom: var(--spacing-lg);
}

.mt-lg {
  margin-top: var(--spacing-lg);
}

.mt-md {
  margin-top: var(--spacing-md);
}

/* Responsive */
@media (max-width: 768px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
