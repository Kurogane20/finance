<template>
  <div class="chart-container">
    <div class="chart-header">
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
.chart-body {
  position: relative;
}
</style>
