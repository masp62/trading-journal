<template>
  <div class="dashboard">
    <div v-if="loading" class="loading">Loading analytics...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else>
      <!-- Date Filter -->
      <div class="date-filter">
        <div class="filter-header">
          <h3>📅 Time Period</h3>
          <div class="selected-range">
            {{ formatDateRange() }}
          </div>
        </div>
        
        <div class="filter-controls">
          <div class="preset-buttons">
            <button 
              @click="setPreset('today')" 
              :class="{ active: activePreset === 'today' }"
              class="preset-btn"
            >
              Heute
            </button>
            <button 
              @click="setPreset('7days')" 
              :class="{ active: activePreset === '7days' }"
              class="preset-btn"
            >
              7 Tage
            </button>
            <button 
              @click="setPreset('30days')" 
              :class="{ active: activePreset === '30days' }"
              class="preset-btn"
            >
              30 Tage
            </button>
            <button 
              @click="setPreset('90days')" 
              :class="{ active: activePreset === '90days' }"
              class="preset-btn"
            >
              90 Tage
            </button>
            <button 
              @click="setPreset('ytd')" 
              :class="{ active: activePreset === 'ytd' }"
              class="preset-btn"
            >
              YTD
            </button>
            <button 
              @click="setPreset('all')" 
              :class="{ active: activePreset === 'all' }"
              class="preset-btn"
            >
              Alles
            </button>
          </div>
          
          <div class="custom-range">
            <button 
              @click="toggleCustomRange" 
              :class="{ active: showCustomRange }"
              class="custom-btn"
            >
              📅 Custom
            </button>
            
            <div v-if="showCustomRange" class="custom-inputs">
              <input 
                type="date" 
                v-model="customFromDate"
                @change="applyCustomRange"
                class="date-input"
              />
              <span class="date-separator">bis</span>
              <input 
                type="date" 
                v-model="customToDate"
                @change="applyCustomRange"
                class="date-input"
              />
              <button @click="applyCustomRange" class="apply-btn">✓</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Grid: Links (Tiles + Histogram), Rechts (Instrument) -->
      <div class="main-grid">
        <!-- Linke Spalte: Stats und Histogramm -->
        <div class="left-column">
          <!-- Stats Overview -->
          <div class="stats-grid">
        <div class="stat-card">
          <h3>Total P&L</h3>
          <div class="value" :class="analytics.net_profit >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency(analytics.net_profit) }}
          </div>
        </div>
        
        <div class="stat-card">
          <h3>Win Rate</h3>
          <div class="value" :class="analytics.win_rate >= 0.5 ? 'positive' : 'negative'">
            {{ (analytics.win_rate * 100)?.toFixed(1) }}%
          </div>
        </div>
        
        <div class="stat-card">
          <h3>Total Trades</h3>
          <div class="value">{{ analytics.total_trades }}</div>
        </div>
        
        <div class="stat-card">
          <h3>Winning</h3>
          <div class="value positive">{{ analytics.winning_trades }}</div>
        </div>
        
        <div class="stat-card">
          <h3>Loosing</h3>
          <div class="value negative">{{ analytics.losing_trades }}</div>
        </div>
        
        <div class="stat-card">
          <h3>Avg Win</h3>
          <div class="value positive">{{ formatCurrency(analytics.average_win) }}</div>
        </div>
        
        <div class="stat-card">
          <h3>Avg Loss</h3>
          <div class="value negative">{{ formatCurrency(analytics.average_loss) }}</div>
        </div>
        
        <div class="stat-card">
          <h3>Overnight Fees</h3>
          <div class="value negative">{{ formatCurrency(analytics.total_overnight_fees) }}</div>
        </div>
        
        <div class="stat-card">
          <h3>Net P&L (After Fees)</h3>
          <div class="value" :class="(analytics.net_profit + analytics.total_overnight_fees) >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency((analytics.net_profit || 0) + (analytics.total_overnight_fees || 0)) }}
          </div>
        </div>
          </div>
          
          <!-- Profit Distribution Histogram -->
          <ProfitHistogram :fromDate="fromDate" :toDate="toDate" />
        </div>
        
        <!-- Rechte Spalte: Instrument Stats -->
        <div class="right-column">
          <div class="card instrument-stats" v-if="instrumentStats.length > 0">
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th @click="sortBy('symbol')" class="sortable" :class="{ active: sortKey === 'symbol' }">
                  Symbol
                  <span class="sort-icon" v-if="sortKey === 'symbol'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('total_trades')" class="sortable" :class="{ active: sortKey === 'total_trades' }">
                  Trades
                  <span class="sort-icon" v-if="sortKey === 'total_trades'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('win_rate')" class="sortable" :class="{ active: sortKey === 'win_rate' }">
                  Win Rate
                  <span class="sort-icon" v-if="sortKey === 'win_rate'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('total_pnl')" class="sortable" :class="{ active: sortKey === 'total_pnl' }">
                  Total P/L
                  <span class="sort-icon" v-if="sortKey === 'total_pnl'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('avg_pnl')" class="sortable" :class="{ active: sortKey === 'avg_pnl' }">
                  Avg P/L
                  <span class="sort-icon" v-if="sortKey === 'avg_pnl'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('largest_win')" class="sortable" :class="{ active: sortKey === 'largest_win' }">
                  Best
                  <span class="sort-icon" v-if="sortKey === 'largest_win'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('largest_loss')" class="sortable" :class="{ active: sortKey === 'largest_loss' }">
                  Worst
                  <span class="sort-icon" v-if="sortKey === 'largest_loss'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('overnight_fees')" class="sortable" :class="{ active: sortKey === 'overnight_fees' }">
                  Overnight
                  <span class="sort-icon" v-if="sortKey === 'overnight_fees'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th @click="sortBy('net_total')" class="sortable" :class="{ active: sortKey === 'net_total' }">
                  Net Total
                  <span class="sort-icon" v-if="sortKey === 'net_total'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="instrument in sortedInstrumentStats" :key="instrument.symbol">
                <td class="symbol">{{ instrument.symbol }}</td>
                <td>{{ instrument.total_trades }}</td>
                <td :class="instrument.win_rate >= 0.5 ? 'positive' : 'negative'">
                  {{ (instrument.win_rate * 100).toFixed(1) }}%
                </td>
                <td :class="instrument.total_pnl >= 0 ? 'positive' : 'negative'">
                  {{ formatCurrency(instrument.total_pnl) }}
                </td>
                <td :class="instrument.avg_pnl >= 0 ? 'positive' : 'negative'">
                  {{ formatCurrency(instrument.avg_pnl) }}
                </td>
                <td class="positive">{{ formatCurrency(instrument.largest_win) }}</td>
                <td :class="instrument.largest_loss < 0 ? 'negative' : 'positive'">{{ formatCurrency(instrument.largest_loss) }}</td>
                <td :class="instrument.overnight_fees < 0 ? 'negative' : ''">
                  {{ instrument.overnight_fees !== 0 ? formatCurrency(instrument.overnight_fees) : '-' }}
                </td>
                <td :class="instrument.net_total >= 0 ? 'positive' : 'negative'">
                  <strong>{{ formatCurrency(instrument.net_total) }}</strong>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
        </div>
      </div>
      
      <!-- Period Analytics -->
      <PeriodAnalytics :fromDate="fromDate" :toDate="toDate" />
    </div>
  </div>
</template>

<script>
import api from '@/services/api.js';
import ProfitHistogram from '@/components/ProfitHistogram.vue';
import PeriodAnalytics from '@/components/PeriodAnalytics.vue';

export default {
  name: 'Dashboard',
  components: {
    ProfitHistogram,
    PeriodAnalytics
  },
  data() {
    return {
      analytics: {},
      instrumentStats: [],
      sortKey: 'net_total',
      sortDirection: 'desc',
      loading: true,
      error: null,
      activePreset: 'all',
      showCustomRange: false,
      customFromDate: '',
      customToDate: '',
      fromDate: null,
      toDate: null
    };
  },
  mounted() {
    this.initializeDates();
    this.loadAnalytics();
    this.loadInstrumentStats();
  },
  computed: {
    sortedInstrumentStats() {
      if (!this.instrumentStats || this.instrumentStats.length === 0) return [];
      
      const sorted = [...this.instrumentStats].sort((a, b) => {
        let aVal = a[this.sortKey];
        let bVal = b[this.sortKey];
        
        // Handle null/undefined values
        if (aVal === null || aVal === undefined) aVal = 0;
        if (bVal === null || bVal === undefined) bVal = 0;
        
        // String comparison for symbol
        if (this.sortKey === 'symbol') {
          return this.sortDirection === 'asc' 
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal);
        }
        
        // Numeric comparison
        return this.sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      });
      
      return sorted;
    }
  },
  methods: {
    initializeDates() {
      const now = new Date();
      this.customToDate = now.toISOString().split('T')[0];
      const monthAgo = new Date(now);
      monthAgo.setDate(monthAgo.getDate() - 30);
      this.customFromDate = monthAgo.toISOString().split('T')[0];
    },
    
    setPreset(preset) {
      this.activePreset = preset;
      this.showCustomRange = false;
      
      const now = new Date();
      this.toDate = now.toISOString().split('T')[0];
      let fromDate = new Date(now);
      
      switch (preset) {
        case 'today':
          fromDate = new Date(now);
          break;
        case '7days':
          fromDate.setDate(fromDate.getDate() - 6);
          break;
        case '30days':
          fromDate.setDate(fromDate.getDate() - 29);
          break;
        case '90days':
          fromDate.setDate(fromDate.getDate() - 89);
          break;
        case 'ytd':
          fromDate = new Date(now.getFullYear(), 0, 1);
          break;
        case 'all':
          this.fromDate = null;
          this.toDate = null;
          this.reloadData();
          return;
      }
      
      this.fromDate = fromDate.toISOString().split('T')[0];
      this.reloadData();
    },
    
    toggleCustomRange() {
      this.showCustomRange = !this.showCustomRange;
      if (this.showCustomRange) {
        this.activePreset = 'custom';
      }
    },
    
    applyCustomRange() {
      if (this.customFromDate && this.customToDate) {
        this.activePreset = 'custom';
        this.fromDate = this.customFromDate;
        this.toDate = this.customToDate;
        this.reloadData();
      }
    },
    
    formatDateRange() {
      if (!this.fromDate && !this.toDate) {
        return 'Alle Trades';
      }
      
      const formatDate = (dateStr) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('de-DE', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        });
      };
      
      if (this.fromDate && this.toDate) {
        return `${formatDate(this.fromDate)} - ${formatDate(this.toDate)}`;
      } else if (this.fromDate) {
        return `Ab ${formatDate(this.fromDate)}`;
      } else if (this.toDate) {
        return `Bis ${formatDate(this.toDate)}`;
      }
      
      return 'Alle Trades';
    },
    
    reloadData() {
      this.loadAnalytics();
      this.loadInstrumentStats();
      this.$forceUpdate();
    },
    
    sortBy(key) {
      if (this.sortKey === key) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortKey = key;
        this.sortDirection = key === 'symbol' ? 'asc' : 'desc';
      }
    },
    
    async loadAnalytics() {
      try {
        this.loading = true;
        this.error = null;
        const response = await api.getAnalytics(this.fromDate, this.toDate);
        this.analytics = response.data;
      } catch (err) {
        this.error = 'Failed to load analytics: ' + (err.response?.data?.detail || err.message);
      } finally {
        this.loading = false;
      }
    },
    
    async loadInstrumentStats() {
      try {
        const response = await api.getInstrumentStats(null, this.fromDate, this.toDate);
        this.instrumentStats = response.data.instruments;
      } catch (err) {
        console.error('Failed to load instrument stats:', err);
      }
    },
    
    formatCurrency(value) {
      if (value === null || value === undefined) return '€0.00';
      return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
      }).format(value);
    }
  }
}
</script>

<style scoped>
.date-filter {
  background: var(--bg-secondary);
  padding: 1.5rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.selected-range {
  color: var(--text-secondary);
  font-size: 0.875rem;
  background: var(--bg-tertiary);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  font-weight: 500;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  flex-wrap: wrap;
}

.preset-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 1;
}

.preset-btn {
  padding: 0.625rem 1.25rem;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.preset-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--accent-primary);
}

.preset-btn.active {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
}

.custom-range {
  position: relative;
}

.custom-btn {
  padding: 0.625rem 1.25rem;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.custom-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--accent-primary);
}

.custom-btn.active {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
}

.custom-inputs {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1rem;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 10;
  min-width: 400px;
}

.date-input {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.date-input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
}

.date-separator {
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 600;
}

.apply-btn {
  padding: 0.5rem 1rem;
  background: var(--success);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.apply-btn:hover {
  background: var(--accent-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--bg-secondary);
  padding: 1.25rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.05);
}

.stat-card h3 {
  color: var(--text-muted);
  font-size: 0.75rem;
  margin: 0 0 0.75rem 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.stat-card .value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.dashboard h2 {
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--success));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.75rem;
}

.card h3 {
  color: var(--text-primary);
  font-size: 1.3rem;
  margin-bottom: 1.25rem;
  font-weight: 600;
}

.card p {
  margin: 0.5rem 0;
  font-size: 1rem;
  color: var(--text-secondary);
}

.positive {
  color: var(--success);
  font-weight: 600;
}

.negative {
  color: var(--danger);
  font-weight: 600;
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
  align-items: start;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
}

.left-column .profit-histogram {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.right-column {
  display: flex;
  flex-direction: column;
  height: 100%;
}

@media (max-width: 1200px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

.instrument-stats {
  margin-top: 0;
  margin-bottom: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.instrument-stats .table-container {
  flex: 1;
  overflow-y: auto;
  margin-top: 0;
}

.table-container {
  overflow-x: auto;
  margin-top: 1rem;
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
  padding: 0.85rem;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid var(--border-color);
  color: var(--text-primary);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

th.sortable {
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
  position: relative;
}

th.sortable:hover {
  background-color: var(--bg-hover);
  color: var(--accent-primary);
}

th.sortable.active {
  color: var(--accent-primary);
}

.sort-icon {
  margin-left: 0.25rem;
  font-size: 0.875rem;
  opacity: 0.8;
}

td {
  padding: 0.85rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
}

tbody tr {
  transition: all 0.2s ease;
}

tbody tr:hover {
  background-color: var(--bg-hover);
}

td.symbol {
  font-weight: 700;
  color: var(--accent-primary);
  font-family: 'Courier New', monospace;
}
</style>
