<template>
  <aside class="sidebar" :class="{ open: isOpen }">
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <div class="logo-icon">💵</div>
        <span class="logo-text">Finance<span class="highlight">OS</span></span>
      </div>
      <button class="sidebar-close" @click="$emit('close')" aria-label="Close Menu">×</button>
    </div>
    
    <nav class="sidebar-nav">
      <div class="nav-group">
        <label class="nav-label">Main Menu</label>
        <router-link 
          v-for="item in mainMenuItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          @click="$emit('close')"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-text">{{ item.label }}</span>
          <div class="active-indicator" v-if="isActive(item.path)"></div>
        </router-link>
      </div>
      
      <div class="nav-group" v-if="authStore.canApprove">
        <label class="nav-label">Management</label>
        <router-link 
          v-for="item in adminMenuItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          @click="$emit('close')"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-text">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>
    
    <div class="sidebar-footer">
      <div class="user-card">
        <div class="user-avatar">{{ authStore.userInitials }}</div>
        <div class="user-info">
          <div class="user-name">{{ authStore.userName }}</div>
          <div class="user-role">{{ roleName }}</div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])

const route = useRoute()
const authStore = useAuthStore()

const mainMenuItems = [
  { path: '/', icon: '📊', label: 'Dashboard' },
  { path: '/transactions', icon: '💳', label: 'Transaksi' },
  { path: '/invoices', icon: '📄', label: 'Invoices' },
  { path: '/accounts', icon: '🏦', label: 'Akun & Ledger' },
  { path: '/budgets', icon: '🎯', label: 'Anggaran' },
  { path: '/reports', icon: '📈', label: 'Laporan' }
]

const adminMenuItems = computed(() => {
  const items = [
    { path: '/audit-logs', icon: '🔒', label: 'Audit Logs' }
  ]
  if (authStore.isAdmin) {
    items.unshift({ path: '/users', icon: '👥', label: 'Pengguna' })
    items.push({ path: '/settings', icon: '⚡', label: 'Pengaturan' })
  }
  return items
})

const roleName = computed(() => {
  const roles = {
    admin: 'Administrator',
    approver: 'Manager',
    editor: 'Finance Staff',
    viewer: 'Viewer'
  }
  return roles[authStore.userRole] || 'User'
})

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: var(--bg-sidebar);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: var(--glass-border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 1.5rem;
}

.sidebar-header {
  margin-bottom: 2.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.logo-icon {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.logo-text {
  letter-spacing: -0.03em;
}

.highlight {
  color: var(--primary-color);
}

.sidebar-close {
  display: none;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 1.5rem;
  cursor: pointer;
}

.nav-group {
  margin-bottom: 2rem;
}

.nav-label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 600;
  letter-spacing: 0.1em;
  margin-bottom: 1rem;
  padding-left: 0.75rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem 1rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 12px;
  transition: all 0.2s ease;
  margin-bottom: 0.25rem;
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  transform: translateX(4px);
}

.nav-item.active {
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.1), transparent);
  color: var(--primary-color);
  font-weight: 600;
}

.nav-item.active .nav-icon {
  transform: scale(1.1);
}

.active-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--primary-color);
  border-radius: 0 4px 4px 0;
}

.nav-icon {
  width: 24px;
  text-align: center;
  font-size: 1.1rem;
  transition: transform 0.2s;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: rgba(0,0,0,0.1);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: var(--primary-dark);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.user-info {
  flex: 1;
  overflow: hidden;
}

.user-name {
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }
  .sidebar.open {
    transform: translateX(0);
  }
  .sidebar-close {
    display: block;
  }
}
</style>
