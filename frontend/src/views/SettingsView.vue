<template>
  <div class="flex flex-column flex-1 p-4 md:p-6 mx-auto w-full max-w-screen-md">
    <main class="flex flex-column w-full gap-4">
      <!-- Header Options -->
      <div class="flex align-items-center justify-content-between mb-4">
        <h1 class="text-3xl font-bold text-white tracking-tighter m-0 flex align-items-center gap-3">
          <i class="pi pi-user text-primary-400 text-3xl"></i>
          Configuración
        </h1>
        <Button label="Volver" icon="pi pi-arrow-left" text severity="secondary" @click="router.back()" />
      </div>

      <Card class="glass-panel" :pt="{ body: { class: 'p-4' } }">
        <template #title>
          <div class="text-xl font-semibold border-bottom-1 surface-border pb-3 mb-2">
            Perfil de Usuario
          </div>
        </template>
        <template #content>
          <div class="flex flex-column gap-5 pt-2">
            <!-- User Info Badge -->
            <div class="flex align-items-center gap-4 p-4 border-round-xl bg-white-alpha-10 border-1 surface-border">
              <Avatar :label="userInitials" size="xlarge" shape="circle"
                class="bg-green-500 text-white font-bold text-3xl shadow-3 flex-shrink-0"
                style="width: 5rem; height: 5rem;" />
              <div class="flex flex-column gap-1">
                <span class="text-2xl font-semibold text-white">{{ userStore.userName }}</span>
                <span class="text-base text-white-alpha-60">{{ userStore.currentUser?.email }}</span>
              </div>
            </div>

            <!-- Edit Fields -->
            <div class="flex flex-column gap-4 mt-2">
              <div class="flex flex-column gap-2">
                <FloatLabel variant="in">
                  <InputText id="display-name" v-model="displayName" class="w-full" size="large" />
                  <label for="display-name">Nombre de usuario</label>
                </FloatLabel>
                <small class="text-white-alpha-50 pl-2">Este nombre aparecerá en la interfaz principal.</small>
              </div>

              <div class="flex flex-column gap-2">
                <FloatLabel variant="in">
                  <InputText id="user-email" :value="userStore.currentUser?.email" disabled class="w-full opacity-70"
                    size="large" />
                  <label for="user-email">Correo electrónico</label>
                </FloatLabel>
                <small class="text-white-alpha-50 pl-2">No se puede cambiar el correo electrónico asociado a la cuenta
                  actual.</small>
              </div>
            </div>

            <!-- Mensaje de estado -->
            <Message v-if="message" :severity="messageSeverity" :closable="false" class="w-full mt-2 border-round-xl">
              {{ message }}
            </Message>

            <Divider class="my-2" />

            <!-- Actions -->
            <div class="flex justify-content-end gap-3">
              <Button label="Cancelar" text severity="secondary" icon="pi pi-times" @click="loadData"
                :disabled="!hasChanges || saving" />
              <Button label="Guardar cambios" icon="pi pi-check" @click="saveSettings" :loading="saving"
                :disabled="!hasChanges || !displayName.trim()" class="gradient-btn px-4" />
            </div>
          </div>
        </template>
      </Card>
      
      <!-- Placeholder future settings panel e.g. for Octoprint Config -->
      <Card class="glass-panel opacity-60" :pt="{ body: { class: 'p-4' } }">
        <template #title>
          <div class="text-xl font-semibold border-bottom-1 surface-border pb-3 mb-2 flex justify-content-between align-items-center">
            Próximamente
            <Badge value="En desarrollo" severity="info" />
          </div>
        </template>
        <template #content>
          <p class="text-white-alpha-60 line-height-3 m-0">Ajustes de conectividad con OctoPrint, calidad de timelapse, preferencias de notificaciones, y más estarán disponibles aquí pronto.</p>
        </template>
      </Card>

    </main>
    <Toast />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { updateUser } from '../services/usersService'

import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import FloatLabel from 'primevue/floatlabel'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Avatar from 'primevue/avatar'
import Divider from 'primevue/divider'
import Badge from 'primevue/badge'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const userStore = useUserStore()
const toast = useToast()

const displayName = ref('')
const saving = ref(false)
const message = ref('')
const messageSeverity = ref('info')

const userInitials = computed(() => {
  const name = userStore.userName || ''
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.substring(0, 2).toUpperCase()
})

const hasChanges = computed(() => {
  return displayName.value.trim() !== (userStore.userName || '')
})

function loadData() {
  displayName.value = userStore.userName || ''
  message.value = ''
}

onMounted(() => {
  if (!userStore.currentUser) {
    router.push('/login')
  } else {
    loadData()
  }
})

watch(() => userStore.userName, () => {
  if (!hasChanges.value) loadData()
})

async function saveSettings() {
  const newName = displayName.value.trim()
  if (!userStore.currentUser || !newName) return

  saving.value = true
  message.value = ''

  try {
    await updateUser(userStore.currentUser.uid, { displayName: newName })
    userStore.userName = newName
    
    toast.add({ severity: 'success', summary: 'Cambios guardados', detail: 'Tu perfil ha sido actualizado.', life: 3000 })
    message.value = '✓ Perfil actualizado correctamente'
    messageSeverity.value = 'success'
  } catch (err) {
    console.error('Error updating name:', err)
    
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el perfil.', life: 3000 })
    message.value = '✗ Error al actualizar el perfil'
    messageSeverity.value = 'error'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* All styling relies on global PrimeFlex and existing app styles */
:deep(.p-inputtext) {
  background: rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.1);
  color: white;
}

:deep(.p-inputtext:focus) {
  background: rgba(0, 0, 0, 0.3);
  border-color: #a855f7;
  box-shadow: 0 0 0 1px rgba(168, 85, 247, 0.5);
}

:deep(.p-floatlabel label) {
  color: rgba(255, 255, 255, 0.6);
}
</style>
