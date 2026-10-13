<template>
  <div class="market-data">
    <div class="card">
      <div class="header-row">
        <div>
          <h2>Market Data</h2>
          <p class="subtitle">
            Snapshot view to compare how major global indices are performing against each other across the selected interval.
          </p>
        </div>
        <div class="header-actions">
          <label class="range-label" for="market-range">Interval</label>
          <select
            id="market-range"
            class="range-select"
            v-model="selectedRange"
            @change="loadMarketIndices"
            :disabled="indexLoading"
          >
            <option v-for="option in rangeOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
          <button class="btn btn-primary" @click="loadMarketIndices" :disabled="indexLoading">
            {{ indexLoading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>
      </div>

      <div v-if="indexLoading" class="loading">Loading market data...</div>
      <div v-else-if="indexError" class="error">{{ indexError }}</div>
      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>
                <button class="sort-button" @click="setSort('name')">
                  Name {{ sortIndicator('name') }}
                </button>
              </th>
              <th>
                <button class="sort-button" @click="setSort('time')">
                  Time {{ sortIndicator('time') }}
                </button>
              </th>
              <th>Last</th>
              <th>{{ baselineColumnLabel }}</th>
              <th>High</th>
              <th>Low</th>
              <th>52W Range</th>
              <th>
                <button class="sort-button" @click="setSort('change')">
                  Change {{ sortIndicator('change') }}
                </button>
              </th>
              <th>
                <button class="sort-button" @click="setSort('change_percent')">
                  Change% {{ sortIndicator('change_percent') }}
                </button>
              </th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="indexItem in sortedIndexComparison" :key="`${indexItem.symbol}-${indexItem.name}`">
              <td>
                <div class="symbol">{{ indexItem.name }}</div>
                <div class="provider-symbol">{{ indexItem.symbol }}</div>
                <div v-if="indexItem.error" class="row-error">{{ indexItem.error }}</div>
              </td>
              <td>{{ formatMarketTime(indexItem.time) }}</td>
              <td>{{ formatNumber(indexItem.last) }}</td>
              <td>{{ formatNumber(indexItem.prev) }}</td>
              <td>{{ formatNumber(indexItem.high) }}</td>
              <td>{{ formatNumber(indexItem.low) }}</td>
              <td>
                <div class="range-widget" v-if="hasFiftyTwoWeekRange(indexItem)">
                  <div class="range-track">
                    <div class="range-marker" :style="{ left: getFiftyTwoWeekPosition(indexItem) + '%' }"></div>
                  </div>
                  <div class="range-values">
                    <span>{{ formatNumber(indexItem.fifty_two_week_low) }}</span>
                    <span>{{ formatNumber(indexItem.last) }}</span>
                    <span>{{ formatNumber(indexItem.fifty_two_week_high) }}</span>
                  </div>
                </div>
                <span v-else>-</span>
              </td>
              <td :class="changeClass(indexItem.change)">{{ formatSignedNumber(indexItem.change) }}</td>
              <td :class="changeClass(indexItem.change_percent)">{{ formatSignedPercent(indexItem.change_percent) }}</td>
              <td>
                <button
                  class="btn btn-primary btn-retry-icon"
                  @click="retryIndex(indexItem)"
                  :disabled="isRetrying(indexItem)"
                  :title="isRetrying(indexItem) ? 'Refreshing...' : 'Refresh row'"
                  aria-label="Refresh row"
                >
                  <span v-if="isRetrying(indexItem)">...</span>
                  <span v-else>&#x21bb;</span>
                </button>
              </td>
            </tr>
            <tr v-if="sortedIndexComparison.length === 0">
              <td colspan="10">No index data available.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="failedRows.length > 0" class="warning">
        Partial data: {{ failedRows.map(item => item.name).join(', ') }} could not be loaded.
      </p>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.js'

export default {
  name: 'MarketData',
  data() {
    return {
      indexComparison: [],
      indexLoading: false,
      indexError: null,
      rowLoading: {},
      sortKey: 'name',
      sortDirection: 'asc',
      selectedRange: '1d',
      rangeOptions: [
        { value: '1d', label: '1 Day' },
        { value: '5d', label: '5 Days' },
        { value: '1wk', label: '1 Week' },
        { value: '1mo', label: '1 Month' },
        { value: '3mo', label: '3 Months' },
        { value: '6mo', label: '6 Months' },
      ],
    }
  },
  computed: {
    failedRows() {
      return this.indexComparison.filter(item => item.error)
    },

    baselineColumnLabel() {
      return this.selectedRange === '1d' ? 'Prev' : 'Start'
    },

    sortedIndexComparison() {
      const sorted = [...this.indexComparison]

      sorted.sort((a, b) => {
        let first
        let second

        if (this.sortKey === 'name') {
          first = (a.name || '').toLowerCase()
          second = (b.name || '').toLowerCase()
        } else if (this.sortKey === 'time') {
          first = this.getSortableTime(a.time)
          second = this.getSortableTime(b.time)
        } else if (this.sortKey === 'change') {
          first = this.getSortableNumber(a.change)
          second = this.getSortableNumber(b.change)
        } else if (this.sortKey === 'change_percent') {
          first = this.getSortableNumber(a.change_percent)
          second = this.getSortableNumber(b.change_percent)
        } else {
          return 0
        }

        if (first < second) {
          return this.sortDirection === 'asc' ? -1 : 1
        }
        if (first > second) {
          return this.sortDirection === 'asc' ? 1 : -1
        }
        return 0
      })

      return sorted
    },
  },
  mounted() {
    this.loadMarketIndices()
  },
  methods: {
    async loadMarketIndices() {
      try {
        this.indexLoading = true
        this.indexError = null
        const response = await api.getMarketIndices(this.selectedRange)
        this.indexComparison = response.data.indices || []
        this.selectedRange = response.data.selected_range || this.selectedRange

        if (Array.isArray(response.data.available_ranges) && response.data.available_ranges.length > 0) {
          this.rangeOptions = response.data.available_ranges.map(rangeValue => ({
            value: rangeValue,
            label: this.getRangeLabel(rangeValue),
          }))
        }
      } catch (err) {
        this.indexError = 'Failed to load market data: ' + (err.response?.data?.detail || err.message)
      } finally {
        this.indexLoading = false
      }
    },

    async retryIndex(indexItem) {
      const rowKey = this.getRowKey(indexItem)
      this.rowLoading[rowKey] = true
      try {
        const response = await api.getMarketIndex(indexItem.symbol, indexItem.name, this.selectedRange)
        const updatedRow = response.data
        const rowIndex = this.indexComparison.findIndex(item => this.getRowKey(item) === rowKey)
        if (rowIndex !== -1) {
          this.indexComparison.splice(rowIndex, 1, updatedRow)
        }
      } catch (err) {
        const message = err.response?.data?.detail || err.message
        const rowIndex = this.indexComparison.findIndex(item => this.getRowKey(item) === rowKey)
        if (rowIndex !== -1) {
          this.indexComparison[rowIndex].error = message
        }
      } finally {
        this.rowLoading[rowKey] = false
      }
    },

    getRowKey(indexItem) {
      return `${indexItem.symbol}-${indexItem.name}`
    },

    isRetrying(indexItem) {
      return !!this.rowLoading[this.getRowKey(indexItem)]
    },

    setSort(key) {
      if (this.sortKey === key) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
        return
      }

      this.sortKey = key
      this.sortDirection = 'asc'
    },

    sortIndicator(key) {
      if (this.sortKey !== key) return ''
      return this.sortDirection === 'asc' ? '▲' : '▼'
    },

    getRangeLabel(rangeValue) {
      const labels = {
        '1d': '1 Day',
        '5d': '5 Days',
        '1wk': '1 Week',
        '1mo': '1 Month',
        '3mo': '3 Months',
        '6mo': '6 Months',
      }

      return labels[rangeValue] || rangeValue
    },

    getSortableNumber(value) {
      if (value === null || value === undefined || Number.isNaN(Number(value))) {
        return Number.NEGATIVE_INFINITY
      }
      return Number(value)
    },

    hasFiftyTwoWeekRange(indexItem) {
      const low = Number(indexItem.fifty_two_week_low)
      const high = Number(indexItem.fifty_two_week_high)
      const last = Number(indexItem.last)
      if (Number.isNaN(low) || Number.isNaN(high) || Number.isNaN(last)) return false
      return high > low
    },

    getFiftyTwoWeekPosition(indexItem) {
      if (!this.hasFiftyTwoWeekRange(indexItem)) return 0

      const low = Number(indexItem.fifty_two_week_low)
      const high = Number(indexItem.fifty_two_week_high)
      const last = Number(indexItem.last)
      const ratio = ((last - low) / (high - low)) * 100

      return Math.max(0, Math.min(100, ratio))
    },

    getSortableTime(value) {
      if (!value) return Number.NEGATIVE_INFINITY
      const parsedDate = new Date(value)
      if (Number.isNaN(parsedDate.getTime())) return Number.NEGATIVE_INFINITY
      return parsedDate.getTime()
    },

    formatNumber(value) {
      if (value === null || value === undefined) return '-'
      return Number(value).toFixed(2)
    },

    formatSignedNumber(value) {
      if (value === null || value === undefined) return '-'
      const num = Number(value)
      const sign = num > 0 ? '+' : ''
      return `${sign}${num.toFixed(2)}`
    },

    formatSignedPercent(value) {
      if (value === null || value === undefined) return '-'
      const num = Number(value)
      const sign = num > 0 ? '+' : ''
      return `${sign}${num.toFixed(2)}%`
    },

    formatMarketTime(value) {
      if (!value) return '-'
      const parsedDate = new Date(value)
      if (Number.isNaN(parsedDate.getTime())) return value
      return parsedDate.toLocaleString('de-DE')
    },

    changeClass(value) {
      if (value === null || value === undefined) return ''
      if (value > 0) return 'positive'
      if (value < 0) return 'negative'
      return ''
    },
  },
}
</script>

<style scoped>
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.subtitle {
  color: var(--text-secondary);
  margin-top: 0.3rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.range-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.range-select {
  padding: 0.4rem 0.5rem;
  border-radius: 8px;
  border: 1px solid var(--border-color, #3f3f46);
  background: var(--surface-color, #111827);
  color: var(--text-primary);
}

.table-container {
  overflow-x: auto;
}

.sort-button {
  all: unset;
  cursor: pointer;
  font-weight: 700;
  color: var(--text-primary);
  user-select: none;
}

.sort-button:hover {
  color: var(--accent-primary);
}

.symbol {
  font-weight: 700;
  color: var(--accent-primary);
}

.provider-symbol {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.row-error {
  color: var(--danger);
  font-size: 0.8rem;
  margin-top: 0.2rem;
}

.btn-retry-icon {
  width: 2rem;
  height: 2rem;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  line-height: 1;
}

.range-widget {
  min-width: 180px;
}

.range-track {
  position: relative;
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #22c55e 100%);
}

.range-marker {
  position: absolute;
  top: 50%;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #111827;
  transform: translate(-50%, -50%);
}

.range-values {
  margin-top: 0.25rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
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

.warning {
  margin-top: 0.75rem;
  color: #f59e0b;
  font-size: 0.9rem;
}

@media (max-width: 900px) {
  .header-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
