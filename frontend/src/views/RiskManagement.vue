<template>
  <div class="risk-management">
    
    <div class="card">
      <h3>🎯 Positions-Größen-Rechner</h3>
      <p class="description">Berechne optimale Positionsgröße für CFD-Trading mit Hebel</p>
      
      <div class="form-grid">
        <div class="input-group">
          <label>Portfolio-Wert (€):</label>
          <input 
            v-model.number="posCalc.portfolio" 
            type="number" 
            step="100"
            placeholder="Leer lassen für automatische Berechnung"
          />
        </div>
        
        <div class="input-group">
          <label>Risiko (%):</label>
          <input 
            v-model.number="posCalc.riskPercent" 
            type="number" 
            step="0.1"
            min="0.1"
            max="100"
            placeholder="z.B. 2"
            required
          />
        </div>
        
        <div class="input-group">
          <label>Einstiegspreis (€):</label>
          <input 
            v-model.number="posCalc.entryPrice" 
            type="number" 
            step="0.01"
            placeholder="z.B. 18500"
            required
          />
        </div>
        
        <div class="input-group">
          <label>Stop-Loss (€):</label>
          <input 
            v-model.number="posCalc.stopLoss" 
            type="number" 
            step="0.01"
            placeholder="z.B. 18300"
            required
          />
        </div>
        
        <div class="input-group">
          <label>Hebel:</label>
          <input 
            v-model.number="posCalc.leverage" 
            type="number" 
            step="1"
            min="1"
            placeholder="z.B. 20"
          />
        </div>
      </div>
      
      <button @click="calculatePositionSize" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">Berechnen</button>
      
      <div v-if="posCalc.error" class="error-message">
        {{ posCalc.error }}
      </div>
      
      <div v-if="posCalc.calculated" class="results-section">
        <div class="result-box">
          <h4>📊 Eingabeparameter</h4>
          <div class="details-grid">
            <div class="detail-item">
              <span class="label">Portfolio-Wert:</span>
              <span class="value">{{ formatCurrency(posCalc.result.portfolio) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Risiko:</span>
              <span class="value">{{ posCalc.result.riskPercent }}% ({{ formatCurrency(posCalc.result.riskAmount) }})</span>
            </div>
            <div class="detail-item">
              <span class="label">Einstiegspreis:</span>
              <span class="value">{{ formatCurrency(posCalc.result.entryPrice) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Stop-Loss:</span>
              <span class="value">{{ formatCurrency(posCalc.result.stopLoss) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Stop-Loss-Distanz:</span>
              <span class="value">{{ formatCurrency(posCalc.result.stopLossDistance) }} ({{ posCalc.result.stopLossPercent.toFixed(2) }}%)</span>
            </div>
            <div class="detail-item">
              <span class="label">Hebel:</span>
              <span class="value">{{ posCalc.result.leverage }}x</span>
            </div>
          </div>
        </div>
        
        <div class="result-box highlight">
          <h4>🎯 Berechnete Position</h4>
          <div class="details-grid">
            <div class="detail-item">
              <span class="label">Positionsgröße:</span>
              <span class="value"><strong>{{ posCalc.result.positionSize.toFixed(2) }} Kontrakte/Einheiten</strong></span>
            </div>
            <div class="detail-item">
              <span class="label">Positionswert:</span>
              <span class="value"><strong>{{ formatCurrency(posCalc.result.positionValue) }}</strong></span>
            </div>
            <div class="detail-item">
              <span class="label">Benötigte Margin:</span>
              <span class="value" :class="{ 'warning-text': posCalc.result.marginUsagePercent > 30 }">
                {{ formatCurrency(posCalc.result.marginRequired) }} ({{ posCalc.result.marginUsagePercent.toFixed(1) }}%)
              </span>
            </div>
            <div class="detail-item">
              <span class="label">Verbleibende Margin:</span>
              <span class="value">{{ formatCurrency(posCalc.result.remainingMargin) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">Verlust bei Stop-Loss:</span>
              <span class="value" style="color: var(--danger);">{{ formatCurrency(posCalc.result.lossAtStopLoss) }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="posCalc.result.marginUsagePercent > 50" class="warning-box danger">
          ⚠ WARNUNG: Margin-Nutzung über 50%! Hohes Risiko eines Margin Calls!
        </div>
        <div v-else-if="posCalc.result.marginUsagePercent > 30" class="warning-box">
          ⚠ Achtung: Margin-Nutzung über 30%. Vorsicht bei volatilen Märkten!
        </div>
        
        <div class="result-box">
          <h4>📈 Gewinn/Verlust-Szenarien</h4>
          <table>
            <thead>
              <tr>
                <th>Szenario</th>
                <th>Kursänderung (€)</th>
                <th>Neuer Kurs</th>
                <th>G/V (€)</th>
                <th>G/V (% Portfolio)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="scenario in posCalc.result.scenarios" :key="scenario.label">
                <td>{{ scenario.label }}</td>
                <td :style="{ color: scenario.priceChange >= 0 ? 'var(--success)' : 'var(--danger)' }">
                  {{ scenario.priceChange >= 0 ? '+' : '' }}{{ scenario.priceChange.toFixed(2) }}
                </td>
                <td>{{ formatCurrency(scenario.newPrice) }}</td>
                <td :style="{ color: scenario.pnl >= 0 ? 'var(--success)' : 'var(--danger)' }">
                  {{ formatCurrency(scenario.pnl) }}
                </td>
                <td :style="{ color: scenario.pnlPercent >= 0 ? 'var(--success)' : 'var(--danger)' }">
                  {{ scenario.pnlPercent >= 0 ? '+' : '' }}{{ scenario.pnlPercent.toFixed(2) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="info-box">
          <h4>⚠ Wichtige Hinweise:</h4>
          <ul>
            <li>Stellen Sie sicher, dass genug freie Margin vorhanden ist</li>
            <li>Berücksichtigen Sie Spreads und Gebühren</li>
            <li>Hebel vergrößert sowohl Gewinne als auch Verluste</li>
            <li>Stop-Loss diszipliniert einhalten!</li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="card">
      <h3>📊 Risiko-Rechner</h3>
      <p class="description">Berechne Risiko-Beträge für verschiedene Prozentsätze deines Portfolios</p>
      
      <div class="input-group">
        <label>Portfolio-Wert (€):</label>
        <input 
          v-model.number="riskCalc.portfolio" 
          type="number" 
          step="100"
          placeholder="Leer lassen für automatische Berechnung"
        />
        <button @click="calculateRiskAmounts" class="btn btn-primary" style="margin-top: 0.75rem;">Berechnen</button>
      </div>
      
      <div v-if="riskCalc.calculated" class="portfolio-info">
        <p><strong>Portfolio-Wert:</strong> {{ formatCurrency(riskCalc.actualPortfolio) }}</p>
        <p><small>Net Profit (Alle Trades): {{ formatCurrency(riskCalc.totalTrades) }} | Overnight-Zinsen: {{ formatCurrency(riskCalc.totalOvernight) }}</small></p>
      </div>
      
      <div v-if="riskCalc.results.length > 0" class="results-section">
        <table>
          <thead>
            <tr>
              <th>Risiko %</th>
              <th>Betrag (€)</th>
              <th>Verbleibendes Kapital (€)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="result in riskCalc.results" :key="result.percentage">
              <td><strong>{{ result.percentage }}%</strong></td>
              <td>{{ formatCurrency(result.amount) }}</td>
              <td>{{ formatCurrency(result.remaining) }}</td>
            </tr>
          </tbody>
        </table>
        
        <div class="recommendations">
          <h4>💡 Empfehlungen:</h4>
          <ul>
            <li><strong>Anfänger:</strong> 1-2% Risiko pro Trade</li>
            <li><strong>Fortgeschritten:</strong> 2-3% Risiko pro Trade</li>
            <li><strong>Erfahren:</strong> 3-5% Risiko pro Trade</li>
            <li class="warning"><strong>⚠ Warnung:</strong> >5% Risiko kann zu schnellem Kapitalverlust führen</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.js'

export default {
  name: 'RiskManagement',
  data() {
    return {
      riskCalc: {
        portfolio: null,
        actualPortfolio: 0,
        totalTrades: 0,
        totalOvernight: 0,
        calculated: false,
        results: []
      },
      posCalc: {
        portfolio: null,
        riskPercent: 2,
        entryPrice: null,
        stopLoss: null,
        leverage: 20,
        calculated: false,
        error: null,
        result: null
      }
    }
  },
  methods: {
    async calculateRiskAmounts() {
      try {
        let portfolio = this.riskCalc.portfolio
        
        // Wenn kein Wert angegeben, aus Datenbank berechnen
        if (!portfolio) {
          const analyticsResponse = await api.getAnalytics()
          const analytics = analyticsResponse.data
          
          // Use net_profit (all trades) instead of total_profit (only winning trades)
          this.riskCalc.totalTrades = analytics.net_profit || 0
          this.riskCalc.totalOvernight = analytics.total_overnight_fees || 0
          portfolio = this.riskCalc.totalTrades + this.riskCalc.totalOvernight
        }
        
        if (portfolio <= 0) {
          alert('Portfolio-Wert muss größer als 0 sein.')
          return
        }
        
        this.riskCalc.actualPortfolio = portfolio
        this.riskCalc.calculated = true
        
        const percentages = [1, 2, 3, 4, 5, 10]
        this.riskCalc.results = percentages.map(percentage => ({
          percentage,
          amount: portfolio * (percentage / 100),
          remaining: portfolio * (1 - percentage / 100)
        }))
      } catch (err) {
        console.error('Failed to calculate risk amounts:', err)
        alert('Fehler beim Berechnen der Risiko-Beträge')
      }
    },
    
    async calculatePositionSize() {
      this.posCalc.error = null
      this.posCalc.calculated = false
      
      try {
        // Validierung
        if (!this.posCalc.riskPercent || !this.posCalc.entryPrice || !this.posCalc.stopLoss) {
          this.posCalc.error = 'Bitte alle Pflichtfelder ausfüllen (Risiko %, Einstiegspreis, Stop-Loss)'
          return
        }
        
        if (this.posCalc.entryPrice <= 0 || this.posCalc.stopLoss <= 0) {
          this.posCalc.error = 'Einstiegspreis und Stop-Loss müssen größer als 0 sein'
          return
        }
        
        if (this.posCalc.riskPercent <= 0 || this.posCalc.riskPercent > 100) {
          this.posCalc.error = 'Risiko-Prozentsatz muss zwischen 0 und 100 liegen'
          return
        }
        
        let portfolio = this.posCalc.portfolio
        
        // Wenn kein Wert angegeben, aus Datenbank berechnen
        if (!portfolio) {
          const analyticsResponse = await api.getAnalytics()
          const analytics = analyticsResponse.data
          
          // Use net_profit (all trades) instead of total_profit (only winning trades)
          const totalTrades = analytics.net_profit || 0
          const totalOvernight = analytics.total_overnight_fees || 0
          portfolio = totalTrades + totalOvernight
          
          if (portfolio <= 0) {
            this.posCalc.error = 'Kein Portfolio-Wert in der Datenbank gefunden. Bitte manuell eingeben.'
            return
          }
        }
        
        // Berechnungen
        const riskAmount = portfolio * (this.posCalc.riskPercent / 100)
        const stopLossDistance = Math.abs(this.posCalc.entryPrice - this.posCalc.stopLoss)
        const stopLossPercent = (stopLossDistance / this.posCalc.entryPrice) * 100
        
        const positionSize = riskAmount / stopLossDistance
        const positionValue = positionSize * this.posCalc.entryPrice
        
        const marginRequired = positionValue / this.posCalc.leverage
        const remainingMargin = portfolio - marginRequired
        const marginUsagePercent = (marginRequired / portfolio) * 100
        
        const lossAtStopLoss = positionSize * stopLossDistance
        
        // Szenarien berechnen
        const scenarioDefinitions = [
          { percent: -2, label: '2% Kursverlust' },
          { percent: -1, label: '1% Kursverlust' },
          { percent: -0.5, label: '0.5% Kursverlust' },
          { percent: -0.25, label: '0.25% Kursverlust' },
          { percent: 0, label: 'Breakeven (0%)' },
          { percent: 0.25, label: '0.25% Kursgewinn' },
          { percent: 0.5, label: '0.5% Kursgewinn' },
          { percent: 1, label: '1% Kursgewinn' },
          { percent: 2, label: '2% Kursgewinn' }
        ]
        
        const scenarios = scenarioDefinitions.map(({ percent, label }) => {
          const newPrice = this.posCalc.entryPrice * (1 + percent / 100)
          const priceChange = newPrice - this.posCalc.entryPrice
          const pnl = positionSize * priceChange
          const pnlPercent = (pnl / portfolio) * 100
          
          return {
            label,
            priceChange,
            newPrice,
            pnl,
            pnlPercent
          }
        })
        
        this.posCalc.result = {
          portfolio,
          riskPercent: this.posCalc.riskPercent,
          riskAmount,
          entryPrice: this.posCalc.entryPrice,
          stopLoss: this.posCalc.stopLoss,
          stopLossDistance,
          stopLossPercent,
          leverage: this.posCalc.leverage,
          positionSize,
          positionValue,
          marginRequired,
          remainingMargin,
          marginUsagePercent,
          lossAtStopLoss,
          scenarios
        }
        
        this.posCalc.calculated = true
      } catch (err) {
        console.error('Failed to calculate position size:', err)
        this.posCalc.error = 'Fehler beim Berechnen der Positionsgröße'
      }
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
.risk-management {
  /* max-width is set by parent container */
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.75rem;
  margin-bottom: 1.5rem;
}

.card h3 {
  margin-top: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.description {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.input-group {
  margin-bottom: 1rem;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  font-weight: 600;
}

.input-group input {
  width: 100%;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 1rem;
}

.input-group input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1rem;
  font-weight: 600;
}

.btn:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
}

.btn-primary {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.btn-primary:hover {
  opacity: 0.9;
}

.portfolio-info {
  padding: 1rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
}

.portfolio-info p {
  margin: 0.25rem 0;
  color: var(--text-primary);
}

.results-section {
  margin-top: 1.5rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
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

.recommendations {
  padding: 1.5rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.recommendations h4 {
  margin-top: 0;
  color: var(--text-primary);
}

.recommendations ul {
  margin: 0;
  padding-left: 1.5rem;
}

.recommendations li {
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.recommendations li.warning {
  color: var(--danger);
}

.result-box {
  padding: 1.5rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
}

.result-box.highlight {
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  border-color: var(--accent-primary);
}

.result-box h4 {
  margin-top: 0;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.detail-item .label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.detail-item .value {
  color: var(--text-primary);
  font-weight: 600;
  text-align: right;
}

.warning-text {
  color: var(--danger) !important;
}

.warning-box {
  padding: 1rem;
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid #ffc107;
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
  color: #ffc107;
  font-weight: 600;
}

.warning-box.danger {
  background: rgba(231, 76, 60, 0.1);
  border-color: var(--danger);
  color: var(--danger);
}

.info-box {
  padding: 1.5rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.info-box h4 {
  margin-top: 0;
  color: var(--text-primary);
}

.info-box ul {
  margin: 0;
  padding-left: 1.5rem;
}

.info-box li {
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.error-message {
  padding: 1rem;
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger);
  border-radius: var(--radius-md);
  margin-top: 1rem;
}
</style>
