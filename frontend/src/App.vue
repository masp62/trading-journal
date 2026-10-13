<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">
        <h1>📈 Trading Journal</h1>
        <span class="breadcrumb" v-if="$route.meta.title"> > {{ $route.meta.title }}</span>
      </div>
      <div class="nav-links">
        <router-link to="/">Dashboard</router-link>
        <router-link to="/market-data">Market Data</router-link>
        <router-link to="/risk-management">Risk Management</router-link>
        <router-link to="/trades">Trades</router-link>
        <router-link to="/journal">Journal</router-link>
        <router-link to="/overnight">Overnight Fees</router-link>
        <router-link to="/import">Import</router-link>
        <router-link to="/expenses">Expenses</router-link>
        <router-link to="/settings">⚙️ Settings</router-link>
      </div>
    </nav>
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
:root {
  --bg-primary: #0f1419;
  --bg-secondary: #1a1f2e;
  --bg-tertiary: #232935;
  --bg-hover: #2a3142;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;
  --border-color: #30363d;
  --accent-primary: #58a6ff;
  --accent-hover: #409eff;
  --success: #3fb950;
  --success-bg: rgba(63, 185, 80, 0.15);
  --danger: #f85149;
  --danger-bg: rgba(248, 81, 73, 0.15);
  --warning: #d29922;
  --warning-bg: rgba(210, 153, 34, 0.15);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
}

#app {
  min-height: 100vh;
}

.navbar {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-md);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.nav-brand h1 {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--success));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: inline;
}

.nav-brand .breadcrumb {
  color: var(--text-muted);
  font-size: 1.2rem;
  font-weight: 600;
  margin-left: 0.5rem;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-links a {
  color: var(--text-secondary);
  text-decoration: none;
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 0.95rem;
}

.nav-links a:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.nav-links a.router-link-active {
  background: rgba(88, 166, 255, 0.15);
  color: var(--accent-primary);
  font-weight: 600;
}

.container {
  max-width: 2400px;
  margin: 0 auto;
  padding: 2rem 4rem;
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
}

.card:hover {
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-lg);
}

.card h2 {
  margin-bottom: 1rem;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.5rem;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-primary {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.btn-primary:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
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

.btn-success {
  background: var(--success);
  color: white;
  border-color: var(--success);
}

.btn-success:hover {
  background: #56d364;
  border-color: #56d364;
}

.btn-info {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.btn-info:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

thead {
  background: var(--bg-tertiary);
  border-bottom: 2px solid var(--border-color);
}

th, td {
  padding: 0.85rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

td {
  color: var(--text-secondary);
}

tbody tr {
  transition: background 0.2s ease;
}

tbody tr:hover {
  background: var(--bg-hover);
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 1rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
  font-family: inherit;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  padding: 0.875rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-primary), var(--success));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card h3 {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-bottom: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  font-weight: 600;
}

.stat-card .value {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  font-feature-settings: 'tnum';
  font-variant-numeric: tabular-nums;
}

.stat-card .value.positive {
  color: var(--success);
}

.stat-card .value.negative {
  color: var(--danger);
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.error {
  background: var(--danger-bg);
  color: var(--danger);
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--danger);
  font-weight: 500;
}
</style>
