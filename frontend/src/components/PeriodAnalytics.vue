<template>
  <div class="period-analytics">
    <div class="header">
      <h3>Statistics</h3>
      <div class="controls">
        <select v-model="selectedPeriod" @change="fetchData" class="period-select">
          <option value="day">Daily</option>
          <option value="week">Weekly</option>
          <option value="month">Monthly</option>
          <option value="year">Yearly</option>
        </select>
        <select v-model="limit" @change="fetchData" class="limit-select">
          <option :value="10">10 periods</option>
          <option :value="20">20 periods</option>
          <option :value="50">50 periods</option>
        </select>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else>
      <!-- Summary Stats -->
      <div v-if="summary" class="summary-cards">
        <div class="summary-card">
          <span class="label">Total Trades</span>
          <span class="value">{{ summary.total_trades }}</span>
        </div>
        <div class="summary-card">
          <span class="label">Total P/L</span>
          <span class="value" :class="summary.total_pnl >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency(summary.total_pnl) }}
          </span>
        </div>
        <div class="summary-card">
          <span class="label">Overnight Fees</span>
          <span class="value negative">{{ formatCurrency(summary.total_overnight_fees) }}</span>
        </div>
        <div class="summary-card">
          <span class="label">Net Combined</span>
          <span class="value" :class="summary.total_combined >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency(summary.total_combined) }}
          </span>
        </div>
        <div class="summary-card">
          <span class="label">Target</span>
          <span class="value">{{ formatCurrency(summary.total_target) }}</span>
        </div>
        <div class="summary-card">
          <span class="label">Deviation</span>
          <span class="value" :class="summary.total_deviation >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency(summary.total_deviation) }}
          </span>
        </div>
      </div>

      <!-- Period Table -->
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Period</th>
              <th>Trades</th>
              <th>Total P/L</th>
              <th>Avg P/L</th>
              <th>Overnight</th>
              <th>Total</th>
              <th>Target</th>
              <th>Deviation</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(period, index) in periods" :key="index">
              <td class="period-date">{{ period.period }}</td>
              <td>{{ period.trade_count }}</td>
              <td :class="period.total_pnl >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(period.total_pnl) }}
              </td>
              <td :class="period.avg_pnl >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(period.avg_pnl) }}
              </td>
              <td :class="period.overnight_fees < 0 ? 'negative' : ''">
                {{ formatCurrency(period.overnight_fees) }}
              </td>
              <td :class="(period.total_pnl + period.overnight_fees) >= 0 ? 'positive' : 'negative'">
                <strong>{{ formatCurrency(period.total_pnl + period.overnight_fees) }}</strong>
              </td>
              <td class="target">{{ formatCurrency(period.target_profit) }}</td>
              <td :class="period.deviation_from_target >= 0 ? 'positive' : 'negative'">
                <strong>{{ formatCurrency(period.deviation_from_target) }}</strong>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'

export default {
  name: 'PeriodAnalytics',
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const selectedPeriod = ref('week')
    const limit = ref(10)
    const periods = ref([])
    const summary = ref(null)

    const fetchData = async () => {
      try {
        loading.value = true
        error.value = null
        const response = await api.getPeriodStats(selectedPeriod.value, limit.value)
        periods.value = response.data.periods
        summary.value = response.data.summary
      } catch (err) {
        console.error('Error fetching period stats:', err)
        error.value = 'Failed to load period analytics'
      } finally {
        loading.value = false
      }
    }

    const formatCurrency = (value) => {
      if (value === null || value === undefined) return '€0.00'
      return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
      }).format(value)
    }

    onMounted(() => {
      fetchData()
    })

    return {
      loading,
      error,
      selectedPeriod,
      limit,
      periods,
      summary,
      fetchData,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.period-analytics {
  background: var(--bg-secondary);
  padding: 1.5rem;
  border-radius: var(--radius-md);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.controls {
  display: flex;
  gap: 0.75rem;
}

.period-select,
.limit-select {
  padding: 0.5rem 0.75rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.period-select:hover,
.limit-select:hover {
  border-color: var(--accent-primary);
}

.period-select:focus,
.limit-select:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.summary-card {
  background: var(--bg-tertiary);
  padding: 1rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-card .label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.summary-card .value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.table-container {
  overflow-x: auto;
  border-radius: var(--radius-md);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

thead {
  background-color: var(--bg-tertiary);
}

th {
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid var(--border-color);
  color: var(--text-primary);
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.5px;
}

td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
}

tbody tr {
  transition: all 0.2s ease;
}

tbody tr:hover {
  background-color: var(--bg-hover);
}

.period-date {
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'Courier New', monospace;
}

.positive {
  color: var(--success);
  font-weight: 600;
}

.negative {
  color: var(--danger);
  font-weight: 600;
}

.loading, .error {
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
}

.error {
  color: var(--danger);
}
</style>
