<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Profil Saya</h1>
    </div>

    <div class="profile-grid">
      <!-- Profile Info Card -->
      <div class="card profile-card">
        <div class="card-header">
          <h3>Informasi Profil</h3>
        </div>
        <div class="card-body">
          <div class="profile-avatar">
            <div class="avatar-circle">{{ userInitials }}</div>
            <div class="profile-info">
              <h2>{{ user?.full_name }}</h2>
              <span class="role-badge">{{ user?.role?.name }}</span>
            </div>
          </div>

          <form @submit.prevent="updateProfile" class="profile-form">
            <div class="form-group">
              <label class="form-label">Nama Lengkap</label>
              <input 
                v-model="profileForm.full_name" 
                type="text" 
                class="form-input"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">Email</label>
              <input 
                v-model="profileForm.email" 
                type="email" 
                class="form-input"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">Role</label>
              <input 
                :value="user?.role?.name" 
                type="text" 
                class="form-input"
                disabled
              />
              <small class="form-hint">Role hanya bisa diubah oleh admin</small>
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="profileLoading">
                {{ profileLoading ? 'Menyimpan...' : 'Simpan Perubahan' }}
              </button>
            </div>
          </form>

          <div v-if="profileMessage" :class="['alert', profileError ? 'alert-error' : 'alert-success']">
            {{ profileMessage }}
          </div>
        </div>
      </div>

      <!-- Password Change Card -->
      <div class="card password-card">
        <div class="card-header">
          <h3>Ubah Password</h3>
        </div>
        <div class="card-body">
          <form @submit.prevent="changePassword" class="password-form">
            <div class="form-group">
              <label class="form-label">Password Lama</label>
              <input 
                v-model="passwordForm.current_password" 
                type="password" 
                class="form-input"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">Password Baru</label>
              <input 
                v-model="passwordForm.new_password" 
                type="password" 
                class="form-input"
                minlength="8"
                required
              />
              <small class="form-hint">Minimal 8 karakter</small>
            </div>
            <div class="form-group">
              <label class="form-label">Konfirmasi Password Baru</label>
              <input 
                v-model="passwordForm.confirm_password" 
                type="password" 
                class="form-input"
                required
              />
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="passwordLoading">
                {{ passwordLoading ? 'Mengubah...' : 'Ubah Password' }}
              </button>
            </div>
          </form>

          <div v-if="passwordMessage" :class="['alert', passwordError ? 'alert-error' : 'alert-success']">
            {{ passwordMessage }}
          </div>
        </div>
      </div>

      <!-- Account Info Card -->
      <div class="card info-card">
        <div class="card-header">
          <h3>Informasi Akun</h3>
        </div>
        <div class="card-body">
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">Status</span>
              <span :class="['status-badge', user?.is_active ? 'status-active' : 'status-inactive']">
                {{ user?.is_active ? 'Aktif' : 'Nonaktif' }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">Dibuat</span>
              <span class="info-value">{{ formatDate(user?.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Permissions</span>
              <div class="permissions-list">
                <span v-for="(value, key) in user?.role?.permissions" :key="key" class="permission-badge">
                  {{ key }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usersAPI } from '@/api'

const authStore = useAuthStore()
const user = computed(() => authStore.user)
const userInitials = computed(() => authStore.userInitials)

// Profile form
const profileForm = reactive({
  full_name: '',
  email: ''
})
const profileLoading = ref(false)
const profileMessage = ref('')
const profileError = ref(false)

// Password form
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
const passwordLoading = ref(false)
const passwordMessage = ref('')
const passwordError = ref(false)

onMounted(() => {
  if (user.value) {
    profileForm.full_name = user.value.full_name
    profileForm.email = user.value.email
  }
})

const updateProfile = async () => {
  profileLoading.value = true
  profileMessage.value = ''
  profileError.value = false

  try {
    const response = await usersAPI.updateProfile({
      full_name: profileForm.full_name,
      email: profileForm.email
    })
    
    // Update local user data
    authStore.user = response.data
    localStorage.setItem('user', JSON.stringify(response.data))
    
    profileMessage.value = 'Profil berhasil diperbarui!'
  } catch (error) {
    profileError.value = true
    profileMessage.value = error.response?.data?.detail || 'Gagal memperbarui profil'
  } finally {
    profileLoading.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordError.value = true
    passwordMessage.value = 'Password baru dan konfirmasi tidak cocok'
    return
  }

  passwordLoading.value = true
  passwordMessage.value = ''
  passwordError.value = false

  try {
    await usersAPI.changePassword(
      passwordForm.current_password,
      passwordForm.new_password
    )
    
    passwordMessage.value = 'Password berhasil diubah!'
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error) {
    passwordError.value = true
    passwordMessage.value = error.response?.data?.detail || 'Gagal mengubah password'
  } finally {
    passwordLoading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('id-ID', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: var(--spacing-lg);
}

.profile-card,
.password-card,
.info-card {
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
  color: var(--text-primary);
}

.card-body {
  padding: var(--spacing-lg);
}

/* Profile Avatar */
.profile-avatar {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 600;
}

.profile-info h2 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: 1.4rem;
  color: var(--text-primary);
}

.role-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--primary-color-light);
  color: var(--primary-color);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  text-transform: capitalize;
}

/* Forms */
.profile-form,
.password-form {
  display: flex;
  flex-direction: column;
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
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-color-light);
}

.form-input:disabled {
  background: var(--bg-secondary);
  cursor: not-allowed;
}

.form-hint {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.form-actions {
  margin-top: var(--spacing-sm);
}

/* Alerts */
.alert {
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  margin-top: var(--spacing-md);
  font-size: 0.9rem;
}

.alert-success {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

/* Info List */
.info-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.info-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.info-value {
  color: var(--text-primary);
  font-weight: 500;
}

.status-badge {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
}

.status-active {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.status-inactive {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.permission-badge {
  padding: 2px 8px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  text-transform: capitalize;
}

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  
  .profile-avatar {
    flex-direction: column;
    text-align: center;
  }
}
</style>
