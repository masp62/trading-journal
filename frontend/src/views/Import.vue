<template>
  <div class="import">
    <div class="card">
      <h3>Import Trades</h3>
      <p style="color: #6c757d; margin-bottom: 1rem;">
        Upload the JSON export file from Trading212 containing deine Trades <b>oder</b> füge den JSON-Inhalt direkt unten ein.
      </p>
      <div class="form-group">
        <label>Trades JSON File</label>
        <input type="file" @change="handleTradesFile" accept=".json" />
      </div>
      <div class="form-group" style="margin-top: 1rem;">
        <label>Oder JSON-Inhalt einfügen</label>
        <textarea v-model="tradesJsonText" rows="6" style="width:100%;font-family:monospace;"></textarea>
      </div>
      <button @click="importTrades" :disabled="!tradesFile && !tradesJsonText" class="btn btn-primary">
        Import Trades
      </button>
      <div v-if="tradesResult" :class="tradesResult.success ? 'success-message' : 'error'" style="margin-top: 1rem;">
        {{ tradesResult.message }}
      </div>
    </div>
    
    <div class="card">
      <h3>Import Overnight Fees</h3>
      <p style="color: #6c757d; margin-bottom: 1rem;">
        Upload die JSON-Datei <b>oder</b> füge den JSON-Inhalt direkt unten ein.
      </p>
      <div class="form-group">
        <label>Overnight Fees JSON File</label>
        <input type="file" @change="handleFeesFile" accept=".json" />
      </div>
      <div class="form-group" style="margin-top: 1rem;">
        <label>Oder JSON-Inhalt einfügen</label>
        <textarea v-model="feesJsonText" rows="6" style="width:100%;font-family:monospace;"></textarea>
      </div>
      <button @click="importFees" :disabled="!feesFile && !feesJsonText" class="btn btn-primary">
        Import Overnight Fees
      </button>
      <div v-if="feesResult" :class="feesResult.success ? 'success-message' : 'error'" style="margin-top: 1rem;">
        {{ feesResult.message }}
      </div>
    </div>
    
    <div class="card">
      <h3>Instructions</h3>
      <ol style="line-height: 1.8;">
        <li>Log in to Trading212</li>
        <li>Navigate to History → Export</li>
        <li>Select the desired time period</li>
        <li>Download as JSON format</li>
        <li>Upload the files here</li>
      </ol>
      <p style="margin-top: 1rem; padding: 1rem; background: var(--warning-bg); border-radius: var(--radius-md); border: 1px solid var(--warning); color: var(--text-primary);">
        <strong style="color: var(--warning);">Note:</strong> Duplicate entries (same position ID) will be automatically skipped.
      </p>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.js'

export default {
  name: 'Import',
  data() {
    return {
      tradesFile: null,
      tradesJsonText: '',
      feesFile: null,
      feesJsonText: '',
      tradesResult: null,
      feesResult: null
    }
  },
  methods: {
    handleTradesFile(event) {
      this.tradesFile = event.target.files[0]
      this.tradesResult = null
    },
    handleFeesFile(event) {
      this.feesFile = event.target.files[0]
      this.feesResult = null
    },
    async importTrades() {
      let data = null
      if (this.tradesFile) {
        try {
          const text = await this.tradesFile.text()
          data = JSON.parse(text)
        } catch (err) {
          this.tradesResult = {
            success: false,
            message: 'Datei konnte nicht gelesen werden: ' + err.message
          }
          return
        }
      } else if (this.tradesJsonText) {
        try {
          data = JSON.parse(this.tradesJsonText)
        } catch (err) {
          this.tradesResult = {
            success: false,
            message: 'JSON-Text ungültig: ' + err.message
          }
          return
        }
      } else {
        this.tradesResult = {
          success: false,
          message: 'Bitte Datei auswählen oder JSON einfügen.'
        }
        return
      }
      try {
        const response = await api.importTrades(data)
        this.tradesResult = {
          success: true,
          message: `Successfully imported ${response.data.imported} trades | Duplicates: ${response.data.duplicates} | Archived: ${response.data.archived} | Skipped: ${response.data.skipped}`
        }
      } catch (err) {
        this.tradesResult = {
          success: false,
          message: 'Import failed: ' + (err.response?.data?.detail || err.message)
        }
      }
    },
    async importFees() {
      let data = null
      if (this.feesFile) {
        try {
          const text = await this.feesFile.text()
          data = JSON.parse(text)
        } catch (err) {
          this.feesResult = {
            success: false,
            message: 'Datei konnte nicht gelesen werden: ' + err.message
          }
          return
        }
      } else if (this.feesJsonText) {
        try {
          data = JSON.parse(this.feesJsonText)
        } catch (err) {
          this.feesResult = {
            success: false,
            message: 'JSON-Text ungültig: ' + err.message
          }
          return
        }
      } else {
        this.feesResult = {
          success: false,
          message: 'Bitte Datei auswählen oder JSON einfügen.'
        }
        return
      }
      try {
        const response = await api.importOvernightFees(data)
        this.feesResult = {
          success: true,
          message: `Successfully imported ${response.data.imported} overnight fees | Duplicates: ${response.data.duplicates} | Archived: ${response.data.archived} | Skipped: ${response.data.skipped}`
        }
      } catch (err) {
        this.feesResult = {
          success: false,
          message: 'Import failed: ' + (err.response?.data?.detail || err.message)
        }
      }
    }
  }
}
</script>

<style scoped>
.success-message {
  background: #d4edda;
  color: #155724;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #c3e6cb;
}

ol {
  padding-left: 1.5rem;
}
</style>
