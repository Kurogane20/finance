<template>
  <header class="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-6 sticky top-0 z-30">
    <div class="flex items-center gap-4">
      <button 
        class="md:hidden text-slate-500 hover:text-slate-700 focus:outline-none"
        @click="$emit('toggle-sidebar')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      
      <div class="hidden md:flex flex-col">
         <h2 class="text-sm font-bold text-slate-800 leading-tight uppercase tracking-wider">{{ pageTitle }}</h2>
         <span class="text-xs text-slate-400 font-medium">{{ currentDate }}</span>
      </div>
    </div>

    <div class="flex items-center gap-4">
      <button class="relative p-2 text-slate-400 hover:text-slate-600 transition-colors">
        <span class="sr-only">Notifications</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <span class="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
      </button>
      
      <div class="w-px h-8 bg-slate-200 mx-2"></div>
      
      <button 
        @click="handleLogout" 
        class="text-sm font-medium text-slate-600 hover:text-red-600 transition-colors flex items-center gap-2"
      >
        <span>Logout</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

defineEmits(['toggle-sidebar']);

const pageTitles = {
  '/': 'Dashboard',
  '/transactions': 'Transaksi',
  '/journals': 'Jurnal Umum',
  '/invoices': 'Invoice',
  '/accounts': 'Chart of Accounts',
  '/budgets': 'Anggaran',
  '/reports': 'Laporan Keuangan',
  '/users': 'Manajemen User',
  '/audit-logs': 'Audit Logs',
  '/settings': 'Pengaturan',
  '/profile': 'Profil'
};

const pageTitle = computed(() => {
  return pageTitles[route.path] || 'Dashboard';
});

const currentDate = computed(() => {
  return new Date().toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
});

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

