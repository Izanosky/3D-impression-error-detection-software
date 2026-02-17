<template>
  <div class="camera-wrapper">
    <div class="camera-container">
      <img v-if="snapshotUrl" :src="snapshotUrl" alt="Vista de impresora" class="camera-image"
        @error="handleImageError" />
      <div v-else class="camera-placeholder">
        <span class="placeholder-text">Imagen de la cámara</span>
      </div>
    </div>

    <!-- Detections overlay or status -->
    <div v-if="detections.has_errors" class="detections-overlay">
      <Tag value="Error detectado" severity="danger" />
    </div>
  </div>
</template>

<script setup>
import Tag from 'primevue/tag'

defineProps({
  snapshotUrl: {
    type: String,
    default: ''
  },
  detections: {
    type: Object,
    default: () => ({ has_errors: false, total_detections: 0, classes: {} })
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
