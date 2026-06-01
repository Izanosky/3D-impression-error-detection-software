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
          <Button label="Actualizar" icon="pi pi-refresh" severity="secondary" outlined :loading="cargando"
            @click="cargarHistorial" />
        </div>
      </div>

      <!-- Estado: Cargando -->
      <div v-if="cargando && registros.length === 0"
        class="flex flex-column align-items-center justify-content-center p-6 bg-black-alpha-20 border-round-xl border-1 surface-border">
        <i class="pi pi-spin pi-spinner text-primary text-5xl mb-3"></i>
        <p class="text-color-secondary m-0">Cargando historial...</p>
      </div>

      <!-- Estado: Error -->
      <div v-else-if="mensajeError"
        class="flex flex-column align-items-center justify-content-center p-6 bg-black-alpha-20 border-round-xl border-1 surface-border">
        <i class="pi pi-exclamation-triangle text-orange-400 text-5xl mb-3"></i>
        <p class="text-color-secondary m-0 mb-3">{{ mensajeError }}</p>
        <Button label="Reintentar" icon="pi pi-refresh" @click="cargarHistorial" />
      </div>

      <!-- Estado: Sin registros -->
      <div v-else-if="registros.length === 0"
        class="flex flex-column align-items-center justify-content-center p-6 bg-black-alpha-20 border-round-xl border-1 surface-border">
        <i class="pi pi-history text-color-secondary text-5xl mb-3 opacity-50"></i>
        <p class="text-color m-0 text-lg">No hay impresiones registradas</p>
        <p class="text-color-secondary m-0 text-sm mt-1">El historial de tus impresiones aparecerá aquí</p>
      </div>

      <!-- Lista de registros -->
      <div v-else class="card bg-black-alpha-20 border-round-xl border-1 surface-border p-3">
        <DataTable :value="registros" paginator :rows="10" :rowsPerPageOptions="[5, 10, 25, 50]"
          responsiveLayout="stack" breakpoint="960px" stripedRows class="p-datatable-sm"
          emptyMessage="No se encontraron registros en el historial.">
          <!-- Columna Estado -->
          <Column field="estado" header="Estado" sortable style="width: 15%;">
            <template #body="{ data }">
              <Tag :value="etiquetaEstado(data.estado)" :severity="severidadEstado(data.estado)"
                :icon="iconoEstado(data.estado)" class="font-semibold" />
            </template>
          </Column>

          <!-- Columna Archivo -->
          <Column field="nombreArchivo" header="Archivo" sortable style="width: 40%; max-width: 0;">
            <template #body="{ data }">
              <div class="font-medium text-color text-overflow-ellipsis overflow-hidden white-space-nowrap"
                v-tooltip.bottom="data.nombreArchivo" style="cursor: help;">
                {{ data.nombreArchivo }}
              </div>
            </template>
          </Column>

          <!-- Columna Fecha -->
          <Column field="fechaFin" header="Fecha" sortable style="width: 20%;">
            <template #body="{ data }">
              <div class="flex align-items-center gap-2 text-color-secondary text-sm">
                <i class="pi pi-calendar text-xs"></i>
                <span>{{ formatearFecha(data.fechaFin) }}</span>
              </div>
            </template>
          </Column>

          <!-- Columna Gráficas -->
          <Column header="Gráficas" style="width: 15%; text-align: center;">
            <template #body="{ data }">
              <div class="flex align-items-center justify-content-center gap-1">
                <Button icon="pi pi-chart-line" severity="warning" text rounded size="small"
                  v-tooltip.left="'Ver temperaturas'" @click="abrirGraficaTemperatura(data)"
                  :disabled="!tieneProgresion(data)" />
                <Button icon="pi pi-percentage" severity="info" text rounded size="small"
                  v-tooltip.left="'Ver progreso'" @click="abrirGraficaProgreso(data)"
                  :disabled="!tieneProgresion(data)" />
              </div>
            </template>
          </Column>

          <!-- Columna Acciones -->
          <Column header="" style="width: 10%; text-align: center;">
            <template #body="{ data }">
              <Button icon="pi pi-trash" severity="danger" text rounded v-tooltip.left="'Eliminar registro'"
                @click="confirmarEliminacion(data)" />
            </template>
          </Column>
        </DataTable>
      </div>

    </main>

    <!-- ═══════════════════════════════════════════════════════════════ -->
    <!-- Modal: Gráfica de Temperatura                                  -->
    <!-- ═══════════════════════════════════════════════════════════════ -->
    <Dialog v-model:visible="modalTemperaturaVisible" modal dismissableMask
      :style="{ width: '90vw', maxWidth: '800px' }" :pt="{ content: { style: 'padding: 0' } }">
      <template #header>
        <div class="flex align-items-center gap-2">
          <i class="pi pi-chart-line text-orange-400 text-xl"></i>
          <span class="font-bold text-lg">Progresión de Temperatura</span>
        </div>
      </template>
      <div class="p-4">
        <div class="text-sm text-color-secondary mb-3 flex align-items-center gap-2">
          <i class="pi pi-file text-xs"></i>
          <span>{{ registroSeleccionado?.nombreArchivo }}</span>
        </div>
        <div style="position: relative; height: 380px;">
          <Line v-if="datosGraficaTemperatura" :data="datosGraficaTemperatura" :options="opcionesGraficaTemperatura" />
        </div>
        <div class="flex justify-content-center gap-4 mt-3">
          <div class="flex align-items-center gap-2">
            <span class="inline-block border-round" style="width: 12px; height: 12px; background: #fb923c;"></span>
            <span class="text-sm text-color-secondary">Extrusor</span>
          </div>
          <div class="flex align-items-center gap-2">
            <span class="inline-block border-round" style="width: 12px; height: 12px; background: #f87171;"></span>
            <span class="text-sm text-color-secondary">Cama Caliente</span>
          </div>
        </div>
      </div>
    </Dialog>

    <!-- ═══════════════════════════════════════════════════════════════ -->
    <!-- Modal: Gráfica de Progreso                                     -->
    <!-- ═══════════════════════════════════════════════════════════════ -->
    <Dialog v-model:visible="modalProgresoVisible" modal dismissableMask
      :style="{ width: '90vw', maxWidth: '800px' }" :pt="{ content: { style: 'padding: 0' } }">
      <template #header>
        <div class="flex align-items-center gap-2">
          <i class="pi pi-percentage text-blue-400 text-xl"></i>
          <span class="font-bold text-lg">Progresión de Porcentaje</span>
        </div>
      </template>
      <div class="p-4">
        <div class="text-sm text-color-secondary mb-3 flex align-items-center gap-2">
          <i class="pi pi-file text-xs"></i>
          <span>{{ registroSeleccionado?.nombreArchivo }}</span>
        </div>
        <div style="position: relative; height: 380px;">
          <Line v-if="datosGraficaProgreso" :data="datosGraficaProgreso" :options="opcionesGraficaProgreso" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { obtenerHistorial, eliminarRegistro } from '../services/historyService'
import { useConfirm } from 'primevue/useconfirm'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

// Registrar los componentes de Chart.js necesarios
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

// Accedemos al store del usuario para saber si hay alguien logueado
const userStore = useUserStore()
// confirm nos permite mostrar un diálogo de confirmación antes de borrar
const confirm = useConfirm()

// Lista de registros que se mostrará en la tabla
const registros = ref([])
// Indica si estamos esperando respuesta de Firebase (para mostrar el spinner)
const cargando = ref(false)
// Mensaje de error si algo falla al cargar
const mensajeError = ref(null)

// Estado de los modales de gráficas
const modalTemperaturaVisible = ref(false)
const modalProgresoVisible = ref(false)
const registroSeleccionado = ref(null)
const datosGraficaTemperatura = ref(null)
const datosGraficaProgreso = ref(null)

// En cuanto se carga la página, pedimos el historial a Firebase
onMounted(() => {
  cargarHistorial()
})

// Pide todos los registros del usuario actual a Firebase y los guarda en 'registros'
async function cargarHistorial() {
  // Si no hay usuario logueado, no podemos consultar Firebase
  if (!userStore.currentUser) {
    mensajeError.value = 'Usuario no autenticado'
    return
  }

  cargando.value = true // Ponemos esto en true para que nos muestre el icono de carga
  mensajeError.value = null

  try {
    registros.value = await obtenerHistorial() // Obtenemos el historial de Firebase
  } catch (e) {
    mensajeError.value = 'Error al cargar el historial. Verifica tu conexión.'
    console.error('[Historial] Error:', e)
  } finally {
    // Tanto si sale bien como si falla, quitamos el spinner
    cargando.value = false
  }
}

// Dialog para pedirle al usuario confirmación antes de borrar un registro
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
        // Borramos el documento de Firebase
        await eliminarRegistro(registro)
        // Lo quitamos también de la lista local para que desaparezca sin recargar la página
        registros.value = registros.value.filter(r => r.id !== registro.id)
      } catch (e) {
        console.error('[Historial] Error eliminando registro:', e)
      }
    }
  })
}

// ═══════════════════════════════════════════════════════════════
// Utilidades para la tabla
// ═══════════════════════════════════════════════════════════════

// Comprueba si un registro tiene datos de progresión
function tieneProgresion(registro) {
  return registro.progresion && registro.progresion.length > 0
}

// Con esta función ponemos el estado de cada impresión en formato texto para mostrarlo en la tabla
function etiquetaEstado(estado) {
  const etiquetas = {
    finalizada: 'Finalizada',
    cancelada: 'Cancelada',
    error: 'Error'
  }
  return etiquetas[estado] || estado
}

// Con esta función ponemos el color del badge según el resultado de la impresión
function severidadEstado(estado) {
  const severidades = {
    finalizada: 'success',
    cancelada: 'warn',
    error: 'danger'
  }
  return severidades[estado] || 'secondary'
}

// Con esta función ponemos el icono del badge según el resultado de la impresión
function iconoEstado(estado) {
  const iconos = {
    finalizada: 'pi pi-check-circle',
    cancelada: 'pi pi-ban',
    error: 'pi pi-exclamation-triangle'
  }
  return iconos[estado] || 'pi pi-info-circle'
}

// Convertimos el timestamp almacenado en Firebase al formato dd/mm/yyyy hh:mm
function formatearFecha(timestamp) {
  if (!timestamp) return 'Fecha desconocida'

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

// ═══════════════════════════════════════════════════════════════
// Gráficas
// ═══════════════════════════════════════════════════════════════

// Convierte los timestamps de los snapshots a etiquetas de tiempo relativo
function generarEtiquetasTiempo(progresion) {
  if (!progresion || progresion.length === 0) return []
  const inicio = progresion[0].t
  return progresion.map(s => {
    const segs = Math.round((s.t - inicio) / 1000)
    const mins = Math.floor(segs / 60)
    const secs = segs % 60
    if (mins >= 60) {
      const hrs = Math.floor(mins / 60)
      const m = mins % 60
      return `${hrs}h ${m.toString().padStart(2, '0')}m`
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`
  })
}

// Estilo base compartido para ambas gráficas
const estiloBaseGrafica = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: 'rgba(15, 15, 25, 0.95)',
      titleColor: '#e2e8f0',
      bodyColor: '#cbd5e1',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      borderWidth: 1,
      cornerRadius: 8,
      padding: 12,
      bodySpacing: 6,
      titleFont: { weight: 'bold', size: 13 },
      bodyFont: { size: 12 },
    },
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(255, 255, 255, 0.06)',
        drawBorder: false,
      },
      ticks: {
        color: '#94a3b8',
        font: { size: 11 },
        maxRotation: 45,
        maxTicksLimit: 15,
      },
    },
    y: {
      grid: {
        color: 'rgba(255, 255, 255, 0.06)',
        drawBorder: false,
      },
      ticks: {
        color: '#94a3b8',
        font: { size: 11 },
      },
    },
  },
}

// Opciones específicas de la gráfica de temperatura
const opcionesGraficaTemperatura = {
  ...estiloBaseGrafica,
  plugins: {
    ...estiloBaseGrafica.plugins,
    tooltip: {
      ...estiloBaseGrafica.plugins.tooltip,
      callbacks: {
        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y?.toFixed(1) ?? '--'} °C`,
      },
    },
  },
  scales: {
    ...estiloBaseGrafica.scales,
    y: {
      ...estiloBaseGrafica.scales.y,
      title: {
        display: true,
        text: 'Temperatura (°C)',
        color: '#94a3b8',
        font: { size: 12, weight: 'bold' },
      },
    },
    x: {
      ...estiloBaseGrafica.scales.x,
      title: {
        display: true,
        text: 'Tiempo transcurrido',
        color: '#94a3b8',
        font: { size: 12, weight: 'bold' },
      },
    },
  },
}

// Opciones específicas de la gráfica de progreso
const opcionesGraficaProgreso = {
  ...estiloBaseGrafica,
  plugins: {
    ...estiloBaseGrafica.plugins,
    tooltip: {
      ...estiloBaseGrafica.plugins.tooltip,
      callbacks: {
        label: (ctx) => `Progreso: ${ctx.parsed.y?.toFixed(1) ?? '--'}%`,
      },
    },
  },
  scales: {
    ...estiloBaseGrafica.scales,
    y: {
      ...estiloBaseGrafica.scales.y,
      min: 0,
      max: 100,
      title: {
        display: true,
        text: 'Progreso (%)',
        color: '#94a3b8',
        font: { size: 12, weight: 'bold' },
      },
    },
    x: {
      ...estiloBaseGrafica.scales.x,
      title: {
        display: true,
        text: 'Tiempo transcurrido',
        color: '#94a3b8',
        font: { size: 12, weight: 'bold' },
      },
    },
  },
}

// Abre el modal de la gráfica de temperatura y construye los datos
function abrirGraficaTemperatura(registro) {
  registroSeleccionado.value = registro
  const prog = registro.progresion || []
  const etiquetas = generarEtiquetasTiempo(prog)

  datosGraficaTemperatura.value = {
    labels: etiquetas,
    datasets: [
      {
        label: 'Extrusor',
        data: prog.map(s => s.tempExtrusor),
        borderColor: '#fb923c',
        backgroundColor: 'rgba(251, 146, 60, 0.1)',
        borderWidth: 2.5,
        pointRadius: prog.length > 50 ? 0 : 3,
        pointHoverRadius: 5,
        pointBackgroundColor: '#fb923c',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Cama Caliente',
        data: prog.map(s => s.tempCama),
        borderColor: '#f87171',
        backgroundColor: 'rgba(248, 113, 113, 0.08)',
        borderWidth: 2.5,
        pointRadius: prog.length > 50 ? 0 : 3,
        pointHoverRadius: 5,
        pointBackgroundColor: '#f87171',
        tension: 0.3,
        fill: true,
      },
    ],
  }
  modalTemperaturaVisible.value = true
}

// Abre el modal de la gráfica de progreso y construye los datos
function abrirGraficaProgreso(registro) {
  registroSeleccionado.value = registro
  const prog = registro.progresion || []
  const etiquetas = generarEtiquetasTiempo(prog)

  datosGraficaProgreso.value = {
    labels: etiquetas,
    datasets: [
      {
        label: 'Progreso',
        data: prog.map(s => s.porcentaje),
        borderColor: '#60a5fa',
        backgroundColor: (ctx) => {
          const chart = ctx.chart
          const { ctx: context, chartArea } = chart
          if (!chartArea) return 'rgba(96, 165, 250, 0.1)'
          const gradient = context.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
          gradient.addColorStop(0, 'rgba(96, 165, 250, 0.25)')
          gradient.addColorStop(1, 'rgba(96, 165, 250, 0.02)')
          return gradient
        },
        borderWidth: 2.5,
        pointRadius: prog.length > 50 ? 0 : 3,
        pointHoverRadius: 5,
        pointBackgroundColor: '#60a5fa',
        tension: 0.3,
        fill: true,
      },
    ],
  }
  modalProgresoVisible.value = true
}
</script>
