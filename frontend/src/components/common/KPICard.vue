<template>
  <div class="card kpi-card" :style="{ '--card-color': color }">
    <div class="kpi-icon-wrapper">
      <div class="kpi-icon">{{ icon }}</div>
    </div>
    <div class="kpi-content">
      <p class="kpi-label">{{ title }}</p>
      <div class="kpi-value-row">
        <p class="kpi-value">{{ formattedValue }}</p>
        <span class="kpi-change" :class="changeClass">
          {{ changeIcon }} {{ Math.abs(changePercent) }}%
        </span>
      </div>
    </div>
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
  
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(num)
})

const changeClass = computed(() => {
  return props.changeType === 'increase' ? 'positive' : 'negative'
})

const changeIcon = computed(() => {
  return props.changeType === 'increase' ? '↑' : '↓'
})
</script>

<style scoped>
.kpi-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 4px solid var(--card-color);
  overflow: hidden;
  position: relative;
}

.kpi-card::after {
  content: '';
  position: absolute;
  top: 0; right: 0; bottom: 0; left: 0;
  background: linear-gradient(135deg, var(--card-color), transparent);
  opacity: 0.05;
  pointer-events: none;
}

.kpi-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.kpi-content {
  flex: 1;
}

.kpi-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.kpi-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.kpi-change {
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 100px;
  background: rgba(0,0,0,0.2);
  font-weight: 600;
  display: inline-flex;
  align-items: center;
}

.kpi-change.positive {
  color: #10b981;
  background: rgba(16, 185, 129, 0.15);
}

.kpi-change.negative {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.15);
}
</style>
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
