<template>
    <div class="login-container">
        <Toast />
        <div class="background-pattern"></div>
        <Card class="auth-card">
            <template #title>
                <div class="card-header">
                    <div class="logo-circle mb-3">
                        <img :src="logo" alt="Logo" />
                    </div>
                    <h1 class="text-3xl font-bold m-0 text-white">Iniciar Sesión</h1>
                    <span class="text-gray-400 text-sm mt-2">Bienvenido de nuevo a PrintErr</span>
                </div>
            </template>
            <template #content>
                <Form v-slot="$form" :initialValues="initialValues" :resolver="resolver" @submit="onFormSubmit"
                    class="flex flex-column gap-4 w-full mt-2">

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
                        <div class="flex justify-content-end mb-1">
                            <Button label="¿Olvidaste tu contraseña?" link size="small" @click="openResetDialog"
                                class="p-0 text-xs text-primary-400 hover:text-primary-300 transition-colors" />
                        </div>
                        <FloatLabel variant="in">
                            <IconField>
                                <InputIcon class="pi pi-lock" />
                                <Password name="password" toggleMask :feedback="false" class="w-full"
                                    inputClass="w-full pl-5" />
                            </IconField>
                            <label>Contraseña</label>
                        </FloatLabel>
                        <Message v-if="$form.password?.invalid" severity="error" size="small" variant="simple">
                            {{ $form.password.error.message }}
                        </Message>
                    </div>

                    <Message v-if="loginError" severity="error" size="small" variant="simple"
                        class="w-full justify-content-center">
                        {{ loginError }}
                    </Message>

                    <Button type="submit" label="Acceder" icon="pi pi-arrow-right" iconPos="right" :loading="loading"
                        class="w-full gradient-btn font-bold py-3" />
                </Form>

                <div class="text-center mt-5 footer-text">
                    <span class="text-sm text-gray-400">¿Aún no tienes cuenta? </span>
                    <Button label="Crear cuenta gratuitamente" link @click="router.push('/register')"
                        class="p-0 ml-1 font-semibold text-primary-400" />
                </div>
            </template>
        </Card>

        <ConfirmDialog group="headless">
            <template #container="{ message, acceptCallback, rejectCallback }">
                <div class="auth-card p-4 border-round relative overflow-hidden" style="max-width: 400px; width: 90vw;">
                    <div class="background-pattern opacity-20"></div>
                    <div class="relative z-1">
                        <div class="text-xl font-bold mb-2 text-white">Recuperar contraseña</div>
                        <p class="text-gray-400 mb-4 text-sm">{{ message.message }}</p>
                        <div class="flex flex-column gap-3 mb-4">
                            <FloatLabel variant="on">
                                <IconField>
                                    <InputIcon class="pi pi-envelope" />
                                    <InputText v-model="resetEmail" type="email" class="w-full" />
                                </IconField>
                                <label>Email asociado</label>
                            </FloatLabel>
                        </div>
                        <div class="flex gap-2 justify-content-end">
                            <Button label="Cancelar" severity="secondary" text @click="rejectCallback" />
                            <Button label="Enviar instrucciones" @click="acceptCallback" :loading="resetLoading"
                                severity="primary" />
                        </div>
                    </div>
                </div>
            </template>
        </ConfirmDialog>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { z } from 'zod'
import { Form } from '@primevue/forms'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import { useRouter } from 'vue-router'
const router = useRouter()

import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Message from 'primevue/message'
import Button from 'primevue/button'
import Card from 'primevue/card'
import ConfirmDialog from 'primevue/confirmdialog'
import FloatLabel from 'primevue/floatlabel'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import logo from '../assets/logo.png'

import {
    signIn,
    subscribeToAuth,
    resetPassword
} from '@/services/authService'

const toast = useToast()
const confirm = useConfirm()
const user = ref(null)
const loading = ref(false)
const loginError = ref('')
const resetEmail = ref('')
const resetLoading = ref(false)
let unsubscribe = null

const initialValues = ref({
    email: '',
    password: ''
})

const resolver = ref(
    zodResolver(
        z.object({
            email: z.string().trim().email({ message: 'El email no es válido' }),
            password: z.string().min(1, { message: 'Introduce tu contraseña' })
        })
    )
)

const onFormSubmit = async ({ valid, values }) => {
    if (!valid) return
    loading.value = true
    loginError.value = ''
    try {
        await signIn(values.email, values.password)
        toast.add({ severity: 'success', summary: 'Bienvenido', detail: 'Sesión iniciada correctamente', life: 3000 })
        router.push('/monitor')
    } catch (err) {
        console.error('Error login', err)
        loginError.value = 'Credenciales incorrectas'
        toast.add({ severity: 'error', summary: 'Error de acceso', detail: 'Verifica tu email y contraseña', life: 3000 })
    } finally {
        loading.value = false
    }
}

const openResetDialog = () => {
    resetEmail.value = ''
    confirm.require({
        message: 'Introduce tu email para enviarte las instrucciones.',
        group: 'headless',
        accept: async () => {
            if (!resetEmail.value || !resetEmail.value.includes('@')) {
                toast.add({ severity: 'warn', summary: 'Email inválido', detail: 'Introduce un correo válido', life: 3000 })
                return
            }
            resetLoading.value = true
            try {
                await resetPassword(resetEmail.value)
                toast.add({ severity: 'success', summary: 'Enviado', detail: 'Revisa tu bandeja de entrada', life: 5000 })
            } catch (err) {
                toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo enviar el correo', life: 3000 })
            } finally {
                resetLoading.value = false
            }
        }
    })
}

onMounted(() => {
    unsubscribe = subscribeToAuth((currentUser) => {
        user.value = currentUser
        if (currentUser) router.push('/monitor')
    })
})

onUnmounted(() => {
    if (unsubscribe) unsubscribe()
})
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 84px);
    padding: 2rem;
    position: relative;
    overflow: hidden;
}

/* Tech Background Pattern */
.background-pattern {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image:
        linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 30px 30px;
    mask-image: radial-gradient(circle at center, black 40%, transparent 80%);
    z-index: 0;
}

.auth-card {
    width: 100%;
    max-width: 440px;
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);
    position: relative;
    z-index: 1;
    overflow: hidden;
}

.auth-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
}

.card-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 2rem;
    text-align: center;
}

.logo-circle {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2));
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.2);
}

.logo-circle img {
    width: 85%;
    height: 85%;
    object-fit: contain;
}

:deep(.p-card-content) {
    padding-top: 0;
}

:deep(.p-inputtext) {
    background: rgba(0, 0, 0, 0.2);
    border-color: rgba(255, 255, 255, 0.1);
    color: white;
    padding-left: 2.5rem;
    /* Space for icon */
}

:deep(.p-inputtext:focus) {
    background: rgba(0, 0, 0, 0.3);
    border-color: #a855f7;
    box-shadow: 0 0 0 1px rgba(168, 85, 247, 0.5);
}

:deep(.p-float-label label) {
    left: 2.5rem;
    /* Align label with text start */
    color: rgba(255, 255, 255, 0.6);
}

:deep(.p-iconfield .p-inputicon) {
    left: 0.75rem;
    color: rgba(255, 255, 255, 0.5);
}

.gradient-btn {
    background: linear-gradient(135deg, #6366f1, #a855f7) !important;
    border: none;
    transition: transform 0.2s, box-shadow 0.2s;
}

.gradient-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px -5px rgba(168, 85, 247, 0.4);
}

.text-primary-400 {
    color: #c084fc;
}
</style>