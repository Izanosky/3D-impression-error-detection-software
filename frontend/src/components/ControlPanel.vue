<template>
  <Card class="control-card">
    <template #title>
      <div class="card-header">
        <i class="pi pi-sliders-h"></i>
        <span>Controles</span>
      </div>
    </template>
    <template #content>
      <div class="controls">
        <Button 
          v-if="!isPaused"
          label="Pausar Impresión" 
          icon="pi pi-pause" 
          severity="warning"
          :disabled="!isPrinting"
          @click="$emit('pause')"
          class="control-btn"
        />
        <Button 
          v-else
          label="Reanudar Impresión" 
          icon="pi pi-play" 
          severity="success"
          @click="$emit('resume')"
          class="control-btn"
        />
      </div>

      <div class="status-indicator">
        <div class="indicator" :class="{ active: isPrinting && !isPaused }"></div>
        <span>{{ statusText }}</span>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { computed } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'

const props = defineProps({
  isPrinting: Boolean,
  isPaused: Boolean
})

defineEmits(['pause', 'resume'])

const statusText = computed(() => {
  if (props.isPaused) return 'Impresión pausada'
  if (props.isPrinting) return 'Imprimiendo...'
  return 'En espera'
})
</script>

<style scoped>
.control-card {
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

.controls {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.control-btn {
  width: 100%;
  justify-content: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #71717a;
}

.indicator.active {
  background: #22c55e;
  box-shadow: 0 0 10px #22c55e;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
