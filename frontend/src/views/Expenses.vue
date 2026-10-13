<template>
  <div class="expenses">
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3>Trading Expenses & Subscriptions</h3>
        <div>
          <button @click="showAddForm = !showAddForm" class="btn btn-primary">
            {{ showAddForm ? 'Cancel' : '+ Add Expense' }}
          </button>
          <button @click="downloadCSV" class="btn btn-success" style="margin-left: 0.5rem;">
            Download CSV
          </button>
        </div>
      </div>
      
      <div v-if="showAddForm" class="card" style="background: var(--bg-tertiary); border: 1px solid var(--border-color); margin-top: 1rem;">
        <h4>Add New Expense</h4>
        <form @submit.prevent="addExpense" class="expense-form">
          <div class="form-row">
            <div class="form-group">
              <label>Name *</label>
              <input 
                v-model="newExpense.name" 
                type="text" 
                required 
                maxlength="200"
                placeholder="e.g., TradingView Pro" />
            </div>
            
            <div class="form-group">
              <label>Category</label>
              <input 
                v-model="newExpense.category" 
                type="text" 
                maxlength="100"
                placeholder="e.g., Subscription, Data Feed, Broker" />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Purchase Date *</label>
              <input 
                v-model="newExpense.purchase_date" 
                type="date" 
                required />
            </div>
            
            <div class="form-group">
              <label>Expiry Date *</label>
              <input 
                v-model="newExpense.expiry_date" 
                type="date" 
                required />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Price *</label>
              <input 
                v-model.number="newExpense.price" 
                type="number" 
                step="0.01" 
                min="0.01"
                required 
                placeholder="0.00" />
            </div>
            
            <div class="form-group">
              <label>Currency</label>
              <select v-model="newExpense.currency">
                <option value="EUR">EUR (€)</option>
                <option value="USD">USD ($)</option>
                <option value="CHF">CHF (Fr)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>Notes</label>
            <textarea 
              v-model="newExpense.notes" 
              rows="3" 
              maxlength="500"
              placeholder="Additional information..."></textarea>
          </div>
          
          <button type="submit" class="btn btn-success">
            Add Expense
          </button>
        </form>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Loading expenses...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="card">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Purchase Date</th>
            <th>Expiry Date</th>
            <th>Price</th>
            <th style="width: 1%; text-align: right;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="expense in expenses" 
            :key="expense.id"
            :class="{ 'expiring-soon': isExpiringSoon(expense.expiry_date) }">
            <td><strong>{{ expense.name }}</strong></td>
            <td>{{ expense.category || '-' }}</td>
            <td>{{ formatDate(expense.purchase_date) }}</td>
            <td>
              {{ formatDate(expense.expiry_date) }}
              <span v-if="isExpiringSoon(expense.expiry_date)" class="warning-badge">
                ⚠️ Expiring soon
              </span>
            </td>
            <td style="font-weight: bold;">
              {{ formatCurrency(expense.price, expense.currency) }}
            </td>
            <td style="white-space: nowrap;">
              <button @click="viewDetails(expense)" class="btn btn-info" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-right: 0.5rem;">Details</button>
              <button @click="deleteExpense(expense)" class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="expenses.length === 0" style="text-align: center; padding: 2rem; color: #6c757d;">
        No expenses recorded yet. Add your first expense above.
      </p>
      
      <!-- Pagination Controls -->
      <div v-if="expenses.length > 0" class="pagination-controls">
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
          Zeige {{ expenses.length }} Einträge
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
            :disabled="expenses.length < pageSize" 
            class="btn">
            Nächste →
          </button>
        </div>
      </div>
      
      <div v-if="expenses.length > 0" style="margin-top: 1rem; padding-top: 1rem; border-top: 2px solid #dee2e6;">
        <strong>Total Expenses (all currencies):</strong>
        <span style="font-size: 1.2rem; margin-left: 1rem;">
          {{ calculateTotalByCurrency() }}
        </span>
      </div>
      
      <!-- Expense Details Modal -->
      <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Expense Details</h3>
            <button @click="closeDetailsModal" class="btn-close">×</button>
          </div>
          <div class="modal-body" v-if="selectedExpense">
            <div class="details-grid">
              <div class="detail-item"><span class="detail-label">ID:</span> <span class="detail-value">{{ selectedExpense.id }}</span></div>
              <div class="detail-item"><span class="detail-label">Name:</span> <span class="detail-value">{{ selectedExpense.name }}</span></div>
              <div class="detail-item"><span class="detail-label">Category:</span> <span class="detail-value">{{ selectedExpense.category || '-' }}</span></div>
              <div class="detail-item"><span class="detail-label">Purchase Date:</span> <span class="detail-value">{{ formatDate(selectedExpense.purchase_date) }}</span></div>
              <div class="detail-item"><span class="detail-label">Expiry Date:</span> <span class="detail-value">{{ formatDate(selectedExpense.expiry_date) }}</span></div>
              <div class="detail-item"><span class="detail-label">Price:</span> <span class="detail-value">{{ formatCurrency(selectedExpense.price, selectedExpense.currency) }}</span></div>
              <div class="detail-item"><span class="detail-label">Currency:</span> <span class="detail-value">{{ selectedExpense.currency }}</span></div>
              <div class="detail-item full-width" v-if="selectedExpense.notes">
                <span class="detail-label">Notes:</span> 
                <span class="detail-value">{{ selectedExpense.notes }}</span>
              </div>
              <div class="detail-item"><span class="detail-label">Created:</span> <span class="detail-value">{{ formatDateTime(selectedExpense.created_at) }}</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop style="max-width: 450px;">
        <div class="modal-header">
          <h3>Expense löschen?</h3>
          <button @click="closeDeleteModal" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <p style="margin-bottom: 1.5rem; color: var(--text-primary);">
            Möchtest du diese Ausgabe wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.
          </p>
          <div v-if="expenseToDelete" style="padding: 1rem; background: var(--bg-tertiary); border-radius: var(--radius-sm); margin-bottom: 1.5rem;">
            <strong style="color: var(--text-primary);">{{ expenseToDelete.name }}</strong><br>
            <span style="color: var(--text-secondary); font-size: 0.9rem;">
              {{ formatCurrency(expenseToDelete.price, expenseToDelete.currency) }} • {{ formatDate(expenseToDelete.expiry_date) }}
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
    
    <!-- Success Toast Notification -->
    <div v-if="showSuccessMessage" class="toast-overlay">
      <div class="toast-success">
        <span class="toast-icon">✓</span>
        <span class="toast-message">{{ successMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.js'

export default {
  name: 'Expenses',
  data() {
    return {
      expenses: [],
      currentPage: 1,
      pageSize: 10,
      loading: true,
      error: null,
      showAddForm: false,
      showDetailsModal: false,
      showDeleteModal: false,
      selectedExpense: null,
      expenseToDelete: null,
      showSuccessMessage: false,
      successMessage: '',
      newExpense: {
        name: '',
        category: '',
        purchase_date: '',
        expiry_date: '',
        price: null,
        currency: 'EUR',
        notes: ''
      }
    }
  },
  mounted() {
    this.loadExpenses()
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
    isExpiringSoon(expiryDate) {
      if (!expiryDate) return false
      const today = new Date()
      const expiry = new Date(expiryDate)
      const diffTime = expiry - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays >= 0 && diffDays < 30
    },
    viewDetails(expense) {
      this.selectedExpense = expense
      this.showDetailsModal = true
    },
    closeDetailsModal() {
      this.showDetailsModal = false
      this.selectedExpense = null
    },
    closeDeleteModal() {
      this.showDeleteModal = false
      this.expenseToDelete = null
    },
    showSuccess(message) {
      this.successMessage = message
      this.showSuccessMessage = true
      setTimeout(() => {
        this.showSuccessMessage = false
      }, 3000)
    },
    async addExpense() {
      try {
        await api.createExpense(this.newExpense)
        
        // Reset form
        this.newExpense = {
          name: '',
          category: '',
          purchase_date: '',
          expiry_date: '',
          price: null,
          currency: 'EUR',
          notes: ''
        }
        
        // Reload expenses
        this.currentPage = 1
        await this.loadExpenses()
        
        // Close form and show success
        this.showAddForm = false
        this.showSuccess('Expense added successfully!')
      } catch (err) {
        console.error('Add expense error:', err)
        alert('Failed to add expense: ' + (err.response?.data?.detail || err.message))
      }
    },
    async loadExpenses() {
      try {
        this.loading = true
        this.error = null
        
        const offset = (this.currentPage - 1) * this.pageSize
        const response = await api.getExpenses(this.pageSize, false, offset)
        this.expenses = response.data
      } catch (err) {
        console.error('Load expenses error:', err)
        this.error = 'Failed to load expenses: ' + (err.response?.data?.detail || err.message)
      } finally {
        this.loading = false
      }
    },
    deleteExpense(expense) {
      this.expenseToDelete = expense
      this.showDeleteModal = true
    },
    async confirmDelete() {
      if (!this.expenseToDelete) return
      
      try {
        await api.deleteExpense(this.expenseToDelete.id)
        this.closeDeleteModal()
        await this.loadExpenses()
        this.showSuccess('Expense deleted successfully!')
      } catch (err) {
        console.error('Delete expense error:', err)
        this.closeDeleteModal()
        alert('Failed to delete expense: ' + (err.response?.data?.detail || err.message))
      }
    },
    changePageSize() {
      this.currentPage = 1
      this.loadExpenses()
    },
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.loadExpenses()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    nextPage() {
      if (this.expenses.length === this.pageSize) {
        this.currentPage++
        this.loadExpenses()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    async downloadCSV() {
      try {
        const response = await api.getExpenses(1000, true)
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `expenses_${new Date().toISOString().split('T')[0]}.csv`
        a.click()
      } catch (err) {
        alert('Failed to download CSV: ' + err.message)
      }
    },
    calculateTotalByCurrency() {
      const totals = {}
      this.expenses.forEach(expense => {
        const currency = expense.currency || 'EUR'
        if (!totals[currency]) {
          totals[currency] = 0
        }
        totals[currency] += expense.price
      })
      
      return Object.entries(totals)
        .map(([currency, total]) => this.formatCurrency(total, currency))
        .join(' + ')
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString('de-DE')
    },
    formatDateTime(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString('de-DE')
    },
    formatCurrency(value, currency = 'EUR') {
      if (value === null || value === undefined) return '-'
      
      const currencySymbols = {
        'EUR': '€',
        'USD': '$',
        'CHF': 'Fr',
        'GBP': '£'
      }
      
      return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: currency
      }).format(value).replace(currency, currencySymbols[currency] || currency)
    }
  }
}
</script>

<style scoped>
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.75rem;
  margin-bottom: 1.5rem;
}

.expense-form {
  margin-top: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
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
  background: var(--bg-tertiary);
}

th {
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 2px solid var(--border-color);
}

td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
}

tr.expiring-soon {
  background-color: var(--danger-bg);
  border-left: 3px solid var(--danger);
}

.warning-badge {
  display: inline-block;
  margin-left: 0.5rem;
  font-size: 0.85rem;
  color: var(--warning);
}

.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-size-selector select {
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.pagination-buttons {
  display: flex;
  align-items: center;
}

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
}

.modal-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
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
}

.btn-close {
  background: none;
  border: none;
  font-size: 2rem;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
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
  gap: 1rem;
}

.detail-item {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
}

.detail-item.full-width {
  grid-column: 1 / -1;
  grid-template-columns: 150px 1fr;
}

.detail-label {
  font-weight: 600;
  color: var(--text-secondary);
}

.detail-value {
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

.toast-overlay {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 2000;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast-success {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--success-bg);
  border: 1px solid var(--success);
  border-left: 4px solid var(--success);
  color: var(--success);
  padding: 1rem 1.5rem;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  min-width: 300px;
}

.toast-icon {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--success);
  background: rgba(63, 185, 80, 0.2);
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.toast-message {
  font-weight: 500;
  color: var(--text-primary);
}
</style>
