<template>
  <div class="flex flex-column p-4 md:p-6 mx-auto w-full gap-4" style="max-width: 1400px;">

    <h1 class="text-3xl font-bold text-white m-0 flex align-items-center gap-3 border-bottom-1 surface-border pb-3">
      <i class="pi pi-print text-primary" style="font-size: 2rem"></i>
      Monitorización de Impresión
    </h1>

    <!-- Main Content (Accordions) -->
    <div class="flex flex-column gap-4">

      <!-- Desplegable 1: Configuración -->
      <Panel toggleable :collapsed="configCollapsed" @update:collapsed="configCollapsed = $event" class="shadow-4">
        <template #header>
          <div class="text-xl font-semibold flex align-items-center gap-2 transition-colors duration-200"
            :class="!configCollapsed ? 'text-primary' : 'text-white'">
            <i class="pi pi-cog"></i> Configuración
          </div>
        </template>
        <div class="grid pt-3">

          <!-- Sistema -->
          <div
            class="col-12 lg:col-6 flex flex-column gap-3 border-right-none lg:border-right-1 surface-border pr-0 lg:pr-4">
            <div class="text-lg font-semibold flex align-items-center gap-2 mb-2">
              <i class="pi pi-desktop text-color-secondary"></i> Sistema
            </div>

            <div class="flex flex-column gap-2 bg-white-alpha-10 p-3 border-round">
              <div class="flex align-items-center justify-content-between">
                <span class="font-medium text-base text-color-secondary">Backend</span>
                <Tag :severity="store.wsConnected ? 'success' : 'danger'"
                  :value="store.wsConnected ? 'Conectado' : 'Desconectado'" />
              </div>
              <div class="flex align-items-center justify-content-between mt-1">
                <span class="font-medium text-base text-color-secondary">Impresora</span>
                <Tag :severity="store.status.connected ? 'success' : 'danger'"
                  :value="store.status.connected ? 'Conectada' : 'Desconectada'" />
              </div>
            </div>

            <div class="flex flex-column gap-1 mt-auto pt-2">
              <span class="text-xs font-semibold text-color-secondary uppercase">Conexión IP</span>
              <InputGroup>
                <InputText v-model="ipAddress" placeholder="Ej: 192.168.1.100" class="bg-white-alpha-10 w-full"
                  :disabled="store.isPrinting || store.isPaused" />
                <Button label="Conectar" icon="pi pi-bolt" @click="updateIp"
                  :disabled="store.isPrinting || store.isPaused || !ipAddress.trim()" />
              </InputGroup>
            </div>
          </div>

          <!-- Propiedades -->
          <div class="col-12 lg:col-6 flex flex-column gap-3 pt-4 lg:pt-0 pl-0 lg:pl-4">
            <div class="text-lg font-semibold flex align-items-center gap-2 mb-2">
              <i class="pi pi-sliders-h text-color-secondary"></i> Propiedades
            </div>

            <div class="flex flex-column gap-1">
              <span class="text-xs font-semibold text-color-secondary uppercase">Seleccionar Archivos</span>
              <Select v-model="selectedFile" :options="store.gcodeFiles" optionLabel="name" optionValue="name"
                placeholder="Seleccionar archivo..." class="w-full"
                :disabled="store.isPrinting || store.isPaused || store.uploading" @change="onFileChange" />
            </div>

            <div class="flex flex-column gap-1">
              <span class="text-xs font-semibold text-color-secondary uppercase">Subir Archivo</span>
              <FileUpload mode="basic" auto customUpload @uploader="onFileUploadPrime" accept=".gcode,.gco,.g"
                :chooseLabel="store.uploading ? 'Subiendo...' : 'Subir Archivo'"
                :chooseIcon="store.uploading ? 'pi pi-spin pi-spinner' : 'pi pi-upload'"
                :disabled="store.isPrinting || store.isPaused || store.uploading" class="w-full"
                pt:chooseButton="w-full p-button-secondary p-button-outlined" />
            </div>

            <div class="flex flex-column gap-2 mt-auto pt-4">
              <Button v-if="!store.isPrinting && !store.isPaused" label="Iniciar Impresión" icon="pi pi-play"
                :disabled="!store.hasFile || store.uploading" @click="store.startPrint" />
              <Button v-else-if="store.isPrinting && !store.isPaused" label="Pausar Impresión" icon="pi pi-pause"
                severity="warning" @click="store.pausePrint" />
              <Button v-else label="Reanudar Impresión" icon="pi pi-play" @click="store.resumePrint" />
              <Button label="Cancelar Impresión" icon="pi pi-times" severity="danger" outlined
                :disabled="!store.isPrinting && !store.isPaused" @click="store.cancelPrint" />
            </div>
          </div>

        </div>
      </Panel>

      <!-- Desplegable 2: Monitorización (Cámara y Estadísticas) -->
      <Panel toggleable :collapsed="monitorCollapsed" @update:collapsed="monitorCollapsed = $event" class="shadow-4">
        <template #header>
          <div class="text-xl font-semibold flex align-items-center gap-2 transition-colors duration-200"
            :class="!monitorCollapsed ? 'text-primary' : 'text-white'">
            <i class="pi pi-video"></i> Seguimiento en Vivo
          </div>
        </template>
        <div class="grid pt-3">

          <!-- Cámara -->
          <div class="col-12 lg:col-8 flex flex-column gap-3">
            <div class="text-lg font-semibold flex align-items-center gap-2">
              <i class="pi pi-camera text-color-secondary"></i> Cámara
            </div>

            <div
              class="relative w-full flex align-items-center justify-content-center bg-black overflow-hidden border-round-xl border-1 surface-border shadow-4 p-2"
              style="aspect-ratio: 16/9;">
              <!-- MJPEG Stream -->
              <img ref="cameraImg" v-if="store.streamUrl" :src="store.streamUrl" crossorigin="anonymous"
                alt="Vista de cámara" class="w-full h-full block border-round" style="object-fit: contain;"
                @error="handleImageError" />
              <div v-else
                class="text-color-secondary text-xl flex flex-column align-items-center justify-content-center w-full h-full gap-3">
                <i class="pi pi-camera" style="font-size: 4rem"></i>
                <span>Cámara no disponible</span>
              </div>

              <!-- Hidden Canvas for Inference -->
              <canvas ref="captureCanvas" class="hidden"></canvas>

              <!-- Detection Overlay -->
              <div v-if="store.detections?.has_errors" class="absolute top-0 right-0 p-3 z-5">
                <Tag value="¡Error Detectado!" severity="danger" icon="pi pi-exclamation-triangle"
                  class="text-lg px-3 py-2 shadow-4 animate-pulse" />
              </div>
            </div>
          </div>

          <!-- Estadísticas -->
          <div
            class="col-12 lg:col-4 flex flex-column gap-3 pt-4 lg:pt-0 pl-0 lg:pl-4 border-left-none lg:border-left-1 surface-border">
            <div class="text-lg font-semibold flex align-items-center gap-2">
              <i class="pi pi-chart-bar text-color-secondary"></i> Estadísticas
            </div>

            <div class="flex flex-column gap-1 bg-white-alpha-10 p-3 border-round">
              <span class="text-color-secondary uppercase text-xs font-semibold">Archivo Actual</span>
              <span class="font-medium text-overflow-ellipsis overflow-hidden white-space-nowrap"
                :title="store.status.job?.file">{{ store.status.job?.file || 'Ningún archivo' }}</span>
            </div>

            <div class="flex gap-3">
              <div
                class="flex-1 flex flex-column align-items-center bg-white-alpha-10 p-3 border-round gap-1 justify-content-center">
                <span class="text-color-secondary uppercase text-xs font-semibold text-center">Extrusor</span>
                <span class="text-xl font-bold text-orange-400">{{ formatTemp(store.status.temperatures?.tool0?.actual)
                  }}</span>
              </div>
              <div
                class="flex-1 flex flex-column align-items-center bg-white-alpha-10 p-3 border-round gap-1 justify-content-center">
                <span class="text-color-secondary uppercase text-xs font-semibold text-center">Cama Caliente</span>
                <span class="text-xl font-bold text-red-400">{{ formatTemp(store.status.temperatures?.bed?.actual)
                  }}</span>
              </div>
            </div>

            <div class="flex flex-column gap-3 bg-white-alpha-10 p-3 border-round mt-auto">
              <!-- Progreso -->
              <div class="flex justify-content-between align-items-center">
                <span class="text-color-secondary text-xs font-semibold uppercase">Progreso</span>
                <span class="font-bold text-primary">{{ Math.round(store.status.progress?.completion || 0) }}%</span>
              </div>
              <ProgressBar :value="store.status.progress?.completion || 0" :showValue="false"
                style="height: 8px; margin-top: -8px;" />

              <!-- Tiempos -->
              <div class="flex justify-content-between border-top-1 surface-border pt-2">
                <div class="flex flex-column">
                  <span class="text-xs text-color-secondary">Transcurrido</span>
                  <span class="font-mono font-medium">{{ formatTime(store.status.job?.time_elapsed) }}</span>
                </div>
                <div class="flex flex-column text-right">
                  <span class="text-xs text-color-secondary">Restante</span>
                  <span class="font-mono font-medium">{{ formatTime(store.status.job?.time_remaining) }}</span>
                </div>
              </div>
            </div>

          </div>

        </div>
      </Panel>

    </div>
    <Toast />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { usePrinterStore } from '../stores/printer'
import { detectErrorsYolov8 } from '../services/inferenceService'
import { useToast } from 'primevue/usetoast'

import Panel from 'primevue/panel'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'
import Button from 'primevue/button'

import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import InputGroup from 'primevue/inputgroup'
import FileUpload from 'primevue/fileupload'
import Toast from 'primevue/toast'

const store = usePrinterStore()
const toast = useToast()

// Accordion Setup
const configCollapsed = ref(false)
const monitorCollapsed = ref(true)

watch(() => store.isPrinting, (newVal) => {
  if (newVal) {
    configCollapsed.value = true
    monitorCollapsed.value = false
  }
})

const ipAddress = ref('')
const selectedFile = ref('')

// Camera & Inference Logic
const cameraImg = ref(null)
const captureCanvas = ref(null)
let inferenceInterval = null
let isProcessing = false

onMounted(() => {
  // Sync IP
  ipAddress.value = store.backendUrl || localStorage.getItem('printer_monitor_backend_url') || ''

  // Setup inference loop
  inferenceInterval = setInterval(async () => {
    if (!cameraImg.value || !captureCanvas.value || !store.streamUrl || isProcessing) return
    if (!store.isPrinting) return

    isProcessing = true
    try {
      const videoEl = cameraImg.value
      const canvasEl = captureCanvas.value

      canvasEl.width = videoEl.naturalWidth || 640
      canvasEl.height = videoEl.naturalHeight || 480

      if (canvasEl.width === 0 || canvasEl.height === 0) return

      const ctx = canvasEl.getContext('2d')
      ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height)

      const captureDataUrl = canvasEl.toDataURL('image/jpeg', 0.8)

      const result = await detectErrorsYolov8(captureDataUrl)
      store.detections.has_errors = result.has_errors

      if (result.has_errors) {
        console.warn('[Frontend-AI] Error detectado desde stream local, auto-cancelando impresión...')
        store.cancelPrint()
        store.autoCancelledMessage = 'Impresión cancelada automáticamente por detección de errores (Inferencia Local).'
      }
    } catch (err) {
      console.error('[Frontend-AI] Error capturando frame de stream:', err)
    } finally {
      isProcessing = false
    }
  }, 2000)
})

onUnmounted(() => {
  if (inferenceInterval) clearInterval(inferenceInterval)
})

function handleImageError(e) {
  e.target.style.display = 'none'
  const container = e.target.parentElement
  if (container) {
    const fallback = container.querySelector('.text-color-secondary')
    if (fallback) fallback.style.display = 'flex'
  }
}

// Watchers
watch(() => store.backendUrl, (newUrl) => {
  if (newUrl) ipAddress.value = newUrl
})

watch(() => store.status.job?.file, (val) => {
  if (val && val !== 'Sin archivo') {
    selectedFile.value = val
  }
}, { immediate: true })

watch(() => store.autoCancelledMessage, (message) => {
  if (message) {
    toast.add({ severity: 'error', summary: 'Impresión cancelada', detail: message, life: 5000 })
    store.clearAutoCancelledMessage()
  }
})

// Methods
async function updateIp() {
  let url = ipAddress.value.trim()
  if (!url) return
  url = url.replace(/^https?:\/\//, '')
  store.onSettingsSaved(url)
  await store.connect()
}

function onFileUploadPrime(event) {
  const file = event.files[0]
  if (file) {
    store.uploadGcode(file)
  }
}

function onFileChange(event) {
  if (event.value) {
    store.selectFile(event.value)
  }
}

function formatTemp(temp) {
  if (temp === undefined || temp === null) return '-- °C'
  return `${Math.round(temp)} °C`
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '--:--'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const pad = (n) => n.toString().padStart(2, '0')
  return h > 0 ? `${h}h ${pad(m)}m` : `${pad(m)}m`
}
</script>

<style scoped>
/* Scoped overrides if needed, relying mostly on PrimeFlex styling */
</style>
