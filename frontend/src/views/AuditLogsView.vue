<template>
  <div class="audit-page fade-in">
    <div class="filters-bar mb-lg">
      <select v-model="filters.action" class="form-input form-select" @change="fetchLogs">
        <option value="">Semua Aksi</option>
        <option value="login">Login</option>
        <option value="logout">Logout</option>
        <option value="create">Create</option>
        <option value="update">Update</option>
        <option value="delete">Delete</option>
      </select>
      <select v-model="filters.entity" class="form-input form-select" @change="fetchLogs">
        <option value="">Semua Entitas</option>
        <option value="user">User</option>
        <option value="transaction">Transaksi</option>
        <option value="invoice">Invoice</option>
        <option value="budget">Budget</option>
      </select>
    </div>

    <div class="card">
      <DataTable :columns="columns" :data="logs">
        <template #action="{ value }">
          <span class="badge" :class="actionBadge(value)">{{ value }}</span>
        </template>
        <template #timestamp="{ value }">
          {{ new Date(value).toLocaleString('id-ID') }}
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { usersAPI } from '@/api'
import DataTable from '@/components/common/DataTable.vue'

const logs = ref([])
const filters = reactive({ action: '', entity: '' })

const columns = [
  { key: 'timestamp', label: 'Waktu' },
  { key: 'user_name', label: 'User' },
  { key: 'action', label: 'Aksi' },
  { key: 'entity', label: 'Entitas' },
  { key: 'description', label: 'Deskripsi' }
]

const actionBadge = (a) => ({ login: 'badge-success', logout: 'badge-neutral', create: 'badge-info', update: 'badge-warning', delete: 'badge-danger' }[a] || 'badge-neutral')

const fetchLogs = async () => {
  const params = {}
  if (filters.action) params.action = filters.action
  if (filters.entity) params.entity = filters.entity
  logs.value = (await usersAPI.getAuditLogs(params)).data
}

onMounted(fetchLogs)
</script>

<style scoped>
.filters-bar { display: flex; gap: 1rem; }
.filters-bar .form-input { width: 200px; }
</style>
