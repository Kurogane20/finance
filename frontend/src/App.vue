<template>
  <div v-if="isAuthenticated" class="app-container">
    <!-- Sidebar Overlay (mobile only) -->
    <div 
      class="sidebar-overlay" 
      :class="{ active: sidebarOpen }"
      @click="sidebarOpen = false"
    ></div>
    
    <!-- Sidebar -->
    <Sidebar :is-open="sidebarOpen" @close="sidebarOpen = false" />
    
    <main class="main-content">
      <Navbar @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
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
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
