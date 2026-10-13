<template>
  <div class="overnight">
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3>Recent Fees</h3>
        <button @click="downloadCSV" class="btn btn-success">
          Download CSV
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Loading overnight fees...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="card">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Position ID</th>
            <th>Symbol</th>
            <th>Amount</th>
            <th style="width: 1%; text-align: right;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="fee in fees" :key="fee.id">
            <td>{{ formatDate(fee.timestamp) }}</td>
            <td style="font-family: monospace;">
              {{ fee.order_number_name }}
            </td>
            <td><strong>{{ fee.symbol }}</strong></td>
            <td style="color: #e74c3c; font-weight: bold;">
              {{ formatCurrency(fee.interest) }}
            </td>
            <td style="white-space: nowrap;">
              <button @click="viewFeeDetails(fee)" class="btn btn-info" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-right: 0.5rem;">Details</button>
              <button @click="deleteFee(fee)" class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="fees.length === 0" style="text-align: center; padding: 2rem; color: #6c757d;">
        No overnight fees recorded.
      </p>
      
      <!-- Pagination Controls -->
      <div v-if="fees.length > 0" class="pagination-controls">
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
          Zeige {{ fees.length }} Einträge
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
            :disabled="fees.length < pageSize" 
            class="btn">
            Nächste →
          </button>
        </div>
      </div>
      
      <div v-if="fees.length > 0" style="margin-top: 1rem; padding-top: 1rem; border-top: 2px solid #dee2e6;">
        <strong>Total Overnight Fees:</strong>
        <span style="color: #e74c3c; font-size: 1.2rem; margin-left: 1rem;">
          {{ formatCurrency(totalFees) }}
        </span>
      </div>
      
      <!-- Trade Details Modal -->
      <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Fee Details</h3>
            <button @click="closeDetailsModal" class="btn-close">×</button>
          </div>
          <div class="modal-body" v-if="selectedFee">
            <div class="details-grid">
              <div class="detail-item"><span class="detail-label">ID:</span> <span class="detail-value">{{ selectedFee.id }}</span></div>
              <div class="detail-item"><span class="detail-label">Date:</span> <span class="detail-value">{{ formatDate(selectedFee.timestamp) }}</span></div>
              <div class="detail-item"><span class="detail-label">Symbol:</span> <span class="detail-value">{{ selectedFee.symbol }}</span></div>
              <div class="detail-item"><span class="detail-label">Direction:</span> <span class="detail-value">{{ selectedFee.direction }}</span></div>
              <div class="detail-item"><span class="detail-label">Quantity:</span> <span class="detail-value">{{ selectedFee.quantity }}</span></div>
              <div class="detail-item"><span class="detail-label">Interest:</span> <span class="detail-value">{{ formatCurrency(selectedFee.interest) }}</span></div>
              <div class="detail-item"><span class="detail-label">Instrument Currency:</span> <span class="detail-value">{{ selectedFee.instrument_currency }}</span></div>
              <div class="detail-item"><span class="detail-label">Order Number (Name):</span> <span class="detail-value">{{ selectedFee.order_number_name }}</span></div>
              <div class="detail-item"><span class="detail-label">Order Number (ID):</span> <span class="detail-value">{{ selectedFee.order_number_id }}</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop style="max-width: 450px;">
        <div class="modal-header">
          <h3>Overnight Fee löschen?</h3>
          <button @click="closeDeleteModal" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <p style="margin-bottom: 1.5rem; color: var(--text-primary);">
            Möchtest du diesen Overnight Fee wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.
          </p>
          <div v-if="feeToDelete" style="padding: 1rem; background: var(--bg-tertiary); border-radius: var(--radius-sm); margin-bottom: 1.5rem;">
            <strong style="color: var(--text-primary);">{{ feeToDelete.symbol }}</strong><br>
            <span style="color: var(--text-secondary); font-size: 0.9rem;">
              {{ formatCurrency(feeToDelete.interest) }} • {{ formatDate(feeToDelete.timestamp) }}
            </span>
          </div>
          <div style="display: flex; gap: 1rem; justify-content: flex-end;">
            <button @click="closeDeleteModal" class="btn" style="background: var(--bg-tertiary); border: 1px solid var(--border-color);">
              Abbrechen
            </button>
            <button @click="confirmDelete" class="btn btn-danger">
              Löschen
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.js'

export default {
  name: 'OvernightFees',
  data() {
    return {
      fees: [],
      currentPage: 1,
      pageSize: 10,
      loading: true,
      error: null,
      showDetailsModal: false,
      showDeleteModal: false,
      selectedFee: null,
      feeToDelete: null,
    }
  },
  computed: {
    totalFees() {
      return this.fees.reduce((sum, fee) => sum + (fee.interest || 0), 0)
    }
  },
  mounted() {
    this.loadFees()
    window.addEventListener('keydown', this.handleEscKey)
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleEscKey)
  },
  methods: {
    handleEscKey(event) {
      if (event.key === 'Escape') {
        if (this.showDetailsModal) {
          this.closeDetailsModal()
        } else if (this.showDeleteModal) {
          this.closeDeleteModal()
        }
      }
    },
    viewFeeDetails(fee) {
      this.selectedFee = fee
      this.showDetailsModal = true
    },
    closeDetailsModal() {
      this.showDetailsModal = false
      this.selectedFee = null
    },
    closeDeleteModal() {
      this.showDeleteModal = false
      this.feeToDelete = null
    },
    deleteFee(fee) {
      this.feeToDelete = fee
      this.showDeleteModal = true
    },
    async confirmDelete() {
      if (!this.feeToDelete) return
      
      try {
        await api.deleteOvernightFee(this.feeToDelete.id)
        this.closeDeleteModal()
        await this.loadFees()
      } catch (err) {
        console.error('Delete fee error:', err)
        this.closeDeleteModal()
        alert('Failed to delete fee: ' + (err.response?.data?.detail || err.message))
      }
    },
    async loadFees() {
      try {
        this.loading = true
        this.error = null
        
        // Calculate offset for pagination
        const offset = (this.currentPage - 1) * this.pageSize
        
        const response = await api.getOvernightFees(this.pageSize, false, offset)
        this.fees = response.data.sort((a, b) => {
          const dateA = new Date(a.timestamp || 0)
          const dateB = new Date(b.timestamp || 0)
          return dateB.getTime() - dateA.getTime()
        })
      } catch (err) {
        console.error('Overnight fees error:', err)
        this.error = 'Failed to load overnight fees: ' + (err.response?.data?.detail || err.message || JSON.stringify(err))
      } finally {
        this.loading = false
      }
    },
    changePageSize() {
      this.currentPage = 1
      this.loadFees()
    },
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.loadFees()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    nextPage() {
      if (this.fees.length === this.pageSize) {
        this.currentPage++
        this.loadFees()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    async downloadCSV() {
      try {
        const response = await api.getOvernightFees(1000, true)
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `overnight_fees_${new Date().toISOString().split('T')[0]}.csv`
        a.click()
      } catch (err) {
        alert('Failed to download CSV: ' + err.message)
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
    }
  }
}
</script>
<style scoped>
.overnight {
  /* Remove max-width to use full container width like trades */
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.75rem;
  margin-bottom: 1.5rem;
}

.loading, .error {
  padding: 2rem;
  text-align: center;
  border-radius: var(--radius-md);
}

.error {
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger);
}

table {
  width: 100%;
  border-collapse: collapse;
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

.btn {
  padding: 0.5rem 1rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
}

.btn-success {
  background: var(--success);
  color: white;
  border-color: var(--success);
}

.btn-success:hover {
  opacity: 0.9;
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

.position-link:hover {
  text-decoration: none;
  opacity: 0.8;
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