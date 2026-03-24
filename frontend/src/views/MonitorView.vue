<template>
  <div class="monitor-view">
    <main class="monitor-main">
      <h1 class="page-title">Progreso de la impresión</h1>

      <div class="monitor-content">
        <!-- Top Row: 3 Panels -->
        <div class="top-panels">
          <!-- Col 1: Estadísticas -->
          <div class="panel-wrapper">
            <PrinterStatus :status="store.status" />
          </div>

          <!-- Col 2: Propiedades -->
          <div class="panel-wrapper">
            <ControlPanel :is-printing="store.isPrinting" :is-paused="store.isPaused" :has-file="store.hasFile"
              :uploading="store.uploading" :files="store.gcodeFiles" :current-file="store.status.job?.file || ''"
              @pause="store.pausePrint" @resume="store.resumePrint" @cancel="store.cancelPrint"
              @start="store.startPrint" @upload="store.uploadGcode" @select-file="store.selectFile"
              @refresh-files="store.fetchFiles" />
          </div>

          <!-- Col 3: Sistema -->
          <div class="panel-wrapper system-wrapper">
            <div class="sidebar-panel connection-panel">
              <div class="panel-header">
                <span>Sistema</span>
              </div>
              <div class="panel-content">
                <!-- Connection Status (2 steps) -->
                <div class="connection-status">
                  <div class="status-row">
                    <span class="status-dot" :class="store.wsConnected ? 'dot-green' : 'dot-red'"></span>
                    <span class="status-text" :class="store.wsConnected ? 'text-green' : 'text-red'">Backend</span>
                  </div>
                  <div class="status-row">
                    <span class="status-dot" :class="store.status.connected ? 'dot-green' : 'dot-red'"></span>
                    <span class="status-text"
                      :class="store.status.connected ? 'text-green' : 'text-red'">Impresora</span>
                  </div>
                </div>

                <div class="ip-group">
                  <label class="input-label">IP:</label>
                  <div class="ip-input-wrapper">
                    <input type="text" class="ip-input" v-model="ipAddress" placeholder="192.168.0.1"
                      :disabled="store.isPrinting || store.isPaused" />
                    <i class="pi pi-wifi ip-icon"></i>
                  </div>
                </div>

                <button class="connect-btn" @click="updateIp" :disabled="store.isPrinting || store.isPaused">
                  Conectar
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Bottom Row: Camera -->
        <div class="camera-section">
          <CameraView :stream-url="store.streamUrl" :detections="store.detections" />
        </div>
      </div>
    </main>
    <Toast />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import CameraView from '../components/CameraView.vue'
import PrinterStatus from '../components/PrinterStatus.vue'
import ControlPanel from '../components/ControlPanel.vue'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { usePrinterStore } from '../stores/printer'

const store = usePrinterStore()
const ipAddress = ref('')
const toast = useToast()

onMounted(() => {
  // Sync IP from store
  ipAddress.value = store.backendUrl || localStorage.getItem('printer_monitor_backend_url') || ''
})

// Update local ref if store changes
watch(() => store.backendUrl, (newUrl) => {
  if (newUrl) ipAddress.value = newUrl
})

// Watch for auto-cancel message
watch(() => store.autoCancelledMessage, (message) => {
  if (message) {
    toast.add({
      severity: 'error',
      summary: 'Impresión cancelada',
      detail: message,
      life: 5000
    })
    // Clear the message after showing
    store.clearAutoCancelledMessage()
  }
})

async function updateIp() {
  let url = ipAddress.value.trim()
  if (!url) return

  url = url.replace(/^https?:\/\//, '')

  // Save the URL
  store.onSettingsSaved(url)
  // Explicitly connect
  await store.connect()
}
</script>

<style scoped>
.monitor-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 1.5rem;
  letter-spacing: -0.25px;
}

.monitor-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.top-panels {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.25rem;
  align-items: stretch;
  min-height: 320px;
}

.panel-wrapper {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.camera-section {
  background: var(--surface-card, #0f1028);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 460px;
  flex: 1;
}

.sidebar-panel {
  background: var(--surface-card, #0f1028);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 14px;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
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
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1;
}

.ip-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.input-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.ip-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.ip-input {
  width: 100%;
  padding: 0.65rem 2.5rem 0.65rem 1rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 500;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.ip-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.ip-input:focus {
  border-color: var(--primary-color, #6366f1);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
}

.ip-icon {
  position: absolute;
  right: 0.85rem;
  color: rgba(255, 255, 255, 0.3);
  font-size: 1rem;
}

.connect-btn {
  background: var(--primary-color, #6366f1);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0.7rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  width: 100%;
  margin-top: auto;
}

.connect-btn:hover {
  background: #4f46e5;
}

.connect-btn:active {
  transform: scale(0.98);
}

.connect-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.ip-input:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Connection Status */
.connection-status {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-green {
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
}

.dot-red {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.5);
}

.status-text {
  font-size: 0.8rem;
  font-weight: 500;
}

.text-green {
  color: #86efac;
}

.text-red {
  color: #fca5a5;
}

@media (max-width: 1200px) {
  .top-panels {
    grid-template-columns: 1fr;
    gap: 1.25rem;
    min-height: auto;
  }
}

@media (max-width: 900px) {
  .monitor-view {
    padding: 1.25rem;
  }

  .camera-section {
    min-height: 280px;
  }
}
</style>
