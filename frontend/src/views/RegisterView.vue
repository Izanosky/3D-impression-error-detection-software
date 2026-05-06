<!-- Lo mismo que el login pero utilizamos las funciones de registro de firebase -->
<template>
  <div class="flex align-items-center justify-content-center" style="min-height: calc(100vh - 84px);">
    <div class="w-full px-3" style="max-width: 480px;">
      <Card class="bg-black-alpha-20 border-1 surface-border shadow-4">
        <template #content>
          <div class="flex flex-column align-items-center gap-3 mb-5">
            <div class="flex align-items-center justify-content-center border-round-xl shadow-2"
              style="background: var(--p-green-400); width: 64px; height: 64px;">
              <i class="pi pi-print" style="font-size: 2rem; color: #000;"></i>
            </div>
            <h1 class="text-3xl font-bold m-0 text-white">Crear Cuenta</h1>
            <span class="text-color-secondary text-sm">Únete a la comunidad PrintErr</span>
          </div>

          <Form v-slot="$form" :initialValues="initialValues" :resolver="resolver" @submit="onFormSubmit"
            class="flex flex-column gap-4 w-full">

            <div class="flex flex-column gap-1">
              <FloatLabel variant="in">
                <IconField>
                  <InputIcon class="pi pi-user" />
                  <InputText name="name" type="text" class="w-full" />
                </IconField>
                <label>Nombre completo</label>
              </FloatLabel>
              <Message v-if="$form.name?.invalid" severity="error" size="small" variant="simple">
                {{ $form.name.error.message }}
              </Message>
            </div>

            <div class="flex flex-column gap-1">
              <FloatLabel variant="in">
                <IconField>
                  <InputIcon class="pi pi-envelope" />
                  <InputText name="email" type="email" class="w-full" />
                </IconField>
                <label>Correo Electrónico</label>
              </FloatLabel>
              <Message v-if="$form.email?.invalid" severity="error" size="small" variant="simple">
                {{ $form.email.error.message }}
              </Message>
            </div>

            <div class="flex flex-column gap-1">
              <FloatLabel variant="in">
                <IconField>
                  <InputIcon class="pi pi-lock" />
                  <Password name="password" toggleMask :feedback="true" class="w-full" inputClass="w-full pl-5" />
                </IconField>
                <label>Contraseña</label>
              </FloatLabel>
              <Message v-if="$form.password?.invalid" severity="error" size="small" variant="simple">
                {{ $form.password.error.message }}
              </Message>
            </div>

            <div class="flex flex-column gap-1">
              <FloatLabel variant="in">
                <IconField>
                  <InputIcon class="pi pi-lock-open" />
                  <Password name="confirmPassword" toggleMask :feedback="false" class="w-full"
                    inputClass="w-full pl-5" />
                </IconField>
                <label>Confirmar contraseña</label>
              </FloatLabel>
              <Message v-if="$form.confirmPassword?.invalid" severity="error" size="small" variant="simple">
                {{ $form.confirmPassword.error.message }}
              </Message>
            </div>

            <Message v-if="registerError" severity="error" size="small" variant="simple"
              class="w-full justify-content-center">
              {{ registerError }}
            </Message>

            <Button type="submit" label="Registrarse" icon="pi pi-check" iconPos="right" :loading="loading"
              class="w-full font-bold py-3 mt-2" />
          </Form>


          <div class="text-center mt-5">
            <span class="text-sm text-color-secondary">¿Ya tienes cuenta? </span>
            <Button label="Inicia sesión aquí" link @click="router.push('/login')"
              class="p-0 ml-1 font-semibold text-primary" />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { z } from 'zod'
import { Form } from '@primevue/forms'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { signUp } from '@/services/authService'

const router = useRouter()
const toast = useToast()

const loading = ref(false)

const registerError = ref('')

const initialValues = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const resolver = ref(
  zodResolver(
    z.object({
      name: z
        .string()
        .trim()
        .min(1, { message: 'El nombre es obligatorio' })
        .max(50, { message: 'El nombre no puede exceder 50 caracteres' }),
      email: z
        .string()
        .trim()
        .min(1, { message: 'El email es obligatorio' })
        .email({ message: 'El email no es válido' }),
      password: z
        .string()
        .min(6, { message: 'Mínimo 6 caracteres' })
        .max(100, { message: 'Máximo 100 caracteres' }),
      confirmPassword: z
        .string()
        .min(1, { message: 'Confirma tu contraseña' })
    })
      .refine((data) => data.password === data.confirmPassword, {
        message: 'Las contraseñas no coinciden',
        path: ['confirmPassword']
      })
  )
)

async function onFormSubmit({ valid, values }) {
  if (!valid) return

  loading.value = true
  registerError.value = ''
  try {
    await signUp(values.email, values.password, values.name)
    toast.add({ severity: 'success', summary: 'Cuenta creada', detail: `¡Bienvenido ${values.name}!`, life: 3000 })
    router.push('/monitor')
  }
  catch (err) {
    console.error('Error al registrarse', err)
    let msg = 'Error en el registro'
    if (err.code === 'auth/email-already-in-use') msg = 'El email ya está registrado'
    toast.add({ severity: 'error', summary: 'Error', detail: msg, life: 3000 })
    registerError.value = msg
  }
  finally {
    loading.value = false
  }
}


</script>
