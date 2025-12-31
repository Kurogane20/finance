<template>
  <aside class="sidebar w-72 bg-slate-900 border-r border-slate-800 flex flex-col fixed inset-y-0 left-0 z-50 transition-transform duration-300 shadow-2xl" 
         :class="{ '-translate-x-full': !isOpen, 'translate-x-0': isOpen, 'md:translate-x-0': true }">
    
    <!-- Logo -->
    <div class="h-20 flex items-center px-8 border-b border-slate-800/50 bg-slate-900">
       <div class="flex items-center gap-3">
         <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-600 to-indigo-700 flex items-center justify-center text-white font-bold select-none shadow-lg shadow-primary-900/50">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
           </svg>
         </div>
         <span class="text-xl font-bold text-white tracking-tight">Finance<span class="text-primary-400">OS</span></span>
       </div>
       <button class="md:hidden ml-auto text-slate-400 hover:text-white transition-colors" @click="$emit('close')">
         ✕
       </button>
    </div>
    
    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-8 px-4 space-y-1 custom-scrollbar">
      <div class="mb-8">
        <p class="px-4 text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-3">Main Navigation</p>
        <router-link 
          v-for="item in mainMenuItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item group"
          :class="{ 'active': isActive(item.path) }"
          @click="$emit('close')"
        >
          <span class="icon-wrapper group-hover:text-white transition-colors" :class="isActive(item.path) ? 'text-primary-400' : 'text-slate-500'">
             {{ item.icon }}
          </span>
          <span class="font-medium tracking-wide text-sm">{{ item.label }}</span>
          <div class="active-indicator" v-if="isActive(item.path)"></div>
        </router-link>
      </div>

      <div v-if="authStore.canApprove">
        <p class="px-4 text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-3">Management</p>
        <router-link 
          v-for="item in adminMenuItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item group"
          :class="{ 'active': isActive(item.path) }"
          @click="$emit('close')"
        >
           <span class="icon-wrapper group-hover:text-white transition-colors" :class="isActive(item.path) ? 'text-primary-400' : 'text-slate-500'">
             {{ item.icon }}
          </span>
          <span class="font-medium tracking-wide text-sm">{{ item.label }}</span>
          <div class="active-indicator" v-if="isActive(item.path)"></div>
        </router-link>
      </div>
    </nav>
    
    <!-- User Footer -->
    <div class="p-6 border-t border-slate-800 bg-slate-900">
      <div class="flex items-center gap-3 p-3 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:bg-slate-800 hover:border-slate-600 transition-all cursor-pointer group">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 text-white flex items-center justify-center font-semibold text-sm border border-slate-600 shadow-inner group-hover:scale-105 transition-transform">
          {{ authStore.userInitials }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold text-slate-200 truncate group-hover:text-white">{{ authStore.userName }}</p>
          <p class="text-xs text-primary-400 truncate font-medium">{{ roleName }}</p>
        </div>
        <div class="text-slate-500 group-hover:text-white transition-colors">⚙️</div>
      </div>
    </div>
  </aside>

  <!-- Overlay for Mobile -->
  <div v-if="isOpen" class="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-40 md:hidden transition-opacity" @click="$emit('close')"></div>
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
  { path: '/transactions', icon: '💳', label: 'Transactions' },
  { path: '/journals', icon: '📓', label: 'General Journal' },
  { path: '/invoices', icon: '📄', label: 'Invoices' },
  { path: '/accounts', icon: '🏦', label: 'Chart of Accounts' },
  { path: '/budgets', icon: '🎯', label: 'Budgets' },
  { path: '/reports', icon: '📈', label: 'Financial Reports' }
]

const adminMenuItems = computed(() => {
  const items = [
    { path: '/audit-logs', icon: '🛡️', label: 'Audit Logs' }
  ]
  if (authStore.isAdmin) {
    items.unshift({ path: '/users', icon: '👥', label: 'User Management' })
    items.push({ path: '/settings', icon: '⚡', label: 'Settings' })
  }
  return items
})

const roleName = computed(() => {
  const roles = {
    admin: 'Administrator',
    approver: 'Finance Manager',
    editor: 'Finance Staff',
    viewer: 'Auditor'
  }
  return roles[authStore.userRole] || 'User'
})

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #334155;
  border-radius: 20px;
}

.nav-item {
  @apply flex items-center gap-3 px-4 py-3 text-slate-400 rounded-xl transition-all duration-200 relative overflow-hidden;
}

.nav-item:hover {
  @apply text-slate-200 bg-slate-800/50;
}

.nav-item.active {
  @apply bg-primary-600/10 text-white;
}

.active-indicator {
    @apply absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary-500 rounded-r-full;
}

.icon-wrapper {
    @apply flex items-center justify-center w-6 text-lg;
}
</style>
