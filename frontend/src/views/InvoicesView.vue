<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Invoice</h1>
      <div class="page-actions">
        <button class="btn btn-primary" @click="showCreateModal = true">
          + Buat Invoice
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.value"
        :class="['tab-btn', { active: activeTab === tab.value }]"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
        <span class="tab-count">{{ getTabCount(tab.value) }}</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon receivable">📥</div>
        <div class="stat-content">
          <div class="stat-label">Piutang</div>
          <div class="stat-value">{{ formatCurrency(stats.totalReceivable) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon payable">📤</div>
        <div class="stat-content">
          <div class="stat-label">Hutang</div>
          <div class="stat-value">{{ formatCurrency(stats.totalPayable) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon overdue">⚠️</div>
        <div class="stat-content">
          <div class="stat-label">Jatuh Tempo</div>
          <div class="stat-value">{{ stats.overdueCount }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon pending">⏳</div>
        <div class="stat-content">
          <div class="stat-label">Pending</div>
          <div class="stat-value">{{ stats.pendingCount }}</div>
        </div>
      </div>
    </div>

    <!-- Invoice Table -->
    <div class="card">
      <div class="card-header">
        <h3>Daftar Invoice</h3>
        <div class="filter-group">
          <select v-model="filterStatus" class="filter-select">
            <option value="">Semua Status</option>
            <option value="draft">Draft</option>
            <option value="sent">Terkirim</option>
            <option value="paid">Lunas</option>
            <option value="overdue">Jatuh Tempo</option>
          </select>
        </div>
      </div>
      <div class="card-body">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <span>Memuat data...</span>
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>No. Invoice</th>
              <th>Customer/Vendor</th>
              <th>Tanggal</th>
              <th>Jatuh Tempo</th>
              <th>Total</th>
              <th>Status</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="invoice in filteredInvoices" :key="invoice.id">
              <td class="font-mono">{{ invoice.invoice_number }}</td>
              <td>{{ invoice.customer_name }}</td>
              <td>{{ formatDate(invoice.issue_date) }}</td>
              <td>{{ formatDate(invoice.due_date) }}</td>
              <td class="text-right font-mono">{{ formatCurrency(invoice.total_amount) }}</td>
              <td>
                <span :class="['status-badge', `status-${invoice.status}`]">
                  {{ getStatusLabel(invoice.status) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn btn-sm btn-outline" @click="viewInvoice(invoice)">
                    👁️
                  </button>
                  <button class="btn btn-sm btn-outline" @click="editInvoice(invoice)">
                    ✏️
                  </button>
                  <button v-if="invoice.status !== 'paid'" class="btn btn-sm btn-success ml-1" @click="openPayModal(invoice)" title="Bayar">
                    💰
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredInvoices.length === 0">
              <td colspan="7" class="empty-state">
                Tidak ada invoice
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Invoice Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingInvoice ? 'Edit Invoice' : 'Buat Invoice Baru' }}</h3>
          <button class="btn-close" @click="showCreateModal = false">×</button>
        </div>
        <form @submit.prevent="saveInvoice" class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Tipe Invoice</label>
              <select v-model="invoiceForm.type" class="form-input" required>
                <option value="receivable">Piutang (AR)</option>
                <option value="payable">Hutang (AP)</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">No. Invoice</label>
              <input v-model="invoiceForm.invoice_number" type="text" class="form-input" required />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">{{ invoiceForm.type === 'receivable' ? 'Customer' : 'Vendor' }}</label>
            <input v-model="invoiceForm.customer_name" type="text" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="invoiceForm.customer_email" type="email" class="form-input" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Tanggal Invoice</label>
              <input v-model="invoiceForm.issue_date" type="date" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Jatuh Tempo</label>
              <input v-model="invoiceForm.due_date" type="date" class="form-input" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Jumlah</label>
              <input v-model.number="invoiceForm.amount" type="number" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Pajak (%)</label>
              <input v-model.number="invoiceForm.tax_rate" type="number" class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Total: {{ formatCurrency(calculatedTotal) }}</label>
          </div>
          <div class="form-group">
            <label class="form-label">Catatan</label>
            <textarea v-model="invoiceForm.notes" class="form-input" rows="3"></textarea>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline" @click="showCreateModal = false">Batal</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Menyimpan...' : 'Simpan' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Pay Invoice Modal -->
    <div v-if="showPayModal" class="modal-overlay" @click.self="showPayModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Bayar Invoice {{ payingInvoice?.invoice_number }}</h3>
          <button class="btn-close" @click="showPayModal = false">×</button>
        </div>
        <div class="modal-body">
          <p class="mb-4">
            Total: <strong>{{ formatCurrency(payingInvoice?.total_amount) }}</strong><br>
            Tipe: {{ payingInvoice?.type === 'receivable' ? 'Terima Pembayaran' : 'Lakukan Pembayaran' }}
          </p>
          <div class="form-group">
            <label class="form-label">Pilih Akun {{ payingInvoice?.type === 'receivable' ? 'Penerima' : 'Sumber' }}</label>
            <select v-model="selectedAccount" class="form-input" required>
              <option :value="null">Pilih Akun...</option>
              <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
                {{ acc.name }} ({{ formatCurrency(acc.balance) }})
              </option>
            </select>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showPayModal = false">Batal</button>
            <button class="btn btn-primary" :disabled="!selectedAccount || processingPayment" @click="processPayment">
              {{ processingPayment ? 'Memproses...' : 'Bayar Sekarang' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/api'

const loading = ref(true)
const saving = ref(false)
const showCreateModal = ref(false)
const editingInvoice = ref(null)
const invoices = ref([])
const activeTab = ref('all')
const filterStatus = ref('')

const showPayModal = ref(false)
const payingInvoice = ref(null)
const selectedAccount = ref(null)
const processingPayment = ref(false)
const accounts = ref([])

const tabs = [
  { value: 'all', label: 'Semua' },
  { value: 'receivable', label: 'Piutang (AR)' },
  { value: 'payable', label: 'Hutang (AP)' }
]

const invoiceForm = reactive({
  type: 'receivable',
  invoice_number: '',
  customer_name: '',
  customer_email: '',
  issue_date: '',
  due_date: '',
  amount: 0,
  tax_rate: 11,
  notes: ''
})

const stats = computed(() => {
  const receivables = invoices.value.filter(i => i.type === 'receivable')
  const payables = invoices.value.filter(i => i.type === 'payable')
  const overdue = invoices.value.filter(i => i.status === 'overdue')
  const pending = invoices.value.filter(i => ['draft', 'sent', 'viewed'].includes(i.status))
  
  return {
    totalReceivable: receivables.reduce((sum, i) => sum + Number(i.total_amount || 0), 0),
    totalPayable: payables.reduce((sum, i) => sum + Number(i.total_amount || 0), 0),
    overdueCount: overdue.length,
    pendingCount: pending.length
  }
})

const filteredInvoices = computed(() => {
  let result = invoices.value
  
  if (activeTab.value !== 'all') {
    result = result.filter(i => i.type === activeTab.value)
  }
  
  if (filterStatus.value) {
    result = result.filter(i => i.status === filterStatus.value)
  }
  
  return result
})

const calculatedTotal = computed(() => {
  const amount = invoiceForm.amount || 0
  const taxRate = invoiceForm.tax_rate || 0
  const tax = amount * (taxRate / 100)
  return amount + tax
})

const getTabCount = (tab) => {
  if (tab === 'all') return invoices.value.length
  return invoices.value.filter(i => i.type === tab).length
}

const getStatusLabel = (status) => {
  const labels = {
    draft: 'Draft',
    sent: 'Terkirim',
    viewed: 'Dilihat',
    paid: 'Lunas',
    overdue: 'Jatuh Tempo',
    cancelled: 'Dibatalkan'
  }
  return labels[status] || status
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(value || 0)
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('id-ID')
}

const fetchInvoices = async () => {
  loading.value = true
  try {
    // Get invoices from accounts endpoint with invoice filter
    const response = await api.get('/accounts/invoices')
    invoices.value = response.data
  } catch (error) {
    // If endpoint doesn't exist, use mock data for now
    invoices.value = []
  } finally {
    loading.value = false
  }
}

const fetchAccounts = async () => {
  try {
    const response = await api.get('/accounts')
    accounts.value = response.data
  } catch (error) {
    console.error('Failed to fetch accounts', error)
  }
}

const viewInvoice = (invoice) => {
  // TODO: Open detail view
  alert(`View invoice: ${invoice.invoice_number}`)
}

const editInvoice = (invoice) => {
  editingInvoice.value = invoice
  Object.assign(invoiceForm, {
    type: invoice.type,
    invoice_number: invoice.invoice_number,
    customer_name: invoice.customer_name,
    customer_email: invoice.customer_email || '',
    issue_date: invoice.issue_date,
    due_date: invoice.due_date,
    amount: Number(invoice.amount),
    tax_rate: 11,
    notes: invoice.notes || ''
  })
  showCreateModal.value = true
}

const openPayModal = (invoice) => {
  payingInvoice.value = invoice
  selectedAccount.value = null
  showPayModal.value = true
  if (accounts.value.length === 0) fetchAccounts()
}

const processPayment = async () => {
  if (!payingInvoice.value || !selectedAccount.value) return
  
  processingPayment.value = true
  try {
    const payload = { account_id: selectedAccount.value }
    await api.post(`/accounts/invoices/${payingInvoice.value.id}/pay`, payload)
    
    // Refresh data
    showPayModal.value = false
    await fetchInvoices()
    // Optionally refresh accounts balance if we track it in UI locally (we don't for now)
    
    alert('Pembayaran berhasil!')
  } catch (error) {
    alert(error.response?.data?.detail || 'Gagal memproses pembayaran')
  } finally {
    processingPayment.value = false
  }
}

const saveInvoice = async () => {
  saving.value = true
  try {
    const data = {
      ...invoiceForm,
      tax_amount: invoiceForm.amount * (invoiceForm.tax_rate / 100),
      total_amount: calculatedTotal.value
    }
    
    if (editingInvoice.value) {
      // Update existing
      await api.put(`/accounts/invoices/${editingInvoice.value.id}`, data)
    } else {
      // Create new
      await api.post('/accounts/invoices', data)
    }
    
    showCreateModal.value = false
    editingInvoice.value = null
    resetForm()
    fetchInvoices()
  } catch (error) {
    alert(error.response?.data?.detail || 'Gagal menyimpan invoice')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  Object.assign(invoiceForm, {
    type: 'receivable',
    invoice_number: '',
    customer_name: '',
    customer_email: '',
    issue_date: '',
    due_date: '',
    amount: 0,
    tax_rate: 11,
    notes: ''
  })
}

onMounted(() => {
  fetchInvoices()
  fetchAccounts()
})
</script>

<style scoped>
.tabs {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: var(--spacing-sm);
}

.tab-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  transition: all 0.2s;
}

.tab-btn:hover {
  background: var(--bg-secondary);
}

.tab-btn.active {
  background: var(--primary-color);
  color: white;
}

.tab-count {
  background: rgba(0,0,0,0.1);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.stat-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  font-size: 1.5rem;
}

.stat-icon.receivable { background: rgba(16, 185, 129, 0.1); }
.stat-icon.payable { background: rgba(239, 68, 68, 0.1); }
.stat-icon.overdue { background: rgba(245, 158, 11, 0.1); }
.stat-icon.pending { background: rgba(99, 102, 241, 0.1); }

.stat-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.status-badge {
  padding: 4px 12px;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 500;
}

.status-draft { background: #e5e7eb; color: #374151; }
.status-sent { background: #dbeafe; color: #1d4ed8; }
.status-viewed { background: #e0e7ff; color: #4338ca; }
.status-paid { background: #d1fae5; color: #059669; }
.status-overdue { background: #fee2e2; color: #dc2626; }
.status-cancelled { background: #f3f4f6; color: #6b7280; }

.filter-select {
  padding: var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
