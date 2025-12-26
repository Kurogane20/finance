<template>
  <div class="users-page fade-in">
    <div class="page-actions">
      <button class="btn btn-primary" @click="showModal = true">➕ Tambah User</button>
    </div>

    <div class="card">
      <DataTable :columns="columns" :data="users">
        <template #role="{ row }">
          <span class="badge" :class="roleBadge(row.role?.name)">{{ row.role?.name }}</span>
        </template>
        <template #is_active="{ value }">
          <span class="badge" :class="value ? 'badge-success' : 'badge-danger'">
            {{ value ? 'Aktif' : 'Nonaktif' }}
          </span>
        </template>
        <template #actions="{ row }">
          <button class="btn btn-ghost btn-icon" @click="deactivateUser(row.id)" title="Nonaktifkan">🚫</button>
        </template>
      </DataTable>
    </div>

    <!-- Add User Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Tambah User Baru</h3>
          <button class="btn btn-ghost btn-icon" @click="showModal = false">✕</button>
        </div>
        <form @submit.prevent="createUser" class="modal-body">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="newUser.email" type="email" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Nama Lengkap</label>
            <input v-model="newUser.full_name" type="text" class="form-input" required>
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input v-model="newUser.password" type="password" class="form-input" required minlength="6">
          </div>
          <div class="form-group">
            <label class="form-label">Role</label>
            <select v-model="newUser.role_id" class="form-input form-select" required>
              <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
            </select>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showModal = false">Batal</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? 'Menyimpan...' : 'Simpan' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { usersAPI } from '@/api'
import DataTable from '@/components/common/DataTable.vue'

const users = ref([])
const roles = ref([])
const showModal = ref(false)
const saving = ref(false)
const newUser = reactive({ email: '', full_name: '', password: '', role_id: 1 })

const columns = [
  { key: 'id', label: 'ID', width: '60px' },
  { key: 'full_name', label: 'Nama' },
  { key: 'email', label: 'Email' },
  { key: 'role', label: 'Role' },
  { key: 'is_active', label: 'Status' },
  { key: 'created_at', label: 'Terdaftar', type: 'date' },
  { key: 'actions', label: '', width: '60px' }
]

const roleBadge = (r) => ({ admin: 'badge-danger', approver: 'badge-warning', editor: 'badge-info', viewer: 'badge-neutral' }[r] || 'badge-neutral')

const fetchUsers = async () => { users.value = (await usersAPI.getAll()).data }
const fetchRoles = async () => { roles.value = (await usersAPI.getRoles()).data }

const createUser = async () => {
  saving.value = true
  try {
    await usersAPI.create(newUser)
    showModal.value = false
    fetchUsers()
    Object.assign(newUser, { email: '', full_name: '', password: '', role_id: 1 })
  } catch (e) {
    alert(e.response?.data?.detail || 'Gagal membuat user')
  }
  saving.value = false
}

const deactivateUser = async (id) => {
  if (!confirm('Yakin ingin menonaktifkan user ini?')) return
  await usersAPI.delete(id)
  fetchUsers()
}

onMounted(() => { fetchUsers(); fetchRoles() })
</script>

<style scoped>
.page-actions { display: flex; justify-content: flex-end; margin-bottom: 1rem; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--bg-secondary); border-radius: 1rem; width: 100%; max-width: 450px; border: 1px solid var(--glass-border); }
.modal-header { display: flex; justify-content: space-between; padding: 1rem; border-bottom: 1px solid var(--glass-border); }
.modal-body { padding: 1rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.5rem; padding-top: 1rem; }
</style>
