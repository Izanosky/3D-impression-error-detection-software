<template>
  <Card class="status-card">
    <template #title>
      <div class="card-header">
        <i class="pi pi-chart-bar"></i>
        <span>Estado de Impresión</span>
      </div>
    </template>
    <template #content>
      <!-- Estado -->
      <div class="status-item">
        <span class="label">Estado</span>
        <Tag :value="status.state" :severity="stateSeverity" />
      </div>

      <!-- Progreso -->
      <div class="status-item">
        <span class="label">Progreso</span>
        <div class="progress-container">
          <ProgressBar :value="Math.round(status.job?.progress || 0)" 
                       :showValue="true" />
        </div>
      </div>

      <!-- Archivo -->
      <div class="status-item">
        <span class="label">Archivo</span>
        <span class="value">{{ status.job?.file || 'Sin archivo' }}</span>
      </div>

      <!-- Temperaturas -->
      <div class="temperatures">
        <div class="temp-item">
          <i class="pi pi-sun"></i>
          <div class="temp-info">
            <span class="temp-label">Extrusor</span>
            <span class="temp-value">
              {{ formatTemp(status.temperatures?.tool0?.actual) }} / 
              {{ formatTemp(status.temperatures?.tool0?.target) }}
            </span>
          </div>
        </div>
        <div class="temp-item">
          <i class="pi pi-table"></i>
          <div class="temp-info">
            <span class="temp-label">Cama</span>
            <span class="temp-value">
              {{ formatTemp(status.temperatures?.bed?.actual) }} / 
              {{ formatTemp(status.temperatures?.bed?.target) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Tiempos -->
      <div class="times">
        <div class="time-item">
          <span class="label">Tiempo transcurrido</span>
          <span class="value">{{ formatTime(status.job?.time_elapsed) }}</span>
        </div>
        <div class="time-item">
          <span class="label">Tiempo restante</span>
          <span class="value">{{ formatTime(status.job?.time_remaining) }}</span>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { computed } from 'vue'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'

const props = defineProps({
  status: {
    type: Object,
    default: () => ({})
  }
})

const stateSeverity = computed(() => {
  const state = props.status.state?.toLowerCase() || ''
  if (state.includes('print')) return 'info'
  if (state.includes('paus')) return 'warning'
  if (state.includes('error')) return 'danger'
  if (state.includes('ready') || state.includes('operational')) return 'success'
  return 'secondary'
})

function formatTemp(temp) {
  if (temp === undefined || temp === null) return '--°C'
  return `${Math.round(temp)}°C`
}

function formatTime(seconds) {
  if (!seconds) return '--:--'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) {
    return `${h}h ${m}m`
  }
  return `${m}m ${s}s`
}
</script>

<style scoped>
.status-card {
  background: rgba(22, 33, 62, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid var(--surface-border);
  border-radius: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-header i {
  color: var(--primary-color);
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.label {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.value {
  color: var(--text-color);
  font-weight: 500;
  max-width: 60%;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.progress-container {
  width: 60%;
}

.temperatures {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.temp-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.temp-item i {
  font-size: 1.25rem;
  color: #f97316;
}

.temp-label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.temp-value {
  display: block;
  font-weight: 600;
  color: var(--text-color);
}

.times {
  padding-top: 0.75rem;
}

.time-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
}
</style>
