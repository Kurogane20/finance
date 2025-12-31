<template>
  <header class="navbar">
    <div class="navbar-left">
      <h1 class="page-title">{{ pageTitle }}</h1>
      <p class="page-date">{{ currentDate }}</p>
    </div>
    
    <div class="navbar-right">
      <button class="btn btn-ghost btn-icon" title="Notifikasi">
        🔔
      </button>
      <router-link to="/settings" class="btn btn-ghost btn-icon" title="Pengaturan">
        ⚙️
      </router-link>
      <router-link to="/profile" class="btn btn-ghost user-btn" title="Profil">
        <span class="user-avatar-sm">{{ authStore.userInitials }}</span>
        <span class="user-name-sm">{{ authStore.userName }}</span>
      </router-link>
      <button class="btn btn-secondary" @click="handleLogout">
        🚪 Keluar
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const pageTitles = {
  '/': 'Dashboard',
  '/transactions': 'Transaksi',
  '/invoices': 'Invoice',
  '/accounts': 'Akun & AR/AP',
  '/budgets': 'Anggaran',
  '/reports': 'Laporan',
  '/users': 'Manajemen Pengguna',
  '/audit-logs': 'Audit Log',
  '/profile': 'Profil Saya',
  '/settings': 'Pengaturan'
}

const pageTitle = computed(() => pageTitles[route.path] || 'Dashboard')

const currentDate = computed(() => {
  const options = { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  }
  return new Date().toLocaleDateString('id-ID', options)
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) 0;
  margin-bottom: var(--spacing-lg);
}

.navbar-left {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.page-date {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
</style>
