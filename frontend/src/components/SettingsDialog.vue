<template>
  <Dialog 
    v-model:visible="visible" 
    :modal="true" 
    :closable="canClose"
    :header="isFirstTime ? 'Configuración Inicial' : 'Configuración'"
    :style="{ width: '450px' }"
  >
    <div class="settings-form">
      <p v-if="isFirstTime" class="intro-text">
        <i class="pi pi-info-circle"></i>
        Introduce la dirección IP del dispositivo donde se ejecuta el backend.
      </p>

      <!-- IP del Backend -->
      <div class="field">
        <label for="backend-url">Dirección del Backend</label>
        <InputText 
          id="backend-url"
          v-model="backendUrl" 
          placeholder="192.168.1.100:8000"
          class="w-full"
        />
        <small>IP y puerto del dispositivo con el backend (ej: 192.168.1.100:8000)</small>
      </div>

      <!-- Mensaje de estado -->
      <Message v-if="message" :severity="messageSeverity" :closable="false">
        {{ message }}
      </Message>
    </div>

    <template #footer>
      <Button 
        label="Probar conexión" 
        icon="pi pi-wifi" 
        severity="secondary"
        @click="testConnection"
        :loading="testing"
      />
      <Button 
        label="Guardar" 
        icon="pi pi-check" 
        @click="saveSettings"
        :disabled="!backendUrl"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Message from 'primevue/message'

const props = defineProps({
  modelValue: Boolean,
  isFirstTime: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const canClose = computed(() => !props.isFirstTime)

const backendUrl = ref('')
const testing = ref(false)
const message = ref('')
const messageSeverity = ref('info')

// Cargar URL guardada
const STORAGE_KEY = 'printer_monitor_backend_url'

function loadSavedUrl() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved) {
    backendUrl.value = saved
  }
}

function getFullUrl() {
  let url = backendUrl.value.trim()
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'http://' + url
  }
  return url
}

async function testConnection() {
  testing.value = true
  message.value = ''
  
  try {
    const response = await fetch(`${getFullUrl()}/api/status`, {
      method: 'GET',
      mode: 'cors'
    })
    
    if (response.ok) {
      message.value = '✓ Conexión exitosa con el backend'
      messageSeverity.value = 'success'
    } else {
      message.value = '✗ El backend respondió con error'
      messageSeverity.value = 'warn'
    }
  } catch (error) {
    message.value = '✗ No se pudo conectar. Verifica la dirección.'
    messageSeverity.value = 'error'
  } finally {
    testing.value = false
  }
}

function saveSettings() {
  const url = getFullUrl()
  localStorage.setItem(STORAGE_KEY, backendUrl.value.trim())
  emit('saved', url)
  visible.value = false
}

// Cargar al montar
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    loadSavedUrl()
    message.value = ''
  }
}, { immediate: true })
</script>

<style scoped>
.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.intro-text {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 8px;
  color: var(--text-color-secondary);
  margin: 0;
}

.intro-text i {
  color: var(--primary-color);
  margin-top: 2px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field label {
  font-weight: 500;
  color: var(--text-color);
}

.field small {
  color: var(--text-color-secondary);
  font-size: 0.75rem;
}

.w-full {
  width: 100%;
}
</style>
