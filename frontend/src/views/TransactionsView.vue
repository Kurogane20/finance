<template>
  <div class="transactions-page fade-in">
    <!-- Summary Cards -->
    <div class="summary-cards">
      <div class="summary-card green">
        <span class="summary-icon">↑</span>
        <div class="summary-content">
          <p class="summary-label">Total Masuk</p>
          <p class="summary-value">{{ formatCurrency(summary.total_credit) }}</p>
        </div>
      </div>
      <div class="summary-card red">
        <span class="summary-icon">↓</span>
        <div class="summary-content">
          <p class="summary-label">Total Keluar</p>
          <p class="summary-value">{{ formatCurrency(summary.total_debit) }}</p>
        </div>
      </div>
      <div class="summary-card purple">
        <span class="summary-icon">≈</span>
        <div class="summary-content">
          <p class="summary-label">Saldo Bersih</p>
          <p class="summary-value">{{ formatCurrency(summary.net) }}</p>
        </div>
      </div>
      <div class="summary-card blue">
        <span class="summary-icon">⏳</span>
        <div class="summary-content">
          <p class="summary-label">Pending</p>
          <p class="summary-value">{{ summary.pending_count }}</p>
        </div>
      </div>
    </div>

    <!-- Filters & Actions -->
    <div class="filters-bar">
      <div class="filters">
        <select v-model="filters.type" class="form-input form-select" @change="fetchTransactions">
          <option value="">Semua Tipe</option>
          <option value="credit">Masuk</option>
          <option value="debit">Keluar</option>
        </select>
        <select v-model="filters.status" class="form-input form-select" @change="fetchTransactions">
          <option value="">Semua Status</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select v-model="filters.category_id" class="form-input form-select" @change="fetchTransactions">
          <option value="">Semua Kategori</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.icon }} {{ cat.name }}
          </option>
        </select>
      </div>
      <button v-if="authStore.canEdit" class="btn btn-secondary mr-2" @click="showImportModal = true">
        📂 Import CSV
      </button>
      <button v-if="authStore.canEdit" class="btn btn-primary" @click="showModal = true">
        ➕ Tambah Transaksi
      </button>
    </div>

    <!-- Transactions Table -->
    <div class="card">
      <DataTable :columns="columns" :data="transactions">
        <template #type="{ value }">
          <span :class="value === 'credit' ? 'text-success' : 'text-danger'">
            {{ value === 'credit' ? '↑ Masuk' : '↓ Keluar' }}
          </span>
        </template>
        <template #amount="{ row }">
          <span :class="row.type === 'credit' ? 'text-success' : 'text-danger'" style="font-weight: 600;">
            {{ formatCurrency(row.amount) }}
          </span>
        </template>
        <template #category="{ row }">
          <span v-if="row.category">
            {{ row.category.icon }} {{ row.category.name }}
          </span>
          <span v-else class="text-muted">-</span>
        </template>
        <template #status="{ value }">
          <span class="badge" :class="statusClass(value)">{{ value }}</span>
        </template>
      </DataTable>
    </div>

    <!-- Add Transaction Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Tambah Transaksi</h3>
          <button class="btn btn-ghost btn-icon" @click="showModal = false">✕</button>
        </div>
        <form @submit.prevent="createTransaction" class="modal-body">
          <div class="form-group">
            <label class="form-label">Tipe</label>
            <select v-model="newTransaction.type" class="form-input form-select" required>
              <option value="credit">Masuk (Credit)</option>
              <option value="debit">Keluar (Debit)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Jumlah (Rp)</label>
            <input v-model.number="newTransaction.amount" type="number" class="form-input" required min="1">
          </div>
          <div class="form-group">
            <label class="form-label">Kategori</label>
            <select v-model="newTransaction.category_id" class="form-input form-select">
              <option :value="null">Pilih Kategori</option>
              <option v-for="cat in filteredCategories" :key="cat.id" :value="cat.id">
                {{ cat.icon }} {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Akun</label>
            <select v-model="newTransaction.account_id" class="form-input form-select" required>
              <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                {{ acc.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Deskripsi</label>
            <input v-model="newTransaction.description" type="text" class="form-input" placeholder="Deskripsi transaksi">
          </div>
          <div class="form-group">
            <label class="form-label">Referensi</label>
            <input v-model="newTransaction.reference" type="text" class="form-input" placeholder="No. Invoice/Bukti">
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showModal = false">Batal</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Menyimpan...' : 'Simpan' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Import Modal -->
    <div v-if="showImportModal" class="modal-overlay" @click.self="showImportModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Import Transaksi (CSV)</h3>
          <button class="btn btn-ghost btn-icon" @click="showImportModal = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="text-sm text-secondary mb-4">
            Upload file CSV dengan kolom: Date, Description, Amount, Type (credit/debit), Account.
          </p>
          <div class="form-group">
            <input type="file" ref="fileInput" accept=".csv" class="form-input" @change="handleFileSelect">
          </div>
          <div v-if="importResult" class="mt-4 p-4 rounded bg-neutral">
            <p v-if="importResult.message" class="text-success font-bold">{{ importResult.message }}</p>
            <ul v-if="importResult.errors && importResult.errors.length > 0" class="mt-2 text-sm text-danger list-disc pl-4">
              <li v-for="(err, i) in importResult.errors" :key="i">{{ err }}</li>
            </ul>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showImportModal = false">Tutup</button>
          <button class="btn btn-primary" :disabled="!selectedFile || importing" @click="uploadImport">
            {{ importing ? 'Mengupload...' : 'Upload' }}
          </button>
        </div>
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
import { transactionsAPI, accountsAPI } from '@/api'
import DataTable from '@/components/common/DataTable.vue'

const authStore = useAuthStore()

const transactions = ref([])
const categories = ref([])
const accounts = ref([])
const summary = ref({ total_credit: 0, total_debit: 0, net: 0, pending_count: 0 })
const showModal = ref(false)
const showImportModal = ref(false)
const saving = ref(false)
const importing = ref(false)
const selectedFile = ref(null)
const importResult = ref(null)
const fileInput = ref(null)

const toast = reactive({
  show: false,
  message: '',
  type: 'success'
})

const showToast = (message, type = 'success') => {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

const filters = reactive({
  type: '',
  status: '',
  category_id: ''
})

const newTransaction = reactive({
  type: 'debit',
  amount: null,
  category_id: null,
  account_id: null,
  description: '',
  reference: '',
  date: new Date().toISOString(),
  status: 'completed'
})

const columns = [
  { key: 'date', label: 'Tanggal', type: 'date' },
  { key: 'description', label: 'Deskripsi' },
  { key: 'category', label: 'Kategori' },
  { key: 'type', label: 'Tipe' },
  { key: 'amount', label: 'Jumlah' },
  { key: 'reference', label: 'Referensi' },
  { key: 'status', label: 'Status' }
]

const filteredCategories = computed(() => {
  const type = newTransaction.type === 'credit' ? 'income' : 'expense'
  return categories.value.filter(c => c.type === type)
})

const fetchTransactions = async () => {
  try {
    const params = {}
    if (filters.type) params.type = filters.type
    if (filters.status) params.status = filters.status
    if (filters.category_id) params.category_id = filters.category_id
    
    const response = await transactionsAPI.getAll(params)
    transactions.value = response.data
  } catch (error) {
    console.error('Error fetching transactions:', error)
  }
}

const fetchSummary = async () => {
  try {
    const response = await transactionsAPI.getSummary()
    summary.value = response.data
  } catch (error) {
    console.error('Error fetching summary:', error)
  }
}

const fetchCategories = async () => {
  try {
    const response = await transactionsAPI.getCategories()
    categories.value = response.data
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

const fetchAccounts = async () => {
  try {
    const response = await accountsAPI.getAll()
    accounts.value = response.data
    if (accounts.value.length > 0) {
      newTransaction.account_id = accounts.value[0].id
    }
  } catch (error) {
    console.error('Error fetching accounts:', error)
  }
}

const createTransaction = async () => {
  saving.value = true
  try {
    await transactionsAPI.create(newTransaction)
    showModal.value = false
    await Promise.all([fetchTransactions(), fetchSummary()])
    showToast('Transaksi berhasil ditambahkan')
    // Reset form
    newTransaction.amount = null
    newTransaction.category_id = null
    newTransaction.description = ''
    newTransaction.reference = ''
  } catch (error) {
    showToast(error.response?.data?.detail || 'Gagal membuat transaksi', 'error')
  } finally {
    saving.value = false
  }
}

const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0]
  importResult.value = null
}

const uploadImport = async () => {
  if (!selectedFile.value) return
  
  importing.value = true
  importResult.value = null
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  try {
    const response = await transactionsAPI.importCSV(formData)
    importResult.value = response.data
    if (response.data.message.includes('Successfully')) {
      await Promise.all([fetchTransactions(), fetchSummary()])
      selectedFile.value = null
      if (fileInput.value) fileInput.value.value = ''
    }
  } catch (error) {
    importResult.value = { errors: [error.response?.data?.detail || 'Gagal upload file'] }
  } finally {
    importing.value = false
  }
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(value || 0)
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
  fetchTransactions()
  fetchSummary()
  fetchCategories()
  fetchAccounts()
})
</script>

<style scoped>
.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.summary-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--glass-border);
}

.summary-card.green { border-left: 4px solid var(--color-success); }
.summary-card.red { border-left: 4px solid var(--color-danger); }
.summary-card.purple { border-left: 4px solid var(--accent-secondary); }
.summary-card.blue { border-left: 4px solid var(--color-info); }

.summary-icon {
  font-size: 1.5rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border-radius: var(--radius-lg);
}

.summary-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
}

.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.filters {
  display: flex;
  gap: var(--spacing-md);
}

.filters .form-input {
  width: 180px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 500px;
  border: 1px solid var(--glass-border);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
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

@media (max-width: 1024px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
  .filters-bar {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  .filters {
    flex-wrap: wrap;
  }
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
</style>
