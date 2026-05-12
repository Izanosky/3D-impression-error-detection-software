<template>
  <div class="flex flex-column p-4 md:p-6 mx-auto w-full gap-4" style="max-width: 1400px;">

    <h1 class="text-3xl font-bold text-white m-0 flex align-items-center gap-3 border-bottom-1 surface-border pb-3">
      <i class="pi pi-print text-primary" style="font-size: 2rem"></i>
      Monitorización de Impresión
    </h1>

    <div class="flex flex-column gap-4">

      <!-- Panel de Configuración -->
      <Panel toggleable :collapsed="configColapsado" @update:collapsed="configColapsado = $event" class="shadow-4">
        <template #header>
          <div class="text-xl font-semibold flex align-items-center gap-2 transition-colors duration-200"
            :class="!configColapsado ? 'text-primary' : 'text-white'">
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
                <Tag :severity="store.wsConectado ? 'success' : 'danger'"
                  :value="store.wsConectado ? 'Conectado' : 'Desconectado'" />
              </div>
              <div class="flex align-items-center justify-content-between mt-1">
                <span class="font-medium text-base text-color-secondary">Impresora</span>
                <Tag :severity="store.estado.connected ? 'success' : 'danger'"
                  :value="store.estado.connected ? 'Conectada' : 'Desconectada'" />
              </div>
            </div>

            <div class="flex flex-column gap-1 mt-auto pt-2">
              <span class="text-xs font-semibold text-color-secondary uppercase">Conexión IP</span>
              <InputGroup>
                <InputText v-model="direccionIp" placeholder="Ej: 192.168.1.100" class="bg-white-alpha-10 w-full"
                  :disabled="store.estaImprimiendo || store.estaPausada" />
                <Button label="Conectar" icon="pi pi-bolt" @click="actualizarIp"
                  :disabled="store.estaImprimiendo || store.estaPausada || !direccionIp.trim()" />
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
              <Select v-model="archivoSeleccionado" :options="store.archivosGcode" optionLabel="name" optionValue="name"
                placeholder="Seleccionar archivo..." class="w-full"
                :disabled="store.estaImprimiendo || store.estaPausada || store.subiendo" @change="alCambiarArchivo" />
            </div>

            <div class="flex flex-column gap-1">
              <span class="text-xs font-semibold text-color-secondary uppercase">Subir Archivo</span>
              <FileUpload mode="basic" auto customUpload @uploader="alSubirArchivo" accept=".gcode,.gco,.g"
                :chooseLabel="store.subiendo ? 'Subiendo...' : 'Subir Archivo'"
                :chooseIcon="store.subiendo ? 'pi pi-spin pi-spinner' : 'pi pi-upload'"
                :disabled="store.estaImprimiendo || store.estaPausada || store.subiendo" class="w-full"
                pt:chooseButton="w-full p-button-secondary p-button-outlined" />
            </div>

            <div class="flex flex-column gap-2 mt-auto pt-4">
              <Button v-if="!store.estaImprimiendo && !store.estaPausada" label="Iniciar Impresión" icon="pi pi-play"
                :disabled="!store.tieneArchivo || store.subiendo" @click="store.iniciarImpresion" />
              <Button v-else-if="store.estaImprimiendo && !store.estaPausada" label="Pausar Impresión"
                icon="pi pi-pause" severity="warning" @click="store.pausarImpresion" />
              <Button v-else label="Reanudar Impresión" icon="pi pi-play" @click="store.reanudarImpresion" />
              <Button label="Cancelar Impresión" icon="pi pi-times" severity="danger" outlined
                :disabled="!store.estaImprimiendo && !store.estaPausada" @click="store.cancelarImpresion" />
            </div>
          </div>

        </div>
      </Panel>

      <!-- Panel de Seguimiento en Vivo -->
      <Panel toggleable :collapsed="monitorColapsado" @update:collapsed="monitorColapsado = $event" class="shadow-4">
        <template #header>
          <div class="text-xl font-semibold flex align-items-center gap-2 transition-colors duration-200"
            :class="!monitorColapsado ? 'text-primary' : 'text-white'">
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
              <!-- MJPEG Stream de la cámara -->
              <img ref="imagenCamara" v-if="store.urlStream" :src="store.urlStream" crossorigin="anonymous"
                alt="Vista de cámara" class="w-full h-full block border-round" style="object-fit: contain;"
                @error="alErrorImagen" />
              <div v-else
                class="text-color-secondary text-xl flex flex-column align-items-center justify-content-center w-full h-full gap-3">
                <i class="pi pi-camera" style="font-size: 4rem"></i>
                <span>Cámara no disponible</span>
              </div>

              <!-- Canvas oculto para capturar frames de la cámara -->
              <canvas ref="canvasCaptura" class="hidden"></canvas>

              <!-- Alerta de error detectado por la IA -->
              <div v-if="store.detecciones?.has_errors" class="absolute top-0 right-0 p-3 z-5">
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
                :title="store.estado.job?.file">{{ store.estado.job?.file || 'Ningún archivo' }}</span>
            </div>

            <div class="flex gap-3 my-auto">
              <div
                class="flex-1 flex flex-column align-items-center bg-white-alpha-10 p-3 border-round gap-1 justify-content-center">
                <span class="text-color-secondary uppercase text-xs font-semibold text-center">Extrusor</span>
                <span class="text-xl font-bold text-orange-400">{{
                  formatearTemperatura(store.estado.temperatures?.tool0?.actual)
                }}</span>
              </div>
              <div
                class="flex-1 flex flex-column align-items-center bg-white-alpha-10 p-3 border-round gap-1 justify-content-center">
                <span class="text-color-secondary uppercase text-xs font-semibold text-center">Cama Caliente</span>
                <span class="text-xl font-bold text-red-400">{{
                  formatearTemperatura(store.estado.temperatures?.bed?.actual)
                }}</span>
              </div>
            </div>

            <div class="flex flex-column gap-3 bg-white-alpha-10 p-3 border-round">
              <div class="flex justify-content-between align-items-center">
                <span class="text-color-secondary text-xs font-semibold uppercase">Progreso</span>
                <span class="font-bold text-primary">{{ Math.round(store.estado.progress?.completion || 0) }}%</span>
              </div>
              <ProgressBar :value="store.estado.progress?.completion || 0" :showValue="false"
                style="height: 8px; margin-top: -8px;" />

              <div class="flex justify-content-between border-top-1 surface-border pt-2">
                <div class="flex flex-column">
                  <span class="text-xs text-color-secondary">Transcurrido</span>
                  <span class="font-mono font-medium">{{ formatearTiempo(store.estado.job?.time_elapsed) }}</span>
                </div>
                <div class="flex flex-column text-right">
                  <span class="text-xs text-color-secondary">Restante</span>
                  <span class="font-mono font-medium">{{ formatearTiempo(store.estado.job?.time_remaining) }}</span>
                </div>
              </div>
            </div>

          </div>

        </div>
      </Panel>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { usePrinterStore } from '../stores/printer'
import { deteccionErrores } from '../services/inferenceService'
import { useToast } from 'primevue/usetoast'

const store = usePrinterStore()
const toast = useToast()

// Estado de los paneles colapsables
const configColapsado = ref(false)
const monitorColapsado = ref(true)

// Abrir el panel de monitorización automáticamente al empezar a imprimir
watch(() => store.estaImprimiendo, (imprimiendo) => {
  if (imprimiendo) {
    configColapsado.value = true
    monitorColapsado.value = false
  }
})

const direccionIp = ref('')
const archivoSeleccionado = ref('')

// Referencias al elemento de la cámara y al canvas de captura
const imagenCamara = ref(null)
const canvasCaptura = ref(null)
let intervaloInferencia = null
let procesando = false

onMounted(() => {
  direccionIp.value = store.backendUrl || localStorage.getItem('printer_monitor_backend_url') || ''

  // Cada 2s capturamos un frame de la cámara y lo pasamos al modelo para detectar errores
  intervaloInferencia = setInterval(async () => {
    if (!imagenCamara.value || !canvasCaptura.value || !store.urlStream || procesando) return
    if (!store.estaImprimiendo) return

    procesando = true
    try {
      const imagen = imagenCamara.value
      const canvas = canvasCaptura.value

      // Ajustamos el canvas al tamaño del frame y lo dibujamos
      canvas.width = imagen.naturalWidth || 640
      canvas.height = imagen.naturalHeight || 480
      if (canvas.width === 0 || canvas.height === 0) return

      // El contexto 2D es el "pincel" que nos permite dibujar sobre el canvas
      const ctx = canvas.getContext('2d')
      // Copiamos el frame actual de la cámara al canvas
      ctx.drawImage(imagen, 0, 0, canvas.width, canvas.height)

      // Convertimos el canvas a un string base64 para poder enviárselo al modelo de IA
      const capturaDataUrl = canvas.toDataURL('image/jpeg', 0.8)

      // Enviamos el frame al modelo de IA y obtenemos si ha detectado algún error
      const resultado = await deteccionErrores(capturaDataUrl)

      // Guardamos el resultado en el store para que la UI pueda reaccionar
      store.detecciones.has_errors = resultado.has_errors

      // Si la IA detecta un error, registrarlo y cancelar la impresión
      if (resultado.has_errors) {
        console.warn('[IA] Error detectado, cancelando impresión...')
        await store.registrarError()
        store.enviarComando('cancel')
        store.mensajeCancelacionAuto = 'Impresión cancelada automáticamente por detección de errores (Inferencia Local).'
      }
    } catch (err) {
      console.error('[IA] Error capturando frame:', err)
    } finally {
      procesando = false
    }
  }, 2000)
})

// Limpiar el intervalo de inferencia al desmontar el componente
onUnmounted(() => {
  if (intervaloInferencia) clearInterval(intervaloInferencia)
})

// Manejar error de carga de la imagen de la cámara
function alErrorImagen(e) {
  e.target.style.display = 'none'
  const contenedor = e.target.parentElement
  if (contenedor) {
    const fallback = contenedor.querySelector('.text-color-secondary')
    if (fallback) fallback.style.display = 'flex'
  }
}

// Sincronizar la IP del input con la del store
watch(() => store.backendUrl, (nuevaUrl) => {
  if (nuevaUrl) direccionIp.value = nuevaUrl
})

// Sincronizar el archivo seleccionado con el que tiene OctoPrint
watch(() => store.estado.job?.file, (archivo) => {
  if (archivo && archivo !== 'Sin archivo') {
    archivoSeleccionado.value = archivo
  }
}, { immediate: true })

// Mostrar un toast cuando se cancela automáticamente por error
watch(() => store.mensajeCancelacionAuto, (mensaje) => {
  if (mensaje) {
    toast.add({ severity: 'error', summary: 'Impresión cancelada', detail: mensaje, life: 5000 })
    store.limpiarMensajeCancelacion()
  }
})

// Actualizar la IP del backend y reconectar
async function actualizarIp() {
  let url = direccionIp.value.trim()
  if (!url) return
  url = url.replace(/^https?:\/\//, '')
  store.guardarConfiguracion(url)
  await store.conectar()
}

// Subir un archivo .gcode al servidor
function alSubirArchivo(event) {
  const archivo = event.files[0]
  if (archivo) store.subirGcode(archivo)
}

// Al cambiar el archivo seleccionado en el dropdown
function alCambiarArchivo(event) {
  if (event.value) store.seleccionarArchivo(event.value)
}

// Formatea una temperatura numérica a texto con unidades
function formatearTemperatura(temp) {
  if (temp === undefined || temp === null) return '-- °C'
  return `${Math.round(temp)} °C`
}

// Formatea segundos a un formato legible (ej: "2h 15m" o "05m")
function formatearTiempo(segundos) {
  if (!segundos || isNaN(segundos)) return '--:--'
  const h = Math.floor(segundos / 3600)
  const m = Math.floor((segundos % 3600) / 60)
  const pad = (n) => n.toString().padStart(2, '0')
  return h > 0 ? `${h}h ${pad(m)}m` : `${pad(m)}m`
}
</script>
