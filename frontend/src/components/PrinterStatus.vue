<template>
  <div class="status-panel">
    <div class="panel-header">
      <span>Estadísticas</span>
    </div>

    <div class="panel-content">
      <!-- Archivo -->
      <div class="status-group">
        <div class="info-box file-box" :title="status.job?.file || 'N/A'">
          <span class="info-label">Archivo en impresión:</span>
          <span class="info-value file-name">{{ status.job?.file || 'N/A' }}</span>
        </div>
      </div>

      <!-- Temperaturas -->
      <div class="temp-grid">
        <div class="status-group">
          <div class="info-box temp-box">
            <div class="temp-label-group">
              <span>Temperatura</span>
              <span>del extrusor:</span>
            </div>
            <span class="temp-value">{{ formatTemp(status.temperatures?.tool0?.actual) }}</span>
          </div>
        </div>

        <div class="status-group">
          <div class="info-box temp-box">
            <div class="temp-label-group">
              <span>Temperatura</span>
              <span>de la cama:</span>
            </div>
            <span class="temp-value">{{ formatTemp(status.temperatures?.bed?.actual) }}</span>
          </div>
        </div>
      </div>

      <!-- Tiempos -->
      <div class="status-group">
        <div class="info-box time-box">
          <div class="time-row">
            <span>Tiempo de impresión:</span>
            <span>{{ formatTime(status.job?.time_elapsed) }}</span>
          </div>
          <div class="time-row">
            <span>Tiempo restante:</span>
            <span>{{ formatTime(status.job?.time_remaining) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  status: {
    type: Object,
    default: () => ({})
  }
})

function formatTemp(temp) {
  if (temp === undefined || temp === null) return '-- °C'
  return `${Math.round(temp)} °C`
}

function formatTime(seconds) {
  if (!seconds) return '--:--'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  // Format MM:SS or HH:MM if > 1h
  const pad = (n) => n.toString().padStart(2, '0')
  if (h > 0) {
    return `${h}:${pad(m)}:${pad(s)}` // Example format, adapt to screenshot preference
  }
  return `${pad(m)}:${pad(s)}`
}
</script>

<style scoped>
.status-panel {
  background: var(--surface-card, #0f1028);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 14px;
  padding: 0;
  color: #fff;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.panel-header {
  text-align: center;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.03);
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.25rem;
  flex: 1;
}

.status-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.status-group label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
  text-align: center;
}

.file-box {
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  cursor: default;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.45);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.info-value {
  font-weight: 600;
  font-size: 0.95rem;
  color: #fff;
}

.file-name {
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: right;
}

.temp-label-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1.3;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.45);
}

.temp-box {
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 0.5rem;
}

.temp-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
}

.info-box {
  background: rgba(255, 255, 255, 0.04);
  color: #fff;
  padding: 0.65rem 1rem;
  border-radius: 10px;
  font-weight: 500;
  min-height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  border: 1px solid rgba(255, 255, 255, 0.07);
  transition: border-color 0.2s;
}

.info-box:hover {
  border-color: rgba(99, 102, 241, 0.2);
}

.info-box.centered {
  justify-content: center;
}

.temp-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.time-box {
  flex-direction: column;
  align-items: stretch;
  gap: 0.4rem;
  padding: 0.75rem 1rem;
}

.time-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

.time-row span:last-child {
  font-weight: 600;
  color: #fff;
  font-variant-numeric: tabular-nums;
}
</style>
