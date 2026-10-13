<template>
  <div class="settings">
    <h2>⚙️ Settings</h2>
    
    <div v-if="loading" class="loading">Loading settings...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="settings-container">
      <!-- Trading Settings Section -->
      <div class="settings-section">
        <h3>Trading Targets</h3>
        <p class="section-description">Configure your daily trading targets and goals</p>
        
        <div class="settings-group">
          <div class="setting-item">
            <div class="setting-info">
              <label for="daily-target">Daily Profit Target</label>
              <p class="setting-description">Set your target profit per trading day in EUR. This value is used for analytics and performance tracking.</p>
            </div>
            <div class="setting-control">
              <div class="input-group">
                <input 
                  id="daily-target"
                  type="number" 
                  step="0.01" 
                  v-model.number="dailyProfitTarget"
                  class="setting-input"
                  @change="updateDailyTarget"
                />
                <span class="input-suffix">€</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Success message -->
      <div v-if="saveSuccess" class="success-message">
        ✓ Settings saved successfully
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.js'

export default {
  name: 'Settings',
  data() {
    return {
      dailyProfitTarget: 25.0,
      loading: true,
      error: null,
      saveSuccess: false
    }
  },
  mounted() {
    this.loadDailyTarget()
  },
  methods: {
    async loadDailyTarget() {
      try {
        this.loading = true
        this.error = null
        const response = await api.getDailyProfitTarget()
        this.dailyProfitTarget = response.data.value
      } catch (err) {
        this.error = 'Failed to load settings: ' + (err.response?.data?.detail || err.message)
      } finally {
        this.loading = false
      }
    },
    async updateDailyTarget() {
      try {
        this.saveSuccess = false
        await api.updateDailyProfitTarget(this.dailyProfitTarget)
        
        // Show success message
        this.saveSuccess = true
        setTimeout(() => {
          this.saveSuccess = false
        }, 3000)
      } catch (err) {
        this.error = 'Failed to update daily target: ' + (err.response?.data?.detail || err.message)
      }
    }
  }
}
</script>

<style scoped>
.settings h2 {
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--success));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.settings-container {
  max-width: 800px;
}

.settings-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 2rem;
  margin-bottom: 2rem;
}

.settings-section h3 {
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.section-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.settings-group {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  padding: 1.5rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.setting-item:hover {
  border-color: var(--accent-primary);
  background: var(--bg-hover);
}

.setting-info {
  flex: 1;
}

.setting-info label {
  display: block;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.setting-description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

.setting-control {
  min-width: 200px;
}

.input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  transition: all 0.2s ease;
}

.input-group:focus-within {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.2);
}

.setting-input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 1.125rem;
  font-weight: 600;
  outline: none;
  width: 100%;
}

.setting-input::-webkit-inner-spin-button,
.setting-input::-webkit-outer-spin-button {
  opacity: 1;
}

.input-suffix {
  color: var(--success);
  font-size: 1.125rem;
  font-weight: 600;
}

.success-message {
  background: var(--success-bg);
  color: var(--success);
  padding: 1rem 1.5rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--success);
  font-weight: 500;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.loading, .error {
  padding: 2rem;
  text-align: center;
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.error {
  color: var(--danger);
  background: var(--danger-bg);
  border-color: var(--danger);
}

@media (max-width: 768px) {
  .setting-item {
    flex-direction: column;
    gap: 1rem;
  }
  
  .setting-control {
    width: 100%;
  }
}
</style>
