<template>
  <div class="login-container">
    <div class="login-card fade-in">
      <div class="login-header">
        <div class="login-logo">💰</div>
        <h1 class="login-title">Finance Dashboard</h1>
        <p class="login-subtitle">Masuk ke akun Anda</p>
      </div>
      
      <div v-if="authStore.error" class="login-error">
        {{ authStore.error }}
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label class="form-label" for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="form-input"
            placeholder="email@company.com"
            required
            autocomplete="email"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label" for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
            autocomplete="current-password"
          />
        </div>
        
        <button 
          type="submit" 
          class="btn btn-primary login-btn"
          :disabled="authStore.loading"
        >
          {{ authStore.loading ? 'Memproses...' : 'Masuk' }}
        </button>
      </form>
      
      <div class="login-demo">
        <p class="login-demo-title">Demo Accounts:</p>
        <p class="login-demo-accounts">
          <strong>Admin:</strong> admin@company.com / admin123<br>
          <strong>CFO:</strong> cfo@company.com / cfo123<br>
          <strong>Akuntan:</strong> akuntan@company.com / akuntan123
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')

const handleLogin = async () => {
  const success = await authStore.login(email.value, password.value)
  if (success) {
    router.push('/')
  }
}
</script>
