<template>
  <div class="flex align-items-center justify-content-center" style="min-height: calc(100vh - 84px);">
    <div class="w-full px-3" style="max-width: 440px;">
      <Card class="bg-black-alpha-20 border-1 surface-border shadow-4">
        <template #content>
          <!-- Encabezado del formulario -->
          <div class="flex flex-column align-items-center gap-3 mb-5">
            <div class="flex align-items-center justify-content-center border-round-xl shadow-2"
              style="background: var(--p-green-400); width: 64px; height: 64px;">
              <i class="pi pi-print" style="font-size: 2rem; color: #000;"></i>
            </div>
            <h1 class="text-3xl font-bold m-0 text-white">Iniciar Sesión</h1>
            <span class="text-color-secondary text-sm">Bienvenido de nuevo a PrintErr</span>
          </div>

          <!-- Formulario de inicio de sesion -->
          <Form v-slot="$form" :initialValues="initialValues" :resolver="resolver" @submit="onFormSubmit"
            class="flex flex-column gap-4 w-full">

            <div class="flex flex-column gap-1">
              <!-- Utiliazmos el floatlabel para que el texto se suba cuando hacemos focus -->
              <FloatLabel variant="in">
                <IconField>
                  <InputIcon class="pi pi-envelope" />
                  <InputText name="email" type="email" class="w-full" />
                </IconField>
                <label>Correo Electrónico</label>
              </FloatLabel>
              <!-- Mensaje de error que mostramos cuando los datos son incorrectos -->
              <Message v-if="$form.email?.invalid" severity="error" size="small" variant="simple">
                {{ $form.email.error.message }}
              </Message>
            </div>

            <div class="flex flex-column gap-1">
              <div class="flex justify-content-end mb-1">
                <Button label="¿Olvidaste tu contraseña?" link size="small" @click="restablecerEmail"
                  class="p-0 text-xs text-primary" />
              </div>
              <FloatLabel variant="in">
                <IconField>
                  <InputIcon class="pi pi-lock" />
                  <Password name="password" toggleMask :feedback="false" class="w-full" inputClass="w-full pl-5" />
                </IconField>
                <label>Contraseña</label>
              </FloatLabel>
              <Message v-if="$form.password?.invalid" severity="error" size="small" variant="simple">
                {{ $form.password.error.message }}
              </Message>
            </div>

            <!-- Mensaje de error que mostramos cuando hay problemas con el inicio de sesión, no con los datos como tal -->
            <Message v-if="loginError" severity="error" size="small" variant="simple"
              class="w-full justify-content-center">
              {{ loginError }}
            </Message>

            <Button type="submit" label="Acceder" icon="pi pi-arrow-right" iconPos="right" :loading="loading"
              class="w-full font-bold py-3" />
          </Form>


          <div class="text-center mt-5">
            <span class="text-sm text-color-secondary">¿Aún no tienes cuenta? </span>
            <Button label="Crear cuenta gratuitamente" link @click="router.push('/register')"
              class="p-0 ml-1 font-semibold text-primary" />
          </div>
        </template>
      </Card>
    </div>

    <!-- Dialogo para el restablecimiento de contraseña -->
    <ConfirmDialog group="headless">
      <template #container="{ message, acceptCallback, rejectCallback }">
        <Card class="bg-black-alpha-20 border-1 surface-border shadow-4" style="max-width: 400px; width: 90vw;">
          <template #content>
            <div class="text-xl font-bold mb-2 text-white">Recuperar contraseña</div>
            <p class="text-color-secondary mb-4 text-sm">{{ message.message }}</p>
            <div class="flex flex-column gap-3 mb-4">
              <FloatLabel variant="on">
                <IconField>
                  <InputIcon class="pi pi-envelope" />
                  <InputText v-model="newEmail" type="email" class="w-full" />
                </IconField>
                <label>Email asociado</label>
              </FloatLabel>
            </div>
            <div class="flex gap-2 justify-content-end">
              <Button label="Cancelar" severity="secondary" text @click="rejectCallback" />
              <Button label="Enviar instrucciones" @click="acceptCallback" :loading="resetLoading" severity="primary" />
            </div>
          </template>
        </Card>
      </template>
    </ConfirmDialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { z } from 'zod'
import { Form } from '@primevue/forms'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { signIn, signOut, resetPassword } from '@/services/authService'

const router = useRouter()
const toast = useToast()
const confirm = useConfirm()

// Variables auxiliares para estados de carga y otras funciones
const loading = ref(false)

const loginError = ref('')
const newEmail = ref('')
const resetLoading = ref(false)

const initialValues = ref({
  email: '',
  password: ''
})

// Resolver para la validación de los datos del formulario con zod
const resolver = ref(
  zodResolver(
    z.object({
      email: z.string().trim().email({ message: 'El email no es válido' }),
      password: z.string().min(1, { message: 'Introduce tu contraseña' })
    })
  )
)

// Función que se ejecuta al enviar el formulario
async function onFormSubmit({ valid, values }) {
  if (!valid) return // Si el formulario no es válido, simplemente volvemos

  loading.value = true
  loginError.value = ''

  try { // Intentamos iniciar sesión
    const userCredential = await signIn(values.email, values.password)

    // Comprobamos si el usuario ha verificado su correo electrónico
    if (!userCredential.user.emailVerified) {
      await signOut()
      loginError.value = 'Debes verificar tu correo electrónico antes de acceder'
      toast.add({
        severity: 'warn',
        summary: 'Email no verificado',
        detail: 'Revisa tu bandeja de entrada y haz clic en el enlace de verificación.',
        life: 6000
      })
      return
    }

    toast.add({ severity: 'success', summary: 'Bienvenido', detail: 'Sesión iniciada correctamente', life: 3000 })
    router.push('/monitor')
  }
  catch (err) { // Capturamos los posibles errores que nos puedan salir
    console.error('Error login', err)
    loginError.value = 'Credenciales incorrectas'
    toast.add({ severity: 'error', summary: 'Error de acceso', detail: 'Verifica tu email y contraseña', life: 3000 })
  }
  finally { // Pausamos el estado de carga
    loading.value = false
  }
}


// Dialogo para el restablecimiento de contraseña
function restablecerEmail() {
  newEmail.value = ''

  // Ponemos el headless para que inicialmente este oculto y nosotros configuramos su estilo
  confirm.require({
    message: 'Introduce tu email para enviarte las instrucciones.',
    group: 'headless',
    accept: async () => {

      // Comprobamos que el email sea válido
      if (!newEmail.value || !newEmail.value.includes('@')) {
        toast.add({ severity: 'warn', summary: 'Email inválido', detail: 'Introduce un correo válido', life: 3000 })
        return
      }

      // Para mostrar el estado de carga mientras mandamos el correo de reestablecimiento
      resetLoading.value = true

      try {
        await resetPassword(newEmail.value) // Utilizamos la función propia de Firebase
        toast.add({ severity: 'success', summary: 'Enviado', detail: 'Revisa tu bandeja de entrada', life: 5000 })
      }
      catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo enviar el correo', life: 3000 })
      }
      finally { // Independientemente del resultado, paramos el estado de carga
        resetLoading.value = false
      }
    }
  })
}
</script>