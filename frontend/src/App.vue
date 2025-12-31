<template>
  <div v-if="isAuthenticated" class="min-h-screen bg-slate-50 flex font-sans text-slate-900">
    
    <!-- Sidebar -->
    <Sidebar :is-open="sidebarOpen" @close="sidebarOpen = false" />
    
    <!-- Main Content -->
    <div class="flex-1 flex flex-col md:pl-72 transition-all duration-300 min-h-screen">
      <Navbar @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      
      <main class="flex-1 overflow-x-hidden overflow-y-auto w-full p-6 md:p-8">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
             <div class="max-w-7xl mx-auto">
                <component :is="Component" />
             </div>
          </transition>
        </router-view>
      </main>
    </div>

  </div>
  <router-view v-else />
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/layout/Sidebar.vue'
import Navbar from '@/components/layout/Navbar.vue'

const authStore = useAuthStore()
const route = useRoute()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const sidebarOpen = ref(false)

// Close sidebar on route change (mobile)
watch(() => route.path, () => {
  sidebarOpen.value = false
})

onMounted(() => {
  if (authStore.token) {
    authStore.fetchUser()
  }
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(5px);
}
</style>
