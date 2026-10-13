import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import RiskManagement from './views/RiskManagement.vue'
import Trades from './views/Trades.vue'
import Journal from './views/Journal.vue'
import OvernightFees from './views/OvernightFees.vue'
import Import from './views/Import.vue'
import Expenses from './views/Expenses.vue'
import Settings from './views/Settings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Dashboard', component: Dashboard, meta: { title: 'Overview' } },
    { path: '/risk-management', name: 'RiskManagement', component: RiskManagement, meta: { title: 'Risk Management' } },
    { path: '/trades', name: 'Trades', component: Trades, meta: { title: 'Trading History' } },
    { path: '/journal', name: 'Journal', component: Journal, meta: { title: 'Trading Journal' } },
    { path: '/overnight', name: 'OvernightFees', component: OvernightFees, meta: { title: 'Overnight Financing Fees' } },
    { path: '/import', name: 'Import', component: Import, meta: { title: 'Import Data' } },
    { path: '/expenses', name: 'Expenses', component: Expenses, meta: { title: 'Trading Expenses' } },
    { path: '/settings', name: 'Settings', component: Settings, meta: { title: 'Settings' } }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app')
