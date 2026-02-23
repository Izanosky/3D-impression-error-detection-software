<template>
  <Dialog 
    v-model:visible="visible" 
    :modal="true" 
    :closable="true"
    header="Configuración"
    :style="{ width: '400px' }"
  >
    <div class="settings-form">
      <!-- Nombre del usuario -->
      <div v-if="userStore.currentUser" class="field">
        <label for="display-name">Nombre de usuario</label>
        <InputText 
          id="display-name"
          v-model="displayName" 
          placeholder="Tu nombre"
          class="w-full"
        />
      </div>

      <!-- Mensaje de estado -->
      <Message v-if="message" :severity="messageSeverity" :closable="false">
        {{ message }}
      </Message>
    </div>

    <template #footer>
      <Button 
        label="Guardar" 
        icon="pi pi-check" 
        @click="saveSettings"
        :loading="saving"
        :disabled="!displayName.trim()"
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
import { useUserStore } from '../stores/user'
import { updateUser } from '../services/usersService'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'saved'])

const userStore = useUserStore()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const displayName = ref('')
const saving = ref(false)
const message = ref('')
const messageSeverity = ref('info')

async function saveSettings() {
  const newName = displayName.value.trim()
  if (!userStore.currentUser || !newName) return

  if (newName === userStore.userName) {
    visible.value = false
    return
  }

  saving.value = true
  message.value = ''

  try {
    await updateUser(userStore.currentUser.uid, { displayName: newName })
    userStore.userName = newName
    message.value = '✓ Nombre actualizado'
    messageSeverity.value = 'success'
    setTimeout(() => { visible.value = false }, 600)
  } catch (err) {
    console.error('Error updating name:', err)
    message.value = '✗ Error al actualizar el nombre'
    messageSeverity.value = 'error'
  } finally {
    saving.value = false
  }
}

// Cargar datos al abrir
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    displayName.value = userStore.userName || ''
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

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field label {
  font-weight: 500;
  color: var(--text-color);
}

.w-full {
  width: 100%;
}
</style>
