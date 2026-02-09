<template>
  <Card class="camera-card">
    <template #title>
      <div class="card-header">
        <i class="pi pi-camera"></i>
        <span>Vista de Cámara</span>
        <Tag v-if="detections.has_errors" 
             :value="`${detections.total_detections} error(es)`" 
             severity="danger" />
      </div>
    </template>
    <template #content>
      <div class="camera-container">
        <img v-if="snapshotUrl" 
             :src="snapshotUrl" 
             alt="Vista de impresora"
             class="camera-image"
             @error="handleImageError" />
        <div v-else class="camera-placeholder">
          <i class="pi pi-video"></i>
          <p>Conectando a la cámara...</p>
        </div>
      </div>
      
      <!-- Detecciones -->
      <div v-if="detections.has_errors" class="detections-info">
        <Tag v-for="(info, className) in detections.classes" 
             :key="className"
             :value="`${className}: ${info.count}`"
             severity="warning"
             class="detection-tag" />
      </div>
    </template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
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
}
</script>

<style scoped>
.camera-card {
  background: rgba(22, 33, 62, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-header i {
  color: var(--primary-color);
}

.camera-container {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  background: #0a0a0f;
  border-radius: 12px;
  overflow: hidden;
}

.camera-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.camera-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-color-secondary);
}

.camera-placeholder i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.detections-info {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.detection-tag {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
