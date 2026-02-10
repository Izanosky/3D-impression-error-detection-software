<template>
  <header class="app-header">
    <router-link to="/" class="header-brand">
      <i class="pi pi-box"></i>
      <span class="brand-text">PrintErr</span>
    </router-link>

    <nav class="header-nav">
      <router-link to="/" class="nav-link" exact-active-class="nav-link--active">
        <i class="pi pi-home"></i>
        <span>Inicio</span>
      </router-link>
      <router-link to="/monitor" class="nav-link" active-class="nav-link--active">
        <i class="pi pi-desktop"></i>
        <span>Monitor</span>
      </router-link>
      <router-link to="/about" class="nav-link" active-class="nav-link--active">
        <i class="pi pi-info-circle"></i>
        <span>Acerca de</span>
      </router-link>
    </nav>

    <div class="header-actions">
      <span v-if="store.wsConnected" class="ws-indicator">
        <i class="pi pi-bolt"></i>
      </span>
      <Tag :value="store.status.connected ? 'Conectado' : 'Desconectado'" 
           :severity="store.status.connected ? 'success' : 'danger'" />
      <Button 
        icon="pi pi-cog" 
        severity="secondary" 
        text 
        rounded
        @click="store.showSettings = true"
      />
    </div>
  </header>
</template>

<script setup>
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import { usePrinterStore } from '../stores/printer'

const store = usePrinterStore()
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 64px;
  background: rgba(22, 33, 62, 0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--surface-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  font-size: 1.35rem;
  font-weight: 700;
  transition: opacity 0.2s;
}

.header-brand:hover {
  opacity: 0.85;
}

.header-brand i {
  font-size: 1.5rem;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-text {
  background: linear-gradient(90deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-nav {
  display: flex;
  gap: 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.25s ease;
}

.nav-link:hover {
  color: var(--text-color);
  background: rgba(99, 102, 241, 0.1);
}

.nav-link--active {
  color: #a855f7;
  background: rgba(168, 85, 247, 0.12);
}

.nav-link--active i {
  color: #a855f7;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.ws-indicator {
  color: #22c55e;
  animation: pulse-glow 2s infinite;
}

.ws-indicator i {
  font-size: 1rem;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 1rem;
  }

  .nav-link span {
    display: none;
  }

  .brand-text {
    display: none;
  }
}
</style>
