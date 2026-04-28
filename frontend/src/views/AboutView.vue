<template>
  <div class="flex flex-column p-4 md:p-6 mx-auto w-full gap-5" style="max-width: 800px;">
    
    <section class="text-center py-4">
      <h1 class="text-4xl font-extrabold m-0 mb-3 text-primary">Acerca del Proyecto</h1>
      <p class="text-base text-color-secondary m-0">Trabajo de Fin de Grado — Detección de errores en impresión 3D</p>
    </section>

    <!-- Descripción -->
    <Card class="border-1 surface-border shadow-4">
      <template #content>
        <div class="flex align-items-center gap-3 mb-2">
          <Avatar icon="pi pi-book" class="border-round-lg shadow-2" style="width: 48px; height: 48px; background: var(--p-green-400); color: #000;" />
          <h2 class="text-xl font-bold text-white m-0">Descripción</h2>
        </div>
        <p class="text-sm text-color-secondary line-height-3 m-0">
          Sistema de monitorización en tiempo real para impresoras 3D capaz de detectar errores de impresión
          usando modelos de visión por computador e inteligencia artificial. Se conecta a OctoPrint a través
          de un backend proxy, analiza cada frame con un modelo entrenado, y puede alertar o detener la
          impresión automáticamente si detecta un problema.
        </p>
      </template>
    </Card>

    <!-- Stack Tecnológico -->
    <div class="flex flex-column gap-3">
      <h2 class="text-xl font-bold text-white m-0 text-center">Stack Tecnológico</h2>
      <div class="grid">
        <div class="col-6 md:col-4" v-for="tech in techStack" :key="tech.name">
          <Card class="border-1 surface-border shadow-4 text-center h-full">
            <template #content>
              <div class="flex flex-column align-items-center justify-content-center gap-2">
                <Avatar :icon="tech.icon" class="border-round-lg mb-2" style="width: 40px; height: 40px; background: var(--p-green-400); color: #000;" />
                <span class="text-sm font-semibold text-color">{{ tech.name }}</span>
              </div>
            </template>
          </Card>
        </div>
      </div>
    </div>

    <!-- Autor -->
    <Card class="border-1 surface-border shadow-4 text-center mt-3">
      <template #content>
        <div class="flex align-items-center justify-content-center gap-3">
          <i class="pi pi-user" style="font-size: 1.5rem; background: var(--p-green-400); color: #000; padding: 0.5rem; border-radius: 8px;"></i>
          <span class="text-sm text-color-secondary">Proyecto desarrollado como Trabajo de Fin de Grado (TFG).</span>
        </div>
      </template>
    </Card>

  </div>
</template>

<script setup>
const techStack = [
  { name: 'Vue.js 3', icon: 'pi pi-globe' },
  { name: 'FastAPI', icon: 'pi pi-bolt' },
  { name: 'ONNX Web', icon: 'pi pi-eye' },
  { name: 'OctoPrint', icon: 'pi pi-print' },
  { name: 'WebSocket', icon: 'pi pi-arrows-h' },
  { name: 'PrimeVue', icon: 'pi pi-palette' }
]
</script>
