<template>
  <header class="mobile-header">
    <button class="hamburger-btn" @click="$emit('toggle-sidebar')" aria-label="Toggle Menu">
      ☰
    </button>
    <div class="mobile-header-logo">
      <div class="sidebar-logo-icon" style="width: 32px; height: 32px; font-size: 1rem;">💰</div>
      <span style="font-weight: 600; font-size: 0.95rem;">FinanceHub</span>
    </div>
    <div style="width: 44px;"></div> <!-- Spacer for centering -->
  </header>
</template>

<script setup>
defineEmits(['toggle-sidebar'])
</script>
