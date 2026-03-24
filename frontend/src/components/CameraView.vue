<template>
  <div class="camera-wrapper">
    <div class="camera-container">
      <img ref="cameraImg" v-if="streamUrl" :src="streamUrl" crossorigin="anonymous" alt="Vista de impresora" class="camera-image"
        @error="handleImageError" />
      <div v-else class="camera-placeholder">
        <span class="placeholder-text">Imagen de la cámara</span>
      </div>
      <canvas ref="captureCanvas" style="display: none;"></canvas>
    </div>

    <!-- Detections overlay or status -->
    <div v-if="detections.has_errors" class="detections-overlay">
      <Tag value="Error detectado" severity="danger" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Tag from 'primevue/tag'
import { detectErrorsYolov8 } from '../services/inferenceService'
import { usePrinterStore } from '../stores/printer'

const props = defineProps({
  streamUrl: {
    type: String,
    default: ''
  },
  detections: {
    type: Object,
    default: () => ({ has_errors: false, total_detections: 0, classes: {} })
  }
})

const store = usePrinterStore()
const cameraImg = ref(null)
const captureCanvas = ref(null)
let inferenceInterval = null
let isProcessing = false

onMounted(() => {
  // Configurar inferencia local cada 2 segundos
  inferenceInterval = setInterval(async () => {
    if (!cameraImg.value || !captureCanvas.value || !props.streamUrl || isProcessing) return;
    
    // Solo inferir si está imprimiendo
    if (!store.isPrinting) return;

    isProcessing = true;
    try {
      const videoEl = cameraImg.value;
      const canvasEl = captureCanvas.value;
      
      // Dibujar imagen actual en el canvas
      canvasEl.width = videoEl.naturalWidth || 640;
      canvasEl.height = videoEl.naturalHeight || 480;
      
      if (canvasEl.width === 0 || canvasEl.height === 0) return;

      const ctx = canvasEl.getContext('2d');
      ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
      
      const captureDataUrl = canvasEl.toDataURL('image/jpeg', 0.8);
      
      const result = await detectErrorsYolov8(captureDataUrl);
      store.detections.has_errors = result.has_errors;
      
      if (result.has_errors) {
        console.warn('[Frontend-AI] Error detectado desde stream local, auto-cancelando impresión...');
        store.cancelPrint();
        store.autoCancelledMessage = 'Impresión cancelada automáticamente por detección de errores (Inferencia Local).';
      }
    } catch (err) {
      console.error('[Frontend-AI] Error capturando frame de stream:', err);
    } finally {
      isProcessing = false;
    }
  }, 2000);
})

onUnmounted(() => {
  if (inferenceInterval) {
    clearInterval(inferenceInterval)
  }
})

function handleImageError(e) {
  e.target.style.display = 'none'
  // Optionally show placeholder
  const container = e.target.parentElement
  if (container) {
    const placeholder = container.querySelector('.camera-placeholder')
    if (placeholder) placeholder.style.display = 'flex'
  }
}
</script>

<style scoped>
.camera-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.camera-container {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  background: #000;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}

.camera-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.camera-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: #000;
}

.placeholder-text {
  color: #a1a1aa;
  font-size: 1.25rem;
  font-weight: 400;
}

.detections-overlay {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
}
</style>
