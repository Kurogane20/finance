<template>
  <header class="navbar">
    <div class="navbar-left">
      <button class="mobile-toggle" @click="$emit('toggle-sidebar')">☰</button>
      <div class="page-info">
        <h1 class="view-title">{{ pageTitle }}</h1>
        <p class="view-date">{{ currentDate }}</p>
      </div>
    </div>
    
    <div class="navbar-right">
      <button class="btn-icon" @click="toggleTheme" title="Ganti Tema">
        {{ isDark ? '🌞' : '🌙' }}
      </button>
      <button class="btn-icon notification-btn" title="Notifikasi">
        🔔
        <span class="badge"></span>
      </button>
      <div class="separator"></div>
      <button class="btn logout-btn" @click="handleLogout" title="Keluar">
        🚪
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isDark = ref(true)

defineEmits(['toggle-sidebar'])

const pageTitles = {
  '/': 'Dashboard Overview',
  '/transactions': 'Data Transaksi',
  '/invoices': 'Invoice Management',
  '/accounts': 'Akun & Buku Besar',
  '/budgets': 'Perencanaan Anggaran',
  '/reports': 'Laporan Keuangan',
  '/users': 'User Management',
  '/audit-logs': 'System Logs',
  '/profile': 'My Profile',
  '/settings': 'System Settings'
}

const pageTitle = computed(() => pageTitles[route.path] || 'Dashboard')

const currentDate = computed(() => {
  return new Date().toLocaleDateString('id-ID', { 
    weekday: 'long', 
    day: 'numeric', 
    month: 'long', 
    year: 'numeric' 
  })
})

const toggleTheme = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.remove('light')
  } else {
    document.documentElement.classList.add('light')
  }
}

const handleLogout = async () => {
  if(confirm("Apakah Anda yakin ingin keluar?")) {
    await authStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  isDark.value = !document.documentElement.classList.contains('light')
})
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding: 0.5rem 0;
  animation: slideDown 0.5s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mobile-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-primary);
  cursor: pointer;
}

.view-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.view-date {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: var(--bg-card);
  padding: 0.5rem;
  border-radius: 100px; /* Pill shape */
  border: var(--glass-border);
  box-shadow: var(--glass-shadow);
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--bg-hover);
  transform: rotate(15deg);
}

.notification-btn {
  position: relative;
}

.badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  background: var(--secondary-color);
  border-radius: 50%;
}

.separator {
  width: 1px;
  height: 24px;
  background: var(--border-color);
  margin: 0 0.25rem;
}

.logout-btn {
  border: none;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #ef4444;
  color: white;
}

@media (max-width: 768px) {
  .mobile-toggle {
    display: block;
  }
}
</style>
