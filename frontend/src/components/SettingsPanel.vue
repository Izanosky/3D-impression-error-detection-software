<template>
  <Card class="settings-card">
    <template #title>
      <div class="card-header">
        <i class="pi pi-cog"></i>
        <span>Configuración</span>
      </div>
    </template>
    <template #content>
      <div class="settings-form">
        <!-- URL de OctoPrint -->
        <div class="field">
          <label for="octoprint-url">URL de OctoPrint</label>
          <InputText 
            id="octoprint-url"
            v-model="settings.octoprint_url" 
            placeholder="http://192.168.1.100:5000"
            class="w-full"
          />
          <small>Ejemplo: http://192.168.1.100:5000 o http://octopi.local</small>
        </div>

        <!-- API Key de OctoPrint -->
        <div class="field">
          <label for="octoprint-key">API Key de OctoPrint</label>
          <Password 
            id="octoprint-key"
            v-model="settings.octoprint_api_key" 
            placeholder="Tu API Key"
            :feedback="false"
            toggleMask
            class="w-full"
          />
          <small>Se obtiene en OctoPrint → Settings → API</small>
        </div>

        <!-- Botones -->
        <div class="buttons">
          <Button 
            label="Guardar" 
            icon="pi pi-save" 
            @click="saveSettings"
            :loading="saving"
          />
          <Button 
            label="Probar conexión" 
            icon="pi pi-wifi" 
            severity="secondary"
            @click="testConnection"
            :loading="testing"
          />
        </div>

        <!-- Mensaje de estado -->
        <Message v-if="message" :severity="messageSeverity" :closable="false">
          {{ message }}
        </Message>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const emit = defineEmits(['saved'])

const settings = ref({
  octoprint_url: '',
  octoprint_api_key: ''
})

const saving = ref(false)
const testing = ref(false)
const message = ref('')
const messageSeverity = ref('info')

async function loadSettings() {
  try {
    const response = await fetch('/api/settings')
    if (response.ok) {
      const data = await response.json()
      settings.value.octoprint_url = data.octoprint_url || ''
      // No cargamos la API key directamente por seguridad
      settings.value.octoprint_api_key = data.octoprint_api_key || ''
    }
  } catch (error) {
    console.error('Error loading settings:', error)
  }
}

async function saveSettings() {
  saving.value = true
  message.value = ''
  
  try {
    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings.value)
    })
    
    const data = await response.json()
    
    if (data.success) {
      message.value = '✓ Configuración guardada correctamente'
      messageSeverity.value = 'success'
      emit('saved')
    } else {
      message.value = '✗ Error al guardar la configuración'
      messageSeverity.value = 'error'
    }
  } catch (error) {
    message.value = '✗ Error de conexión'
    messageSeverity.value = 'error'
  } finally {
    saving.value = false
  }
}

async function testConnection() {
  testing.value = true
  message.value = ''
  
  try {
    const response = await fetch('/api/status')
    const data = await response.json()
    
    if (data.connected) {
      message.value = '✓ Conexión exitosa con OctoPrint'
      messageSeverity.value = 'success'
    } else {
      message.value = `✗ No se pudo conectar: ${data.error || 'Verifica la URL y API Key'}`
      messageSeverity.value = 'warn'
    }
  } catch (error) {
    message.value = '✗ Error de conexión con el backend'
    messageSeverity.value = 'error'
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-card {
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

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
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

.buttons {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

:deep(.p-inputtext),
:deep(.p-password-input) {
  background: rgba(0, 0, 0, 0.3);
  border-color: var(--surface-border);
  color: var(--text-color);
}

:deep(.p-inputtext:focus),
:deep(.p-password-input:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}
</style>
