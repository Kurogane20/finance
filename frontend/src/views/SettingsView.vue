<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Pengaturan</h1>
    </div>

    <div class="settings-grid">
      <!-- Company Profile -->
      <div class="card settings-card">
        <div class="card-header">
          <h3>🏢 Profil Perusahaan</h3>
        </div>
        <div class="card-body">
          <form @submit.prevent="saveCompany" class="settings-form">
            <div class="form-group">
              <label class="form-label">Nama Perusahaan</label>
              <input v-model="companyForm.name" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Alamat</label>
              <textarea v-model="companyForm.address" class="form-input" rows="3"></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Telepon</label>
                <input v-model="companyForm.phone" type="tel" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">Email</label>
                <input v-model="companyForm.email" type="email" class="form-input" />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">NPWP</label>
              <input v-model="companyForm.tax_id" type="text" class="form-input" />
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="savingCompany">
                {{ savingCompany ? 'Menyimpan...' : 'Simpan' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Financial Settings -->
      <div class="card settings-card">
        <div class="card-header">
          <h3>💰 Pengaturan Keuangan</h3>
        </div>
        <div class="card-body">
          <form @submit.prevent="saveFinancial" class="settings-form">
            <div class="form-group">
              <label class="form-label">Mata Uang Default</label>
              <select v-model="financialForm.currency" class="form-input">
                <option value="IDR">IDR - Rupiah Indonesia</option>
                <option value="USD">USD - US Dollar</option>
                <option value="SGD">SGD - Singapore Dollar</option>
              </select>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Awal Tahun Fiskal</label>
                <select v-model="financialForm.fiscal_year_start" class="form-input">
                  <option value="1">Januari</option>
                  <option value="4">April</option>
                  <option value="7">Juli</option>
                  <option value="10">Oktober</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Format Tanggal</label>
                <select v-model="financialForm.date_format" class="form-input">
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Tarif Pajak Default (%)</label>
              <input v-model.number="financialForm.default_tax_rate" type="number" class="form-input" />
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="savingFinancial">
                {{ savingFinancial ? 'Menyimpan...' : 'Simpan' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Appearance -->
      <div class="card settings-card">
        <div class="card-header">
          <h3>🎨 Tampilan</h3>
        </div>
        <div class="card-body">
          <div class="settings-form">
            <div class="form-group">
              <label class="form-label">Tema</label>
              <div class="theme-options">
                <button 
                  :class="['theme-btn', { active: theme === 'light' }]"
                  @click="setTheme('light')"
                >
                  ☀️ Terang
                </button>
                <button 
                  :class="['theme-btn', { active: theme === 'dark' }]"
                  @click="setTheme('dark')"
                >
                  🌙 Gelap
                </button>
                <button 
                  :class="['theme-btn', { active: theme === 'auto' }]"
                  @click="setTheme('auto')"
                >
                  💻 Sistem
                </button>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Bahasa</label>
              <select v-model="appearance.language" class="form-input">
                <option value="id">Bahasa Indonesia</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Notification Settings -->
      <div class="card settings-card">
        <div class="card-header">
          <h3>🔔 Notifikasi</h3>
        </div>
        <div class="card-body">
          <div class="settings-form">
            <div class="toggle-group">
              <div class="toggle-item">
                <div class="toggle-info">
                  <div class="toggle-label">Email Ringkasan Harian</div>
                  <div class="toggle-desc">Terima ringkasan transaksi harian via email</div>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="notifications.daily_summary" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
              <div class="toggle-item">
                <div class="toggle-info">
                  <div class="toggle-label">Peringatan Jatuh Tempo</div>
                  <div class="toggle-desc">Notifikasi invoice yang akan jatuh tempo</div>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="notifications.due_date_reminder" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
              <div class="toggle-item">
                <div class="toggle-info">
                  <div class="toggle-label">Peringatan Budget</div>
                  <div class="toggle-desc">Notifikasi ketika budget hampir habis</div>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="notifications.budget_alert" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Danger Zone -->
      <div class="card settings-card danger-zone">
        <div class="card-header">
          <h3>⚠️ Zona Berbahaya</h3>
        </div>
        <div class="card-body">
          <div class="danger-item">
            <div class="danger-info">
              <div class="danger-label">Export Data</div>
              <div class="danger-desc">Download semua data dalam format CSV/Excel</div>
            </div>
            <button class="btn btn-outline">Export</button>
          </div>
          <div class="danger-item">
            <div class="danger-info">
              <div class="danger-label">Reset Database Demo</div>
              <div class="danger-desc">Hapus semua data dan isi ulang dengan data demo</div>
            </div>
            <button class="btn btn-danger" @click="confirmReset">Reset</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const theme = ref(localStorage.getItem('theme') || 'light')
const savingCompany = ref(false)
const savingFinancial = ref(false)

const companyForm = reactive({
  name: 'PT Mitra Mutiara',
  address: '',
  phone: '',
  email: '',
  tax_id: ''
})

const financialForm = reactive({
  currency: 'IDR',
  fiscal_year_start: '1',
  date_format: 'DD/MM/YYYY',
  default_tax_rate: 11
})

const appearance = reactive({
  language: 'id'
})

const notifications = reactive({
  daily_summary: false,
  due_date_reminder: true,
  budget_alert: true
})

const setTheme = (newTheme) => {
  theme.value = newTheme
  localStorage.setItem('theme', newTheme)
  
  if (newTheme === 'light') {
    document.documentElement.classList.add('light')
  } else if (newTheme === 'dark') {
    document.documentElement.classList.remove('light')
  } else {
    // Auto - follow system preference
    if (window.matchMedia('(prefers-color-scheme: light)').matches) {
      document.documentElement.classList.add('light')
    } else {
      document.documentElement.classList.remove('light')
    }
  }
}

const saveCompany = async () => {
  savingCompany.value = true
  try {
    // Save to localStorage for now (API not implemented)
    localStorage.setItem('company_settings', JSON.stringify(companyForm))
    alert('Pengaturan perusahaan berhasil disimpan!')
  } finally {
    savingCompany.value = false
  }
}

const saveFinancial = async () => {
  savingFinancial.value = true
  try {
    localStorage.setItem('financial_settings', JSON.stringify(financialForm))
    alert('Pengaturan keuangan berhasil disimpan!')
  } finally {
    savingFinancial.value = false
  }
}

const confirmReset = () => {
  if (confirm('PERHATIAN: Tindakan ini akan menghapus semua data! Apakah Anda yakin?')) {
    alert('Fitur ini belum tersedia.')
  }
}

onMounted(() => {
  // Load saved settings
  const savedCompany = localStorage.getItem('company_settings')
  if (savedCompany) {
    Object.assign(companyForm, JSON.parse(savedCompany))
  }
  
  const savedFinancial = localStorage.getItem('financial_settings')
  if (savedFinancial) {
    Object.assign(financialForm, JSON.parse(savedFinancial))
  }
  
  // Apply theme
  setTheme(theme.value)
})
</script>

<style scoped>
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--spacing-lg);
}

.settings-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.card-header {
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.card-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.card-body {
  padding: var(--spacing-lg);
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-label {
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.form-input {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 1rem;
}

.form-actions {
  margin-top: var(--spacing-sm);
}

/* Theme Options */
.theme-options {
  display: flex;
  gap: var(--spacing-sm);
}

.theme-btn {
  flex: 1;
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.theme-btn:hover {
  border-color: var(--primary-color);
}

.theme-btn.active {
  border-color: var(--primary-color);
  background: var(--primary-color-light);
}

/* Toggle Switches */
.toggle-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.toggle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

.toggle-label {
  font-weight: 500;
  color: var(--text-primary);
}

.toggle-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 2px;
}

.toggle-switch {
  position: relative;
  width: 50px;
  height: 26px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 26px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

.toggle-switch input:checked + .toggle-slider {
  background-color: var(--primary-color);
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

/* Danger Zone */
.danger-zone .card-header {
  background: rgba(239, 68, 68, 0.05);
}

.danger-zone .card-header h3 {
  color: #dc2626;
}

.danger-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.danger-item:last-child {
  border-bottom: none;
}

.danger-label {
  font-weight: 500;
}

.danger-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 2px;
}

.btn-danger {
  background: #dc2626;
  color: white;
  border: none;
}

.btn-danger:hover {
  background: #b91c1c;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .theme-options {
    flex-direction: column;
  }
}
</style>
