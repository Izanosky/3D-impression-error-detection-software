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
        <span v-if="wsConnected" class="ws-indicator">
          <i class="pi pi-bolt"></i>
        </span>
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
const wsConnected = ref(false)

let websocket = null

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

const isPrinting = computed(() => 
  status.value.state?.toLowerCase().includes('print')
)

const isPaused = computed(() => 
  status.value.state?.toLowerCase().includes('paus')
)

function getWsUrl() {
  let base = backendUrl.value
  if (!base) return null
  
  // Limpiar protocolo HTTP si existe
  base = base.replace(/^https?:\/\//, '')
  
  return `ws://${base}/ws`
}

function connectWebSocket() {
  const wsUrl = getWsUrl()
  if (!wsUrl) return
  
  console.log('Conectando a WebSocket:', wsUrl)
  
  websocket = new WebSocket(wsUrl)
  
  websocket.onopen = () => {
    console.log('WebSocket conectado')
    wsConnected.value = true
  }
  
  websocket.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data)
      
      if (message.type === 'update') {
        // Actualizar datos desde el servidor
        if (message.data.status) {
          status.value = message.data.status
        }
        if (message.data.detections) {
          detections.value = message.data.detections
        }
        if (message.data.snapshot) {
          snapshotUrl.value = message.data.snapshot
        }
      } else if (message.type === 'command_result') {
        console.log(`Comando ${message.action}: ${message.success ? 'OK' : 'Error'}`)
      }
    } catch (error) {
      console.error('Error procesando mensaje WebSocket:', error)
    }
  }
  
  websocket.onclose = () => {
    console.log('WebSocket desconectado, reconectando en 3s...')
    wsConnected.value = false
    status.value.connected = false
    
    // Reconectar automáticamente
    setTimeout(() => {
      if (backendUrl.value) {
        connectWebSocket()
      }
    }, 3000)
  }
  
  websocket.onerror = (error) => {
    console.error('Error WebSocket:', error)
    wsConnected.value = false
  }
}

function disconnectWebSocket() {
  if (websocket) {
    websocket.close()
    websocket = null
  }
}

function sendCommand(action) {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.send(JSON.stringify({ action }))
  }
}

function pausePrint() {
  sendCommand('pause')
}

function resumePrint() {
  sendCommand('resume')
}

function onSettingsSaved(url) {
  backendUrl.value = url.replace(/^https?:\/\//, '')
  isFirstTime.value = false
  
  // Desconectar WebSocket anterior y reconectar
  disconnectWebSocket()
  connectWebSocket()
}

onMounted(() => {
  // Verificar si hay URL guardada
  const savedUrl = localStorage.getItem(STORAGE_KEY)
  
  if (savedUrl) {
    backendUrl.value = savedUrl
    connectWebSocket()
  } else {
    // Primera vez: mostrar modal obligatorio
    isFirstTime.value = true
    showSettings.value = true
  }
})

onUnmounted(() => {
  disconnectWebSocket()
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

.ws-indicator {
  color: #22c55e;
  animation: pulse 2s infinite;
}

.ws-indicator i {
  font-size: 1rem;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
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
