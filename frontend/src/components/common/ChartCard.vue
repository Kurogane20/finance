<template>
  <div class="card chart-card">
    <div class="card-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-filters" v-if="showFilters">
        <button
          v-for="filter in filters"
          :key="filter.value"
          class="chart-filter-btn"
          :class="{ active: activeFilter === filter.value }"
          @click="$emit('filter-change', filter.value)"
        >
          {{ filter.label }}
        </button>
      </div>
    </div>
    <div class="chart-body" :style="{ height: height }">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  height: { type: String, default: '300px' },
  showFilters: { type: Boolean, default: false },
  filters: { 
    type: Array, 
    default: () => [
      { label: 'Minggu', value: 'week' },
      { label: 'Bulan', value: 'month' },
      { label: 'Tahun', value: 'year' }
    ]
  },
  activeFilter: { type: String, default: 'month' }
})

defineEmits(['filter-change'])
</script>

<style scoped>
.chart-card {
  display: flex;
  flex-direction: column;
}

.card-header {
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.chart-filters {
  display: flex;
  gap: 0.5rem;
  background: rgba(0,0,0,0.1);
  padding: 4px;
  border-radius: 8px;
}

.chart-filter-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.8rem;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.chart-filter-btn:hover {
  color: var(--text-primary);
}

.chart-filter-btn.active {
  background: var(--bg-card);
  color: var(--primary-color);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  font-weight: 500;
}

.chart-body {
  position: relative;
  flex: 1;
}
</style>
