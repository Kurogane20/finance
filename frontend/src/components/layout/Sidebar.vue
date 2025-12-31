<template>
  <aside class="sidebar" :class="{ open: isOpen }">
    <button class="sidebar-close" @click="$emit('close')" aria-label="Close Menu">✕</button>
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <div class="sidebar-logo-icon">💰</div>
        <span class="sidebar-logo-text">FinanceHub</span>
      </div>
    </div>
    
    <nav class="sidebar-nav">
      <div class="nav-section">
        <div class="nav-section-title">Menu Utama</div>
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
        </router-link>
      </div>
      
      <div class="nav-section" v-if="authStore.canApprove">
        <div class="nav-section-title">Administrasi</div>
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
      <div class="user-info">
        <div class="user-avatar">{{ authStore.userInitials }}</div>
        <div class="user-details">
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
  { path: '/invoices', icon: '📄', label: 'Invoice' },
  { path: '/accounts', icon: '🏦', label: 'Akun & AR/AP' },
  { path: '/budgets', icon: '📋', label: 'Anggaran' },
  { path: '/reports', icon: '📈', label: 'Laporan' }
]

const adminMenuItems = computed(() => {
  const items = [
    { path: '/audit-logs', icon: '📝', label: 'Audit Log' }
  ]
  if (authStore.isAdmin) {
    items.unshift({ path: '/users', icon: '👥', label: 'Pengguna' })
    items.push({ path: '/settings', icon: '⚙️', label: 'Pengaturan' })
  }
  return items
})

const roleName = computed(() => {
  const roles = {
    admin: 'Administrator',
    approver: 'Manager/Approver',
    editor: 'Akuntan',
    viewer: 'Staff'
  }
  return roles[authStore.userRole] || 'User'
})

const isActive = (path) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>
