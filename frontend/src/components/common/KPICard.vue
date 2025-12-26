<template>
  <div class="kpi-card" :style="{ '--card-color': color }">
    <div class="kpi-icon" :class="iconClass">{{ icon }}</div>
    <p class="kpi-label">{{ title }}</p>
    <p class="kpi-value">{{ formattedValue }}</p>
    <span class="kpi-change" :class="changeClass">
      {{ changeIcon }} {{ Math.abs(changePercent) }}%
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  value: { type: [Number, String], required: true },
  changePercent: { type: Number, default: 0 },
  changeType: { type: String, default: 'increase' },
  icon: { type: String, default: '📊' },
  color: { type: String, default: '#6366f1' }
})

const formattedValue = computed(() => {
  const num = Number(props.value)
  if (isNaN(num)) return props.value
  
  // Format as Indonesian Rupiah
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(num)
})

const iconClass = computed(() => {
  const colorMap = {
    '#10b981': 'green',
    '#ef4444': 'red',
    '#6366f1': 'purple',
    '#8b5cf6': 'purple',
    '#06b6d4': 'blue'
  }
  return colorMap[props.color] || 'purple'
})

const changeClass = computed(() => {
  return props.changeType === 'increase' ? 'positive' : 'negative'
})

const changeIcon = computed(() => {
  return props.changeType === 'increase' ? '↑' : '↓'
})
</script>
