<template>
  <div class="control-panel">
    <div class="panel-header">
      <span>Propiedades</span>
    </div>

    <div class="panel-content">
      <!-- File Selector -->
      <div class="control-group">
        <label>Selector de archivos:</label>
        <div class="file-select-wrapper">
          <Select v-model="selectedFile" :options="files" optionLabel="name" optionValue="name"
            placeholder="Seleccionar archivo..." class="file-dropdown" :disabled="isPrinting || isPaused || uploading"
            @change="onFileChange" />
        </div>
      </div>

      <!-- Upload (Hidden or secondary? Screenshot doesn't explicitly show it, keeping it for functionality but maybe less prominent or as is) -->
      <!-- Keeping functionality but maybe minimal UI if not in screenshot? 
           The screenshot focuses on playback controls. I'll keep the logic but maybe simplify UI if needed.
           Actually I'll keep the upload button but maybe style it or hide it if not needed? 
           The screenshot doesn't show an "Upload" button nearby. 
           But I should probably leave it accessible. I'll keep it but maybe above or below. 
           Let's hide it for now if strict adherence to screenshot, or keep it if logically needed. 
           I'll keep it but visually compatible. -->

      <!-- Upload Button -->
      <div class="control-group">
        <label>Subir archivo:</label>
        <Button :label="uploading ? 'Subiendo...' : 'Subir archivo'"
          :icon="uploading ? 'pi pi-spin pi-spinner' : 'pi pi-upload'"
          class="action-btn upload-btn"
          :disabled="isPrinting || isPaused || uploading"
          @click="fileInput?.click()" />
      </div>

      <!-- Controls -->
      <div class="action-buttons">
        <Button v-if="!isPrinting && !isPaused" label="Iniciar Impresión"
          icon="pi pi-play" class="action-btn start-btn" :disabled="!hasFile || uploading" @click="$emit('start')" />

        <Button v-else-if="isPrinting && !isPaused" label="Pausar Impresión" icon="pi pi-pause"
          class="action-btn pause-btn" @click="$emit('pause')" />

        <Button v-else label="Reanudar Impresión" icon="pi pi-play" class="action-btn start-btn"
          @click="$emit('resume')" />

        <Button label="Cancelar Impresión" icon="pi pi-times" class="action-btn cancel-btn"
          :disabled="!isPrinting && !isPaused" @click="$emit('cancel')" />
      </div>

      <!-- Upload Input Hidden -->
      <input ref="fileInput" type="file" accept=".gcode,.gco,.g" style="display: none" @change="onFileSelected" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Button from 'primevue/button'
import Select from 'primevue/select'

const props = defineProps({
  isPrinting: Boolean,
  isPaused: Boolean,
  hasFile: Boolean,
  uploading: Boolean,
  files: { type: Array, default: () => [] },
  currentFile: { type: String, default: '' }
})

const emit = defineEmits(['pause', 'resume', 'cancel', 'start', 'upload', 'select-file', 'refresh-files'])

const selectedFile = ref('')
const fileInput = ref(null)

// Sync selected file with the current file from OctoPrint status
watch(() => props.currentFile, (val) => {
  if (val && val !== 'Sin archivo') {
    selectedFile.value = val
  }
}, { immediate: true })

function onFileSelected(event) {
  const file = event.target.files[0]
  if (file) {
    emit('upload', file)
    event.target.value = ''
  }
}

function onFileChange(event) {
  if (event.value) {
    emit('select-file', event.value)
  }
}
</script>

<style scoped>
.control-panel {
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
  gap: 1.25rem;
  padding: 1.25rem;
  flex: 1;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.control-group label {
  font-size: 0.8rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.file-dropdown {
  width: 100%;
}

:deep(.p-select) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  box-shadow: none;
  transition: border-color 0.2s;
}

:deep(.p-select:hover) {
  border-color: rgba(99, 102, 241, 0.3);
}

:deep(.p-select.p-focus) {
  border-color: var(--primary-color, #6366f1);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
}

:deep(.p-select-label) {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  font-size: 0.85rem;
  padding: 0.6rem 1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.p-select-dropdown) {
  color: rgba(255, 255, 255, 0.4);
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: auto;
}

.action-btn {
  width: 100%;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  font-size: 0.85rem;
  padding: 0.7rem;
  justify-content: center;
  transition: background 0.2s, transform 0.15s, opacity 0.2s;
}

.action-btn:active {
  transform: scale(0.98);
}

.start-btn,
.pause-btn {
  background: var(--primary-color, #6366f1);
  color: #fff;
}

.start-btn:hover,
.pause-btn:hover {
  background: #4f46e5;
  transform: none !important;
}

.cancel-btn {
  background: rgba(239, 68, 68, 0.12);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.cancel-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  transform: none !important;
}

.cancel-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.upload-btn {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.upload-btn:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.25);
  transform: none !important;
}

.upload-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
</style>
