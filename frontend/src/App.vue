<template>
  <div class="app-container dark-mode">
    <!-- Modal de configuración -->
    <SettingsDialog 
      v-model="showSettings" 
      :isFirstTime="isFirstTime"
      @saved="onSettingsSaved"
    />

    <header class="app-header">
      <h1><i class="pi pi-box"></i> Monitor de Impresora 3D</h1>
      <div class="header-actions">
        <Button 
          icon="pi pi-cog" 
          severity="secondary" 
          text 
          rounded
          @click="showSettings = true"
          v-tooltip="'Configuración'"
        />
        <Tag :value="status.connected ? 'Conectado' : 'Desconectado'" 
             :severity="status.connected ? 'success' : 'danger'" />
      </div>
    </header>

    <main class="app-main">
      <!-- Panel de cámara -->
      <CameraView :snapshot-url="snapshotUrl" :detections="detections" />

      <!-- Panel lateral -->
      <aside class="sidebar">
        <PrinterStatus :status="status" />
        <ControlPanel 
          :is-printing="isPrinting"
          :is-paused="isPaused"
          @pause="pausePrint"
          @resume="resumePrint"
        />
      </aside>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import CameraView from './components/CameraView.vue'
import PrinterStatus from './components/PrinterStatus.vue'
import ControlPanel from './components/ControlPanel.vue'
import SettingsDialog from './components/SettingsDialog.vue'

const STORAGE_KEY = 'printer_monitor_backend_url'

const showSettings = ref(false)
const isFirstTime = ref(false)
const backendUrl = ref('')

const status = ref({
  connected: false,
  state: 'Desconocido',
  temperatures: { bed: {}, tool0: {} },
  job: { file: '', progress: 0, time_elapsed: 0, time_remaining: 0 }
})

const detections = ref({
  has_errors: false,
  total_detections: 0,
  classes: {}
})

const snapshotUrl = ref('')
let pollInterval = null

const isPrinting = computed(() => 
  status.value.state?.toLowerCase().includes('print')
)

const isPaused = computed(() => 
  status.value.state?.toLowerCase().includes('paus')
)

function getApiUrl(endpoint) {
  if (!backendUrl.value) return endpoint
  let base = backendUrl.value
  if (!base.startsWith('http://') && !base.startsWith('https://')) {
    base = 'http://' + base
  }
  return `${base}${endpoint}`
}

async function fetchStatus() {
  if (!backendUrl.value) return
  
  try {
    const response = await fetch(getApiUrl('/api/status'))
    if (response.ok) {
      status.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching status:', error)
    status.value.connected = false
  }
}

async function fetchDetections() {
  if (!backendUrl.value) return
  
  try {
    const response = await fetch(getApiUrl('/api/detections'))
    if (response.ok) {
      detections.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching detections:', error)
  }
}

function updateSnapshot() {
  if (!backendUrl.value) return
  snapshotUrl.value = getApiUrl(`/api/snapshot?t=${Date.now()}`)
}

async function pausePrint() {
  try {
    await fetch(getApiUrl('/api/pause'), { method: 'POST' })
    await fetchStatus()
  } catch (error) {
    console.error('Error pausing:', error)
  }
}

async function resumePrint() {
  try {
    await fetch(getApiUrl('/api/resume'), { method: 'POST' })
    await fetchStatus()
  } catch (error) {
    console.error('Error resuming:', error)
  }
}

function onSettingsSaved(url) {
  backendUrl.value = url.replace(/^https?:\/\//, '')
  isFirstTime.value = false
  startPolling()
}

function startPolling() {
  // Limpiar intervalo anterior
  if (pollInterval) {
    clearInterval(pollInterval)
  }
  
  // Fetch inicial
  fetchStatus()
  fetchDetections()
  updateSnapshot()
  
  // Polling cada 3 segundos
  pollInterval = setInterval(() => {
    fetchStatus()
    fetchDetections()
    updateSnapshot()
  }, 3000)
}

onMounted(() => {
  // Verificar si hay URL guardada
  const savedUrl = localStorage.getItem(STORAGE_KEY)
  
  if (savedUrl) {
    backendUrl.value = savedUrl
    startPolling()
  } else {
    // Primera vez: mostrar modal obligatorio
    isFirstTime.value = true
    showSettings.value = true
  }
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: rgba(22, 33, 62, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--surface-border);
}

.app-header h1 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.app-main {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 1.5rem;
  padding: 1.5rem 2rem;
  flex: 1;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

@media (max-width: 1024px) {
  .app-main {
    grid-template-columns: 1fr;
  }
}
</style>
