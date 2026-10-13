<template>
  <div class="profit-histogram">
    <div class="header">
      <h3>Trades Distribution</h3>
      <div class="chart-toggle">
        <button 
          :class="{ active: chartType === 'bar' }" 
          @click="chartType = 'bar'"
          class="toggle-btn"
        >
          📊
        </button>
        <button 
          :class="{ active: chartType === 'pie' }" 
          @click="chartType = 'pie'"
          class="toggle-btn"
        >
          🥧
        </button>
      </div>
    </div>
    <div v-if="loading" class="loading">Lade Daten...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="chart-container">
      <Bar v-if="chartType === 'bar'" :data="chartData" :options="chartOptions" />
      <Pie v-else :data="pieChartData" :options="pieChartOptions" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { Bar, Pie } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import api from '../services/api'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'ProfitHistogram',
  components: {
    Bar,
    Pie
  },
  props: {
    fromDate: {
      type: String,
      default: null
    },
    toDate: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const loading = ref(true)
    const error = ref(null)
    const distributionData = ref(null)
    const chartType = ref('bar')

    const chartData = computed(() => {
      if (!distributionData.value) return null

      const buckets = distributionData.value.buckets
      const labels = buckets.map(b => b.range)
      const profits = buckets.map(b => b.total_profit)
      
      // Count negative and positive buckets for gradient calculation
      const negativeBuckets = buckets.filter(b => b.min_value < 0)
      const positiveBuckets = buckets.filter(b => b.min_value >= 0)
      
      let negativeIndex = 0
      let positiveIndex = 0
      
      // Color buckets with gradients - darker for more extreme values
      const backgroundColors = buckets.map(b => {
        if (b.min_value < 0) {
          const intensity = 0.5 + (negativeIndex / Math.max(1, negativeBuckets.length - 1)) * 0.4
          negativeIndex++
          return `rgba(239, 68, 68, ${intensity})` // red gradient
        } else {
          const intensity = 0.4 + (positiveIndex / Math.max(1, positiveBuckets.length - 1)) * 0.5
          positiveIndex++
          return `rgba(34, 197, 94, ${intensity})` // green gradient
        }
      })

      negativeIndex = 0
      positiveIndex = 0
      
      const borderColors = buckets.map(b => {
        if (b.min_value < 0) {
          const intensity = 0.7 + (negativeIndex / Math.max(1, negativeBuckets.length - 1)) * 0.3
          negativeIndex++
          return `rgba(239, 68, 68, ${intensity})`
        } else {
          const intensity = 0.6 + (positiveIndex / Math.max(1, positiveBuckets.length - 1)) * 0.4
          positiveIndex++
          return `rgba(34, 197, 94, ${intensity})`
        }
      })

      return {
        labels: labels,
        datasets: [
          {
            label: 'Gewinn/Verlust (€)',
            data: profits,
            backgroundColor: backgroundColors,
            borderColor: borderColors,
            borderWidth: 1
          }
        ]
      }
    })

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(17, 24, 39, 0.95)',
          titleColor: '#f3f4f6',
          bodyColor: '#f3f4f6',
          borderColor: '#374151',
          borderWidth: 1,
          callbacks: {
            label: function(context) {
              const bucket = distributionData.value.buckets[context.dataIndex]
              return [
                `Gewinn/Verlust: ${context.parsed.y.toFixed(2)}€`,
                `Anzahl Trades: ${bucket.count}`
              ]
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            precision: 0,
            color: '#9ca3af'
          },
          title: {
            display: true,
            text: 'Gewinn/Verlust (€)',
            color: '#d1d5db'
          }
        },
        x: {
          grid: {
            color: 'rgba(255, 255, 255, 0.05)'
          },
          title: {
            display: true,
            text: 'Gewinn/Verlust Bereich',
            color: '#d1d5db'
          },
          ticks: {
            maxRotation: 45,
            minRotation: 45,
            color: '#9ca3af'
          }
        }
      }
    }

    const pieChartData = computed(() => {
      if (!distributionData.value) return null

      const buckets = distributionData.value.buckets
      const labels = buckets.map(b => b.range)
      const profits = buckets.map(b => b.total_profit)
      
      // Count negative and positive buckets for gradient calculation
      const negativeBuckets = buckets.filter(b => b.min_value < 0)
      const positiveBuckets = buckets.filter(b => b.min_value >= 0)
      
      let negativeIndex = 0
      let positiveIndex = 0
      
      // Color buckets with gradients - darker for more extreme values
      const backgroundColors = buckets.map(b => {
        if (b.min_value < 0) {
          const intensity = 0.6 + (negativeIndex / Math.max(1, negativeBuckets.length - 1)) * 0.3
          negativeIndex++
          return `rgba(239, 68, 68, ${intensity})` // red gradient
        } else {
          const intensity = 0.5 + (positiveIndex / Math.max(1, positiveBuckets.length - 1)) * 0.4
          positiveIndex++
          return `rgba(34, 197, 94, ${intensity})` // green gradient
        }
      })

      negativeIndex = 0
      positiveIndex = 0
      
      const borderColors = buckets.map(b => {
        if (b.min_value < 0) {
          const intensity = 0.8 + (negativeIndex / Math.max(1, negativeBuckets.length - 1)) * 0.2
          negativeIndex++
          return `rgba(239, 68, 68, ${intensity})`
        } else {
          const intensity = 0.7 + (positiveIndex / Math.max(1, positiveBuckets.length - 1)) * 0.3
          positiveIndex++
          return `rgba(34, 197, 94, ${intensity})`
        }
      })

      return {
        labels: labels,
        datasets: [
          {
            label: 'Gewinn/Verlust (€)',
            data: profits,
            backgroundColor: backgroundColors,
            borderColor: borderColors,
            borderWidth: 1
          }
        ]
      }
    })

    const pieChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'right',
          labels: {
            color: '#d1d5db',
            font: {
              size: 11
            },
            padding: 10,
            generateLabels: function(chart) {
              const data = chart.data
              if (data.labels.length && data.datasets.length) {
                return data.labels.map((label, i) => {
                  const meta = chart.getDatasetMeta(0)
                  const value = data.datasets[0].data[i]
                  const bucket = distributionData.value.buckets[i]
                  return {
                    text: `${label}: ${value.toFixed(2)}€ (${bucket.count} Trades)`,
                    fillStyle: data.datasets[0].backgroundColor[i],
                    strokeStyle: data.datasets[0].borderColor[i],
                    fontColor: '#d1d5db',
                    lineWidth: 1,
                    hidden: isNaN(value) || meta.data[i].hidden,
                    index: i
                  }
                })
              }
              return []
            }
          }
        },
        title: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(17, 24, 39, 0.95)',
          titleColor: '#f3f4f6',
          bodyColor: '#f3f4f6',
          borderColor: '#374151',
          borderWidth: 1,
          callbacks: {
            label: function(context) {
              const bucket = distributionData.value.buckets[context.dataIndex]
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = ((context.parsed / total) * 100).toFixed(1)
              return [
                `Gewinn/Verlust: ${context.parsed.toFixed(2)}€`,
                `Anteil: ${percentage}%`,
                `Anzahl Trades: ${bucket.count}`
              ]
            }
          }
        }
      }
    }

    const fetchData = async () => {
      try {
        loading.value = true
        error.value = null
        const response = await api.getProfitDistribution(props.fromDate, props.toDate)
        distributionData.value = response.data
      } catch (err) {
        console.error('Error fetching profit distribution:', err)
        error.value = 'Fehler beim Laden der Gewinn-Verteilung'
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchData()
    })

    // Watch for prop changes and reload data
    watch(() => [props.fromDate, props.toDate], () => {
      fetchData()
    })

    return {
      loading,
      error,
      chartData,
      chartOptions,
      pieChartData,
      pieChartOptions,
      chartType
    }
  }
}
</script>

<style scoped>
.profit-histogram {
  background: var(--bg-secondary);
  padding: 1.5rem;
  border-radius: var(--radius-md);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  margin-bottom: 2rem;
  border: 1px solid var(--border-color);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.profit-histogram h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.chart-toggle {
  display: flex;
  gap: 0.5rem;
}

.toggle-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.toggle-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.toggle-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.chart-container {
  min-height: 300px;
  height: 300px;
  position: relative;
  flex: 1;
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
