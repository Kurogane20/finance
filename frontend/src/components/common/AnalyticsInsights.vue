<template>
  <div class="analytics-insights">
    <!-- Health Score Card -->
    <div class="health-score-card" v-if="analytics">
      <div class="health-score-header">
        <div class="health-score-circle" :class="healthGradeClass">
          <span class="score-value">{{ analytics.health_score?.score || 0 }}</span>
          <span class="score-label">/ 100</span>
        </div>
        <div class="health-score-info">
          <h3 class="health-title">
            Kesehatan Keuangan
            <span class="health-grade" :class="healthGradeClass">
              {{ analytics.health_score?.grade || '-' }}
            </span>
          </h3>
          <p class="health-summary">{{ analytics.health_score?.summary || 'Memuat...' }}</p>
          <div class="health-trend" :class="trendClass">
            <span class="trend-icon">{{ trendIcon }}</span>
            <span class="trend-text">{{ trendText }}</span>
          </div>
        </div>
      </div>
      
      <!-- Health Factors -->
      <div class="health-factors" v-if="showFactors">
        <div 
          class="factor-item" 
          v-for="factor in analytics.health_score?.factors || []" 
          :key="factor.name"
        >
          <div class="factor-header">
            <span class="factor-name">{{ factor.name }}</span>
            <span class="factor-score" :class="factor.status">
              {{ factor.score }}/{{ factor.max_score }}
            </span>
          </div>
          <div class="factor-bar">
            <div 
              class="factor-progress" 
              :class="factor.status"
              :style="{ width: `${(factor.score / factor.max_score) * 100}%` }"
            ></div>
          </div>
          <p class="factor-desc">{{ factor.description }}</p>
        </div>
      </div>
      
      <button class="toggle-factors-btn" @click="showFactors = !showFactors">
        {{ showFactors ? 'Sembunyikan Detail' : 'Lihat Detail' }}
        <span class="toggle-icon">{{ showFactors ? '▲' : '▼' }}</span>
      </button>
    </div>
    
    <!-- Insights List -->
    <div class="insights-section" v-if="analytics?.insights?.length">
      <h3 class="section-title">
        <span class="title-icon">💡</span>
        Smart Insights
        <span class="insights-count">{{ analytics.insights.length }}</span>
      </h3>
      
      <div class="insights-list">
        <div 
          class="insight-card" 
          v-for="insight in analytics.insights" 
          :key="insight.id"
          :class="[insight.type, `severity-${insight.severity}`]"
          @click="handleInsightClick(insight)"
        >
          <div class="insight-icon" :style="{ backgroundColor: insight.color + '20' }">
            {{ insight.icon }}
          </div>
          <div class="insight-content">
            <h4 class="insight-title">{{ insight.title }}</h4>
            <p class="insight-message">{{ insight.message }}</p>
            <div class="insight-meta" v-if="insight.data">
              <span class="insight-category">{{ formatCategory(insight.category) }}</span>
              <span class="insight-action" v-if="insight.action_url">
                Lihat Detail →
              </span>
            </div>
          </div>
          <div class="insight-severity">
            <span 
              v-for="n in 5" 
              :key="n" 
              class="severity-dot"
              :class="{ active: n <= insight.severity }"
            ></span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div class="empty-insights" v-else-if="!loading">
      <div class="empty-icon">✨</div>
      <h4>Semuanya Baik!</h4>
      <p>Tidak ada insight yang perlu perhatian saat ini.</p>
    </div>
    
    <!-- Data Status -->
    <div class="data-status" v-if="analytics">
      <div class="status-info">
        <span class="status-icon">📊</span>
        <span class="status-text">
          {{ analytics.record_count }} transaksi tercatat
        </span>
      </div>
      <div class="ml-status" :class="{ ready: analytics.ml_ready }">
        <span class="ml-icon">{{ analytics.ml_ready ? '🤖' : '⏳' }}</span>
        <span class="ml-text">
          {{ analytics.ml_ready ? 'ML Predictions Ready' : `ML Ready di ${500 - analytics.record_count} transaksi lagi` }}
        </span>
      </div>
    </div>
    
    <!-- Loading State -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
      <p>Menganalisis data...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const analytics = ref(null)
const loading = ref(true)
const showFactors = ref(false)

const healthGradeClass = computed(() => {
  const grade = analytics.value?.health_score?.grade || 'F'
  if (grade.startsWith('A')) return 'grade-a'
  if (grade === 'B') return 'grade-b'
  if (grade === 'C') return 'grade-c'
  return 'grade-d'
})

const trendClass = computed(() => {
  const trend = analytics.value?.health_score?.trend || 'stable'
  return `trend-${trend}`
})

const trendIcon = computed(() => {
  const trend = analytics.value?.health_score?.trend || 'stable'
  const icons = {
    improving: '📈',
    stable: '➡️',
    declining: '📉'
  }
  return icons[trend] || '➡️'
})

const trendText = computed(() => {
  const trend = analytics.value?.health_score?.trend || 'stable'
  const texts = {
    improving: 'Membaik',
    stable: 'Stabil',
    declining: 'Menurun'
  }
  return texts[trend] || 'Stabil'
})

const formatCategory = (category) => {
  const categories = {
    spending: 'Pengeluaran',
    budget: 'Budget',
    cashflow: 'Arus Kas',
    invoice: 'Invoice',
    revenue: 'Pendapatan'
  }
  return categories[category] || category
}

const handleInsightClick = (insight) => {
  if (insight.action_url) {
    router.push(insight.action_url)
  }
}

const fetchAnalytics = async () => {
  loading.value = true
  try {
    const response = await api.get('/analytics/insights')
    analytics.value = response.data
  } catch (error) {
    // Silent fail - analytics is not critical
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAnalytics()
})

// Expose refresh method
defineExpose({ refresh: fetchAnalytics })
</script>

<style scoped>
.analytics-insights {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

/* Health Score Card */
.health-score-card {
  background: var(--bg-card);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  position: relative;
  overflow: hidden;
}

.health-score-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-success));
}

.health-score-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.health-score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 4px solid currentColor;
  flex-shrink: 0;
}

.health-score-circle.grade-a { color: #10b981; border-color: #10b981; }
.health-score-circle.grade-b { color: #3b82f6; border-color: #3b82f6; }
.health-score-circle.grade-c { color: #f59e0b; border-color: #f59e0b; }
.health-score-circle.grade-d { color: #ef4444; border-color: #ef4444; }

.score-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 0.75rem;
  opacity: 0.7;
}

.health-score-info {
  flex: 1;
}

.health-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.health-grade {
  font-size: 1rem;
  padding: 2px 8px;
  border-radius: var(--radius-md);
  font-weight: 700;
}

.health-grade.grade-a { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.health-grade.grade-b { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.health-grade.grade-c { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.health-grade.grade-d { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

.health-summary {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: var(--spacing-sm);
}

.health-trend {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 0.875rem;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.05);
}

.health-trend.trend-improving { color: #10b981; }
.health-trend.trend-stable { color: #71717a; }
.health-trend.trend-declining { color: #ef4444; }

/* Health Factors */
.health-factors {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--glass-border);
  display: grid;
  gap: var(--spacing-md);
}

.factor-item {
  background: rgba(255, 255, 255, 0.02);
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
}

.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.factor-name {
  font-weight: 500;
}

.factor-score {
  font-weight: 600;
  font-size: 0.875rem;
}

.factor-score.good { color: #10b981; }
.factor-score.warning { color: #f59e0b; }
.factor-score.critical { color: #ef4444; }

.factor-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--spacing-xs);
}

.factor-progress {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.5s ease;
}

.factor-progress.good { background: linear-gradient(90deg, #10b981, #34d399); }
.factor-progress.warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.factor-progress.critical { background: linear-gradient(90deg, #ef4444, #f87171); }

.factor-desc {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.toggle-factors-btn {
  width: 100%;
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  background: transparent;
  border: 1px dashed var(--glass-border);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  transition: all 0.2s ease;
}

.toggle-factors-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

/* Insights Section */
.section-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}

.title-icon {
  font-size: 1.25rem;
}

.insights-count {
  background: var(--color-primary);
  color: white;
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.insight-card {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--bg-card);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.insight-card:hover {
  transform: translateX(4px);
  border-color: var(--color-primary);
}

.insight-card.alert { border-left: 3px solid #ef4444; }
.insight-card.warning { border-left: 3px solid #f59e0b; }
.insight-card.success { border-left: 3px solid #10b981; }
.insight-card.info { border-left: 3px solid #3b82f6; }

.insight-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.insight-content {
  flex: 1;
  min-width: 0;
}

.insight-title {
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 4px;
}

.insight-message {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
}

.insight-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  font-size: 0.75rem;
}

.insight-category {
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.insight-action {
  color: var(--color-primary);
  font-weight: 500;
}

.insight-severity {
  display: flex;
  gap: 3px;
  align-items: center;
}

.severity-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
}

.severity-dot.active {
  background: var(--color-warning);
}

.insight-card.alert .severity-dot.active { background: #ef4444; }
.insight-card.warning .severity-dot.active { background: #f59e0b; }
.insight-card.success .severity-dot.active { background: #10b981; }

/* Empty State */
.empty-insights {
  text-align: center;
  padding: var(--spacing-xl);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--glass-border);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
}

.empty-insights h4 {
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
}

.empty-insights p {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* Data Status */
.data-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-lg);
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.status-info, .ml-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.ml-status.ready {
  color: #10b981;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .health-score-header {
    flex-direction: column;
    text-align: center;
  }
  
  .health-title {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .data-status {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
}
</style>
