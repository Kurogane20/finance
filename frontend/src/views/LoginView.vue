<template>
  <div class="min-h-screen flex text-slate-800 relative overflow-hidden bg-slate-50">
    
    <!-- Background Elements -->
    <div class="absolute inset-0 z-0">
        <div class="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-primary-600/10 to-transparent"></div>
        <div class="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-primary-400/20 blur-3xl"></div>
        <div class="absolute top-[20%] -right-[10%] w-[40%] h-[40%] rounded-full bg-purple-400/20 blur-3xl"></div>
    </div>

    <div class="relative z-10 w-full max-w-sm mx-auto flex flex-col justify-center px-4">
        
        <div class="mb-8 text-center animate-fade-in-down">
            <div class="mx-auto w-16 h-16 bg-gradient-to-br from-primary-600 to-indigo-700 rounded-xl shadow-xl flex items-center justify-center text-white mb-4 transform rotate-3 hover:rotate-6 transition-transform duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-9 w-9" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            </div>
            <h1 class="text-3xl font-bold tracking-tight text-slate-900">Finance<span class="text-primary-600">OS</span></h1>
            <p class="text-slate-500 mt-2 text-sm">Enterprise Financial Management System</p>
        </div>

        <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/50 p-8 animate-fade-in-up">
            <div v-if="authStore.error" class="mb-6 p-4 rounded-lg bg-red-50 border border-red-100 flex gap-3 text-sm text-red-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <span>{{ authStore.error }}</span>
            </div>

            <form @submit.prevent="handleLogin" class="space-y-5">
                <div>
                   <label class="block text-sm font-semibold text-slate-700 mb-1.5">Work Email</label>
                   <input 
                      v-model="email" 
                      type="email" 
                      class="form-input" 
                      placeholder="name@company.com" 
                      required
                   >
                </div>
                <div>
                   <div class="flex justify-between items-center mb-1.5">
                       <label class="block text-sm font-semibold text-slate-700">Password</label>
                       <!-- <a href="#" class="text-xs text-primary-600 hover:text-primary-700 font-medium">Forgot?</a> -->
                   </div>
                   <input 
                      v-model="password" 
                      type="password" 
                      class="form-input" 
                      placeholder="••••••••" 
                      required
                   >
                </div>

                <button 
                  type="submit" 
                  class="w-full btn btn-primary py-3 text-base shadow-lg hover:shadow-primary-500/25 transition-all"
                  :disabled="authStore.loading"
                >
                    <span v-if="authStore.loading" class="flex items-center gap-2">
                        <svg class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        Authenticating...
                    </span>
                    <span v-else>Sign In</span>
                </button>
            </form>
        </div>

        <div class="mt-8 text-center text-xs text-slate-400">
            &copy; 2025 FinanceOS Inc. Secured by 256-bit Encryption.
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

<style scoped>
.animate-fade-in-down {
    animation: fadeInDown 0.6s ease-out;
}
.animate-fade-in-up {
    animation: fadeInUp 0.6s ease-out 0.1s both;
}

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
