<template>
  <div class="flex flex-column p-4 md:p-6 mx-auto w-full gap-4" style="max-width: 960px;">
    <main class="flex flex-column gap-4 w-full">

      <!-- Cabecera -->
      <div class="flex align-items-center justify-content-between flex-wrap gap-3">
        <h1 class="text-3xl font-bold text-white m-0 flex align-items-center gap-3">
          <i class="pi pi-history text-primary-400 text-3xl"></i>
          Historial de Impresiones
        </h1>
        <div class="flex gap-2">
          <Button label="Actualizar" icon="pi pi-refresh" severity="secondary" outlined :loading="cargando" @click="cargarHistorial" />
        </div>
      </div>

      <!-- Estado: Cargando -->
      <div v-if="cargando && registros.length === 0" class="flex flex-column align-items-center justify-content-center p-6 bg-black-alpha-20 border-round-xl border-1 surface-border">
        <i class="pi pi-spin pi-spinner text-primary text-5xl mb-3"></i>
        <p class="text-color-secondary m-0">Cargando historial...</p>
      </div>

      <!-- Estado: Error -->
      <div v-else-if="mensajeError" class="flex flex-column align-items-center justify-content-center p-6 bg-black-alpha-20 border-round-xl border-1 surface-border">
        <i class="pi pi-exclamation-triangle text-orange-400 text-5xl mb-3"></i>
        <p class="text-color-secondary m-0 mb-3">{{ mensajeError }}</p>
        <Button label="Reintentar" icon="pi pi-refresh" @click="cargarHistorial" />
      </div>

      <!-- Estado: Sin registros -->
      <div v-else-if="registros.length === 0" class="flex flex-column align-items-center justify-content-center p-6 bg-black-alpha-20 border-round-xl border-1 surface-border">
        <i class="pi pi-history text-color-secondary text-5xl mb-3 opacity-50"></i>
        <p class="text-color m-0 text-lg">No hay impresiones registradas</p>
        <p class="text-color-secondary m-0 text-sm mt-1">El historial de tus impresiones aparecerá aquí</p>
      </div>

      <!-- Lista de registros -->
      <div v-else class="flex flex-column gap-3">
        <div
          v-for="registro in registros"
          :key="registro.id"
          class="flex align-items-center gap-4 p-3 bg-black-alpha-20 border-round-xl border-1 surface-border shadow-2 hover:shadow-4 transition-all transition-duration-200"
        >
          <!-- Información del registro -->
          <div class="flex flex-column gap-1 flex-grow-1 min-w-0">
            <!-- Etiqueta de estado -->
            <div class="flex align-items-center gap-2">
              <Tag
                :value="etiquetaEstado(registro.estado)"
                :severity="severidadEstado(registro.estado)"
                :icon="iconoEstado(registro.estado)"
                class="font-semibold"
              />
            </div>

            <!-- Nombre del archivo .gcode -->
            <span class="font-medium text-color text-overflow-ellipsis overflow-hidden white-space-nowrap" :title="registro.nombreArchivo">
              {{ registro.nombreArchivo }}
            </span>

            <!-- Fecha de finalización -->
            <div class="flex align-items-center gap-1 text-color-secondary text-sm">
              <i class="pi pi-calendar text-xs"></i>
              <span>{{ formatearFecha(registro.fechaFin) }}</span>
            </div>
          </div>

          <!-- Botón para eliminar el registro -->
          <Button
            icon="pi pi-trash"
            severity="danger"
            text
            rounded
            class="flex-shrink-0"
            v-tooltip="'Eliminar registro'"
            @click="confirmarEliminacion(registro)"
          />
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { obtenerHistorial, eliminarRegistro } from '../services/printHistoryService'
import { useConfirm } from 'primevue/useconfirm'

const userStore = useUserStore()
const confirm = useConfirm()

// Estado del componente
const registros = ref([])
const cargando = ref(false)
const mensajeError = ref(null)

// Al montar el componente, cargamos el historial
onMounted(() => {
  cargarHistorial()
})

// Carga todos los registros del historial desde Firebase
async function cargarHistorial() {
  if (!userStore.currentUser) {
    mensajeError.value = 'Usuario no autenticado'
    return
  }

  cargando.value = true
  mensajeError.value = null

  try {
    registros.value = await obtenerHistorial()
  } catch (e) {
    mensajeError.value = 'Error al cargar el historial. Verifica tu conexión.'
    console.error('[Historial] Error:', e)
  } finally {
    cargando.value = false
  }
}

// Muestra un diálogo de confirmación antes de eliminar un registro
function confirmarEliminacion(registro) {
  confirm.require({
    message: '¿Estás seguro de que quieres eliminar este registro del historial?',
    header: 'Confirmar eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Eliminar',
    acceptClass: 'p-button-danger',
    rejectLabel: 'Cancelar',
    accept: async () => {
      try {
        await eliminarRegistro(registro)
        // Quitar el registro de la lista local sin recargar todo
        registros.value = registros.value.filter(r => r.id !== registro.id)
      } catch (e) {
        console.error('[Historial] Error eliminando registro:', e)
      }
    }
  })
}

// ─── Helpers para mostrar el estado de cada registro ──────────────

// Devuelve el texto de la etiqueta según el estado
function etiquetaEstado(estado) {
  const etiquetas = {
    finalizada: 'Finalizada',
    cancelada: 'Cancelada',
    error: 'Error'
  }
  return etiquetas[estado] || estado
}

// Devuelve el color/severidad de PrimeVue según el estado
function severidadEstado(estado) {
  const severidades = {
    finalizada: 'success',
    cancelada: 'warn',
    error: 'danger'
  }
  return severidades[estado] || 'secondary'
}

// Devuelve el icono según el estado
function iconoEstado(estado) {
  const iconos = {
    finalizada: 'pi pi-check-circle',
    cancelada: 'pi pi-ban',
    error: 'pi pi-exclamation-triangle'
  }
  return iconos[estado] || 'pi pi-info-circle'
}

// Formatea un Timestamp de Firestore a una fecha legible en español
function formatearFecha(timestamp) {
  if (!timestamp) return 'Fecha desconocida'

  // Firestore Timestamp tiene .toDate(), pero también puede venir como objeto con seconds
  let fecha
  if (timestamp.toDate) {
    fecha = timestamp.toDate()
  } else if (timestamp.seconds) {
    fecha = new Date(timestamp.seconds * 1000)
  } else {
    fecha = new Date(timestamp)
  }

  return fecha.toLocaleString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
