import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default {
  // Trades API
  async getTrades(limit = 50, asCSV = false, filters = {}, offset = 0) {
    const params = { limit }
    if (asCSV) params.format = 'csv'
    if (offset > 0) params.offset = offset
    
    // Add filter parameters - only add if they have a valid value
    if (filters.symbol && filters.symbol.trim()) params.symbol = filters.symbol.trim()
    if (filters.action && filters.action.trim()) params.action = filters.action.trim()
    if (filters.from_date && filters.from_date.trim()) params.from_date = filters.from_date.trim()
    if (filters.to_date && filters.to_date.trim()) params.to_date = filters.to_date.trim()
    if (filters.min_profit !== null && filters.min_profit !== undefined && filters.min_profit !== '') {
      params.min_profit = filters.min_profit
    }
    
    console.log('API getTrades called with params:', params)
    return apiClient.get('/trades/', { params })
  },

  async getTrade(tradeId) {
    return apiClient.get(`/trades/${tradeId}`)
  },

  async getTradeByOrderNumber(orderNumber) {
    return apiClient.get(`/trades/by-order/${encodeURIComponent(orderNumber)}`)
  },

  async createTrade(tradeData) {
    return apiClient.post('/trades/', tradeData)
  },

  async deleteTrade(tradeId) {
    return apiClient.delete(`/trades/${tradeId}`)
  },

  // Journal API
  async getJournalEntries(limit = 50) {
    return apiClient.get('/journal/', { params: { limit } })
  },

  async getJournalEntry(entryId) {
    return apiClient.get(`/journal/${entryId}`)
  },

  async createJournalEntry(entryData) {
    return apiClient.post('/journal/', entryData)
  },

  async deleteJournalEntry(entryId) {
    return apiClient.delete(`/journal/${entryId}`)
  },

  // Analytics API
  async getAnalytics(fromDate = null, toDate = null) {
    const params = {};
    if (fromDate) params.from_date = fromDate;
    if (toDate) params.to_date = toDate;
    return apiClient.get('/analytics/', { params });
  },

  async getInstrumentStats(limit = null, fromDate = null, toDate = null) {
    const params = {};
    if (limit) params.limit = limit;
    if (fromDate) params.from_date = fromDate;
    if (toDate) params.to_date = toDate;
    return apiClient.get('/analytics/by-instrument', { params });
  },

  async getProfitDistribution(fromDate = null, toDate = null) {
    const params = {};
    if (fromDate) params.from_date = fromDate;
    if (toDate) params.to_date = toDate;
    return apiClient.get('/analytics/profit-distribution', { params });
  },

  async getPeriodStats(period = 'week', limit = 10) {
    return apiClient.get('/analytics/by-period', { params: { period, limit } })
  },

  // Overnight Fees API
  async getOvernightFees(limit = 50, asCSV = false, offset = 0) {
    const params = { limit }
    if (asCSV) params.format = 'csv'
    if (offset > 0) params.offset = offset
    return apiClient.get('/overnight/', { params })
  },

  async getOvernightFee(feeId) {
    return apiClient.get(`/overnight/${feeId}`)
  },

  async createOvernightFee(feeData) {
    return apiClient.post('/overnight/', feeData)
  },

  async deleteOvernightFee(feeId) {
    return apiClient.delete(`/overnight/${feeId}`)
  },

  async getOvernightFeesForTrade(orderNumberName) {
    return apiClient.get(`/trades/overnight-fees/${encodeURIComponent(orderNumberName)}`)
  },

  // Trading212 Import API
  async importTrades(tradesData) {
    return apiClient.post('/import/trades', tradesData)
  },

  async importOvernightFees(feesData) {
    return apiClient.post('/import/overnight', feesData)
  },

  // Expenses API
  async getExpenses(limit = 50, asCSV = false, offset = 0) {
    const params = { limit }
    if (asCSV) params.format = 'csv'
    if (offset > 0) params.offset = offset
    return apiClient.get('/expenses/', { params })
  },

  async getExpense(expenseId) {
    return apiClient.get(`/expenses/${expenseId}`)
  },

  async createExpense(expenseData) {
    return apiClient.post('/expenses/', expenseData)
  },

  async deleteExpense(expenseId) {
    return apiClient.delete(`/expenses/${expenseId}`)
  },

  // Settings API
  async getDailyProfitTarget() {
    return apiClient.get('/settings/daily-profit-target')
  },

  async updateDailyProfitTarget(value) {
    return apiClient.put('/settings/daily-profit-target', { value })
  },

  // Health check
  async healthCheck() {
    return axios.get('/health')
  }
}
