<template>
  <div class="trades">
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3>Recent Trades</h3>
        <div>
          <button @click="showFilters = !showFilters" class="btn" :class="hasActiveFilters ? 'btn-primary' : ''" style="margin-right: 0.5rem;">
            {{ showFilters ? '✕ Hide Filters' : '🔍 Filters' }}
            <span v-if="hasActiveFilters" style="margin-left: 0.3rem; background: var(--success); padding: 0.1rem 0.4rem; border-radius: 10px; font-size: 0.7rem;">{{ activeFilterCount }}</span>
          </button>
          <button @click="showAddForm = !showAddForm" class="btn btn-primary">
            {{ showAddForm ? 'Cancel' : '+ Add Trade' }}
          </button>
          <button @click="downloadCSV" class="btn btn-success" style="margin-left: 0.5rem;">
            Download CSV
          </button>
        </div>
      </div>
      
      <!-- Filter Panel -->
      <div v-if="showFilters" class="filter-panel">
        <h4>Filter Trades</h4>
        <div class="filter-grid">
          <div class="form-group">
            <label>Symbol</label>
            <input v-model="filters.symbol" @input="debouncedApplyFilters" placeholder="z.B. Tech, Germany40" />
          </div>
          
          <div class="form-group">
            <label>Action</label>
            <select v-model="filters.action" @change="applyFilters">
              <option value="">Alle</option>
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Von Datum</label>
            <input v-model="filters.from_date" @change="applyFilters" type="date" />
          </div>
          
          <div class="form-group">
            <label>Bis Datum</label>
            <input v-model="filters.to_date" @change="applyFilters" type="date" />
          </div>
          
          <div class="form-group">
            <label>Min. Gewinn (€)</label>
            <input v-model.number="filters.min_profit" @input="debouncedApplyFilters" type="number" step="0.01" placeholder="z.B. 0" />
          </div>
        </div>
        
        <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
          <button @click="resetFilters" class="btn">Reset Filter</button>
          <span v-if="hasActiveFilters" style="color: var(--text-secondary); font-size: 0.9rem; line-height: 2.5;">
            {{ filteredCount }} von {{ totalCount }} Trades
          </span>
        </div>
      </div>
      
      <div v-if="showAddForm" class="card" style="background: var(--bg-tertiary); border: 1px solid var(--border-color);">
        <h4>Add New Trade</h4>
        <form @submit.prevent="addTrade">
          <div class="form-group">
            <label>Symbol *</label>
            <input v-model="newTrade.symbol" required />
          </div>
          <div class="form-group">
            <label>Type *</label>
            <select v-model="newTrade.type" required>
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </div>
          <div class="form-group">
            <label>Quantity *</label>
            <input v-model.number="newTrade.quantity" type="number" step="0.01" required />
          </div>
          <div class="form-group">
            <label>Entry Price *</label>
            <input v-model.number="newTrade.entry_price" type="number" step="0.01" required />
          </div>
          <div class="form-group">
            <label>Exit Price *</label>
            <input v-model.number="newTrade.exit_price" type="number" step="0.01" required />
          </div>
          <div class="form-group">
            <label>Entry Date (YYYY-MM-DD HH:MM:SS)</label>
            <input v-model="newTrade.entry_date" placeholder="2026-01-28 10:30:00" />
          </div>
          <div class="form-group">
            <label>Exit Date (YYYY-MM-DD HH:MM:SS)</label>
            <input v-model="newTrade.exit_date" placeholder="2026-01-28 15:45:00" />
          </div>
          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="newTrade.notes"></textarea>
          </div>
          <button type="submit" class="btn btn-success">Add Trade</button>
        </form>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Loading trades...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="card">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Order Number</th>
            <th>Symbol</th>
            <th>Type</th>
            <th>Qty</th>
            <th>Entry</th>
            <th>Exit</th>
            <th>P&L</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trade in trades" :key="trade.id">
            <td>{{ formatDate(trade.timestamp) }}</td>
            <td><span style="font-family: monospace; font-size: 0.85em;">{{ trade.order_number_name || '-' }}</span></td>
            <td><strong>{{ trade.symbol }}</strong></td>
            <td>
              <span :style="{ color: trade.action === 'BUY' ? '#2ecc71' : '#e74c3c' }">
                {{ trade.action }}
              </span>
            </td>
            <td>{{ trade.quantity }}</td>
            <td>{{ formatCurrency(trade.price) }}</td>
            <td>{{ formatCurrency(trade.close_price) }}</td>
            <td :style="{ color: trade.result_after_fx_fee >= 0 ? '#2ecc71' : '#e74c3c', fontWeight: 'bold' }">
              {{ formatCurrency(trade.result_after_fx_fee) }}
            </td>
            <td>
              <button @click="viewTradeDetails(trade)" class="btn btn-info" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-right: 0.5rem;">
                Details
              </button>
              <button @click="deleteTrade(trade)" class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="trades.length === 0" style="text-align: center; padding: 2rem; color: var(--text-muted);">
        No trades found. Add your first trade above!
      </p>
      
      <!-- Trade Details Modal -->
      <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Trade Details</h3>
            <button @click="closeDetailsModal" class="btn-close">×</button>
          </div>
          <div class="modal-body" v-if="selectedTrade">
            <div class="details-grid">
              <div class="detail-item">
                <span class="detail-label">ID:</span>
                <span class="detail-value">{{ selectedTrade.id }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Symbol:</span>
                <span class="detail-value"><strong>{{ selectedTrade.symbol }}</strong></span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Action:</span>
                <span class="detail-value" :style="{ color: selectedTrade.action === 'BUY' ? '#2ecc71' : '#e74c3c' }">
                  <strong>{{ selectedTrade.action }}</strong>
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Date:</span>
                <span class="detail-value">{{ formatDate(selectedTrade.timestamp) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Quantity:</span>
                <span class="detail-value">{{ selectedTrade.quantity }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Entry Price:</span>
                <span class="detail-value">{{ formatCurrency(selectedTrade.price) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Exit Price:</span>
                <span class="detail-value">{{ formatCurrency(selectedTrade.close_price) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Result (Gross):</span>
                <span class="detail-value" :style="{ color: selectedTrade.result_gross >= 0 ? '#2ecc71' : '#e74c3c' }">
                  {{ formatCurrency(selectedTrade.result_gross) }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Result (Net):</span>
                <span class="detail-value" :style="{ color: selectedTrade.result_net >= 0 ? '#2ecc71' : '#e74c3c' }">
                  {{ formatCurrency(selectedTrade.result_net) }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">FX Fee:</span>
                <span class="detail-value">{{ formatCurrency(selectedTrade.fx_fee) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Result (After FX Fee):</span>
                <span class="detail-value" :style="{ color: selectedTrade.result_after_fx_fee >= 0 ? '#2ecc71' : '#e74c3c', fontWeight: 'bold' }">
                  {{ formatCurrency(selectedTrade.result_after_fx_fee) }}
                </span>
              </div>
              <div class="detail-item" v-if="selectedTrade.realised_profit_loss_account_currency !== null">
                <span class="detail-label">Realised P/L (Account):</span>
                <span class="detail-value">{{ formatCurrency(selectedTrade.realised_profit_loss_account_currency) }}</span>
              </div>
              <div class="detail-item" v-if="selectedTrade.realised_profit_loss_instrument_currency !== null">
                <span class="detail-label">Realised P/L (Instrument):</span>
                <span class="detail-value">{{ formatCurrency(selectedTrade.realised_profit_loss_instrument_currency) }}</span>
              </div>
              <div class="detail-item" v-if="selectedTrade.instrument_currency">
                <span class="detail-label">Instrument Currency:</span>
                <span class="detail-value">{{ selectedTrade.instrument_currency }}</span>
              </div>
              <div class="detail-item" v-if="selectedTrade.net_result_account_currency !== null">
                <span class="detail-label">Net Result (Account):</span>
                <span class="detail-value" :style="{ color: selectedTrade.net_result_account_currency >= 0 ? '#2ecc71' : '#e74c3c' }">
                  {{ formatCurrency(selectedTrade.net_result_account_currency) }}
                </span>
              </div>
              <div class="detail-item" v-if="selectedTrade.event_type">
                <span class="detail-label">Event Type:</span>
                <span class="detail-value">{{ selectedTrade.event_type }}</span>
              </div>
              <div class="detail-item" v-if="selectedTrade.event_number">
                <span class="detail-label">Event Number:</span>
                <span class="detail-value">{{ selectedTrade.event_number }}</span>
              </div>
              <div class="detail-item" v-if="selectedTrade.order_number_name">
                <span class="detail-label">Order Number (Name):</span>
                <span class="detail-value" style="font-family: monospace;">{{ selectedTrade.order_number_name }}</span>
              </div>
              <div class="detail-item" v-if="selectedTrade.order_number_id">
                <span class="detail-label">Order Number (ID):</span>
                <span class="detail-value" style="font-family: monospace;">{{ selectedTrade.order_number_id }}</span>
              </div>
              <div class="detail-item full-width" v-if="selectedTrade.notes">
                <span class="detail-label">Notes:</span>
                <span class="detail-value">{{ selectedTrade.notes }}</span>
              </div>
              <div class="detail-item" v-if="selectedTrade.created_at">
                <span class="detail-label">Created At:</span>
                <span class="detail-value">{{ formatDate(selectedTrade.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Pagination Controls -->
      <div v-if="trades.length > 0" class="pagination-controls">
        <div class="page-size-selector">
          <label>Einträge pro Seite:</label>
          <select v-model.number="pageSize" @change="changePageSize">
            <option :value="10">10</option>
            <option :value="25">25</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>
        
        <div class="pagination-info">
          Zeige {{ trades.length }} Einträge
          <span v-if="hasActiveFilters"> ({{ filteredCount }} von {{ totalCount }} gesamt)</span>
        </div>
        
        <div class="pagination-buttons">
          <button 
            @click="previousPage" 
            :disabled="currentPage === 1" 
            class="btn"
            style="margin-right: 0.5rem;">
            ← Vorherige
          </button>
          <span style="margin: 0 1rem; color: var(--text-secondary);">Seite {{ currentPage }}</span>
          <button 
            @click="nextPage" 
            :disabled="trades.length < pageSize" 
            class="btn">
            Nächste →
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Trade löschen?</h3>
          <button @click="closeDeleteModal" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <p style="color: var(--text-secondary); margin-bottom: 1rem;">
            Diese Aktion kann nicht rückgängig gemacht werden.
          </p>
          <div v-if="tradeToDelete" style="padding: 1rem; background: var(--bg-secondary); border-radius: 4px; margin-bottom: 1rem;">
            <p><strong>Symbol:</strong> {{ tradeToDelete.symbol }}</p>
            <p><strong>P&L (nach Gebühren):</strong> 
              <span :style="{ color: tradeToDelete.result_after_fx_fee >= 0 ? 'var(--success-color)' : 'var(--danger-color)' }">
                {{ tradeToDelete.result_after_fx_fee >= 0 ? '+' : '' }}{{ tradeToDelete.result_after_fx_fee?.toFixed(2) }} {{ tradeToDelete.currency || 'EUR' }}
              </span>
            </p>
            <p><strong>Datum:</strong> {{ formatDate(tradeToDelete.timestamp) }}</p>
          </div>
          <div style="display: flex; gap: 1rem; justify-content: flex-end;">
            <button @click="closeDeleteModal" class="btn">Abbrechen</button>
            <button @click="confirmDelete" class="btn btn-danger">Löschen</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.js'

export default {
  name: 'Trades',
  data() {
    return {
      trades: [],
      loading: true,
      error: null,
      showAddForm: false,
      showFilters: false,
      showDetailsModal: false,
      showOvernightModal: false,
      showDeleteModal: false,
      selectedTrade: null,
      tradeToDelete: null,
      overnightFees: [],
      overnightSum: 0,
      newTrade: this.getEmptyTrade(),
      filters: {
        symbol: '',
        action: '',
        from_date: '',
        to_date: '',
        min_profit: null
      },
      filteredCount: 0,
      totalCount: 0,
      debounceTimer: null,
      currentPage: 1,
      pageSize: 10
    }
  },
  computed: {
    hasActiveFilters() {
      return this.filters.symbol || this.filters.action || this.filters.from_date || 
             this.filters.to_date || this.filters.min_profit !== null
    },
    activeFilterCount() {
      let count = 0
      if (this.filters.symbol) count++
      if (this.filters.action) count++
      if (this.filters.from_date) count++
      if (this.filters.to_date) count++
      if (this.filters.min_profit !== null) count++
      return count
    }
  },
  mounted() {
    this.loadTrades()
    window.addEventListener('keydown', this.handleEscKey)
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleEscKey)
  },
  methods: {
    handleEscKey(event) {
      if (event.key === 'Escape') {
        if (this.showDeleteModal) {
          this.closeDeleteModal();
        }
        if (this.showDetailsModal) {
          this.closeDetailsModal();
        }
        if (this.showOvernightModal) {
          this.closeOvernightModal();
        }
      }
    },
    async loadTrades() {
      try {
        this.loading = true
        this.error = null
        
        // Build filter object for API
        const apiFilters = {}
        if (this.filters.symbol && this.filters.symbol.trim()) apiFilters.symbol = this.filters.symbol.trim()
        if (this.filters.action && this.filters.action.trim()) apiFilters.action = this.filters.action.trim()
        if (this.filters.from_date && this.filters.from_date.trim()) apiFilters.from_date = this.filters.from_date.trim()
        if (this.filters.to_date && this.filters.to_date.trim()) apiFilters.to_date = this.filters.to_date.trim()
        if (this.filters.min_profit !== null && this.filters.min_profit !== '' && !isNaN(this.filters.min_profit)) {
          apiFilters.min_profit = this.filters.min_profit
        }
        
        console.log('Loading trades with filters:', apiFilters, 'Page:', this.currentPage, 'PageSize:', this.pageSize)
        
        // Calculate offset for pagination
        const offset = (this.currentPage - 1) * this.pageSize
        
        const response = await api.getTrades(this.pageSize, false, apiFilters, offset)
        this.trades = response.data.sort((a, b) => {
          const dateA = new Date(a.timestamp || a.opening_time || 0)
          const dateB = new Date(b.timestamp || b.opening_time || 0)
          return dateB.getTime() - dateA.getTime()
        })
        
        // Show current result count
        this.filteredCount = this.trades.length
        this.totalCount = this.trades.length
      } catch (err) {
        console.error('Error loading trades:', err)
        let errorMsg = 'Failed to load trades: '
        if (err.response?.data?.detail) {
          errorMsg += err.response.data.detail
        } else if (err.response?.data) {
          errorMsg += JSON.stringify(err.response.data)
        } else if (err.message) {
          errorMsg += err.message
        } else {
          errorMsg += 'Unknown error'
        }
        this.error = errorMsg
      } finally {
        this.loading = false
      }
    },
    applyFilters() {
      this.loadTrades()
    },
    debouncedApplyFilters() {
      // Clear existing timer
      if (this.debounceTimer) {
        clearTimeout(this.debounceTimer)
      }
      
      // Set new timer to apply filters after 500ms of no input
      this.debounceTimer = setTimeout(() => {
        this.loadTrades()
      }, 500)
    },
    resetFilters() {
      this.filters = {
        symbol: '',
        action: '',
        from_date: '',
        to_date: '',
        min_profit: null
      }
      this.currentPage = 1
      this.loadTrades()
    },
    changePageSize() {
      this.currentPage = 1
      this.loadTrades()
    },
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.loadTrades()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    nextPage() {
      if (this.trades.length === this.pageSize) {
        this.currentPage++
        this.loadTrades()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    viewTradeDetails(trade) {
      this.selectedTrade = trade
      this.showDetailsModal = true
    },
    closeDetailsModal() {
      this.showDetailsModal = false
      this.selectedTrade = null
    },
    async addTrade() {
      try {
        await api.createTrade(this.newTrade)
        this.showAddForm = false
        this.newTrade = this.getEmptyTrade()
        await this.loadTrades()
      } catch (err) {
        alert('Failed to add trade: ' + (err.response?.data?.detail || err.message))
      }
    },
    deleteTrade(trade) {
      this.tradeToDelete = trade;
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (!this.tradeToDelete) return;
      
      try {
        await api.deleteTrade(this.tradeToDelete.id);
        this.closeDeleteModal();
        await this.loadTrades();
      } catch (err) {
        alert('Failed to delete trade: ' + (err.response?.data?.detail || err.message));
        this.closeDeleteModal();
      }
    },
    closeDeleteModal() {
      this.showDeleteModal = false;
      this.tradeToDelete = null;
    },
    async downloadCSV() {
      try {
        const response = await api.getTrades(1000, true)
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `trades_${new Date().toISOString().split('T')[0]}.csv`
        a.click()
      } catch (err) {
        alert('Failed to download CSV: ' + err.message)
      }
    },
    getEmptyTrade() {
      return {
        symbol: '',
        type: 'BUY',
        quantity: null,
        entry_price: null,
        exit_price: null,
        entry_date: '',
        exit_date: '',
        notes: ''
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString('de-DE')
    },
    formatCurrency(value) {
      if (value === null || value === undefined) return '€0.00'
      return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
      }).format(value)
    },
    async showOvernightFees(trade) {
      try {
        this.showOvernightModal = true;
        this.overnightFees = [];
        this.overnightSum = 0;
        if (!trade.order_number_name) return;
        const response = await api.getOvernightFeesForTrade(trade.order_number_name);
        this.overnightFees = response.data;
        console.log('OvernightFees API response:', response.data);
        this.overnightSum = this.overnightFees.reduce((sum, fee) => sum + (fee.interest || 0), 0);
      } catch (err) {
        this.overnightFees = [];
        this.overnightSum = 0;
      }
    },
      isSameDay(opening, closing) {
        if (!opening || !closing) return false;
        const openDate = new Date(opening);
        const closeDate = new Date(closing);
        return openDate.getFullYear() === closeDate.getFullYear() &&
          openDate.getMonth() === closeDate.getMonth() &&
          openDate.getDate() === closeDate.getDate();
      },
    closeOvernightModal() {
      this.showOvernightModal = false;
      this.overnightFees = [];
      this.overnightSum = 0;
    }
  }
}
</script>

<style scoped>
.trades h2 {
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--success));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.filter-panel {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.filter-panel h4 {
  margin-bottom: 1rem;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-grid .form-group {
  margin-bottom: 0;
}

.filter-grid input,
.filter-grid select {
  font-size: 0.9rem;
}

table {
  font-size: 0.9rem;
}

th {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}

td {
  color: var(--text-secondary);
}

td strong {
  color: var(--accent-primary);
  font-family: 'Courier New', monospace;
}

th:last-child,
td:last-child {
  width: 140px;
  text-align: right;
  white-space: nowrap;
}

td:last-child {
  padding-right: 1rem;
}

tbody tr:hover {
  background-color: var(--bg-hover);
}

.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding: 1rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-size-selector label {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

.page-size-selector select {
  padding: 0.4rem 0.8rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  cursor: pointer;
}

.pagination-info {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.pagination-buttons {
  display: flex;
  align-items: center;
}

.pagination-buttons button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 2rem;
  overflow-y: auto;
}

.modal-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.detail-value {
  font-size: 1rem;
  color: var(--text-primary);
  word-break: break-word;
}

.btn-danger {
  background: var(--danger);
  color: white;
  border-color: var(--danger);
}

.btn-danger:hover {
  background: #ff6b6b;
  border-color: #ff6b6b;
}

.btn-info {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.btn-info:hover {
  opacity: 0.9;
}

.btn-info:disabled {
  background: #cccccc !important;
  color: #888888 !important;
  border-color: #cccccc !important;
  cursor: not-allowed !important;
  opacity: 0.7;
}

@media (max-width: 768px) {
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-overlay {
    padding: 1rem;
  }
}
</style>
