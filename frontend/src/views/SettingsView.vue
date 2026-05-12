<template>
  <div class="flex flex-column p-4 md:p-6 mx-auto w-full gap-4" style="max-width: 600px;">
    <div class="flex align-items-center justify-content-between mb-2">
      <h1 class="text-3xl font-bold text-white m-0">Configuración</h1>
    </div>

    <!-- Perfil de Usuario -->
    <Panel class="shadow-4 mb-4">
      <template #header>
        <div class="text-xl font-semibold flex align-items-center gap-2">
          <i class="pi pi-user text-primary"></i> Perfil de Usuario
        </div>
      </template>
      <Form v-slot="$form" :initialValues="profileInitialValues" :resolver="profileResolver" @submit="onProfileSubmit"
        class="flex flex-column gap-4 pt-3">
        <div class="flex flex-column gap-2">
          <label class="text-sm font-semibold text-color-secondary uppercase">Correo Electrónico</label>
          <InputGroup>
            <InputGroupAddon class="bg-white-alpha-10 border-none"><i class="pi pi-envelope text-white"></i>
            </InputGroupAddon>
            <InputText v-model="email" disabled class="bg-white-alpha-10 border-none" />
          </InputGroup>
        </div>

        <div class="flex flex-column gap-1">
          <label class="text-sm font-semibold text-color-secondary uppercase">Nombre para mostrar</label>
          <InputGroup>
            <InputGroupAddon class="bg-white-alpha-10 border-none"><i class="pi pi-id-card text-white"></i>
            </InputGroupAddon>
            <InputText name="displayName" class="bg-white-alpha-10 border-none" />
          </InputGroup>
          <Message v-if="$form.displayName?.invalid" severity="error" size="small" variant="simple">
            {{ $form.displayName.error.message }}
          </Message>
        </div>

        <Button type="submit" label="Guardar Perfil" icon="pi pi-save" :loading="loading"
          class="mt-2 w-full md:w-auto align-self-end w-full" />
      </Form>
    </Panel>

    <!-- Sistema Base -->
    <Panel class="shadow-4">
      <template #header>
        <div class="text-xl font-semibold flex align-items-center gap-2">
          <i class="pi pi-cog text-primary"></i> Sistema Base
        </div>
      </template>
      <div class="flex flex-column gap-4 pt-3">
        <div class="flex flex-column gap-2">
          <label class="text-sm font-semibold text-color-secondary uppercase">IP / Dominio del Backend (Defecto)</label>
          <small class="text-color-secondary mb-2">Dirección por defecto utilizada para conectarse al backend o a
            OctoPrint
            desde la vista del Monitor.</small>
          <InputGroup>
            <InputGroupAddon class="bg-white-alpha-10 border-none"><i class="pi pi-server text-white"></i>
            </InputGroupAddon>
            <InputText v-model="backendIP" placeholder="Ej: 192.168.1.100" class="bg-white-alpha-10 border-none" />
          </InputGroup>
        </div>

        <Button label="Actualizar Red" icon="pi pi-cloud-upload" severity="secondary" @click="saveSettings"
          class="mt-2 w-full md:w-auto align-self-end w-full" />
      </div>
    </Panel>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { z } from 'zod'
import { Form } from '@primevue/forms'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import { auth } from '../services/firebase'
import { updateProfile } from 'firebase/auth'
import { usePrinterStore } from '../stores/printer'
import { useUserStore } from '../stores/user'
import { updateUser } from '../services/usersService'
import { useToast } from 'primevue/usetoast'

const store = usePrinterStore()
const userStore = useUserStore()
const toast = useToast()

// Variables para almacenar los datos del usuario
const email = ref('')
const backendIP = ref('')
const loading = ref(false)

const profileInitialValues = ref({
  displayName: ''
})

// Definimos las restricciones del formulario mediante el Zod
const profileResolver = ref(
  zodResolver(
    z.object({
      displayName: z
        .string()
        .trim()
        .min(1, { message: 'El nombre es obligatorio' })
        .max(30, { message: 'El nombre no puede superar los 30 caracteres' })
    })
  )
)

// Cuando se carga la vista, cargamos los datos del usuario
onMounted(() => {
  const user = auth.currentUser
  if (user) {
    email.value = user.email || ''
    profileInitialValues.value.displayName = userStore.userName || user.displayName || ''
  }
  backendIP.value = store.backendUrl || localStorage.getItem('printer_monitor_backend_url') || ''
})

// Función para manejar el submit del formulario
async function onProfileSubmit({ valid, values }) {

  // Si el formulario no es válido, no hacemos nada
  if (!valid) return

  // Obtenemos el usuario actual
  const user = auth.currentUser
  if (!user) return

  // Actualizamos el perfil
  loading.value = true
  try {
    // Actualizamos el perfil
    await updateProfile(user, { displayName: values.displayName })
    // Actualizamos el usuario en la base de datos
    await updateUser(user.uid, { displayName: values.displayName })
    // Actualizamos el usuario en el store
    userStore.userName = values.displayName
    toast.add({ severity: 'success', summary: 'Perfil guardado', detail: 'Tu perfil se ha actualizado correctamente.', life: 3000 })
  }
  catch (error) {
    console.error('Error actualizando perfil:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el perfil.', life: 3000 })
  }
  finally {
    loading.value = false
  }
}

// Guardamos la configuración
function saveSettings() {
  let url = backendIP.value.trim()
  url = url.replace(/^https?:\/\//, '')
  store.guardarConfiguracion(url)
  toast.add({ severity: 'success', summary: 'Sistema Base guardado', detail: 'La ruta IP predeterminada ha sido actualizada.', life: 3000 })
}
</script>
