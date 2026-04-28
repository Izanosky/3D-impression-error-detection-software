<template>
  <div class="flex flex-column p-4 md:p-6 mx-auto w-full gap-6" style="max-width: 960px;">

    <!-- Hero -->
    <section class="flex flex-column align-items-center text-center gap-4 py-6 w-full mx-auto" style="max-width: 600px;">
      <Avatar icon="pi pi-desktop" class="border-round-xl shadow-4 flex align-items-center justify-content-center" style="width: 80px; height: 80px; font-size: 2.5rem; background: var(--p-green-400); color: #000;" />

      <h1 class="text-4xl md:text-5xl font-extrabold line-height-2 m-0 text-white">
        Monitoriza tu impresora 3D <span class="text-primary">en tiempo real</span>
      </h1>
      
      <p class="text-lg text-color-secondary line-height-3 m-0">
        Detecta errores de impresión automáticamente con inteligencia artificial,
        protegiendo tus impresiones y tu impresora.
      </p>
      
      <div class="flex gap-3 mt-2">
        <Button label="Ir al Monitor" icon="pi pi-arrow-right" iconPos="right" @click="$router.push('/monitor')" />
        <Button label="Saber más" icon="pi pi-info-circle" severity="secondary" outlined @click="$router.push('/about')" />
      </div>
    </section>

    <!-- Características -->
    <section class="flex flex-column gap-4 w-full">
      <h2 class="text-2xl font-bold text-center text-white m-0">Características</h2>
      
      <div class="grid">
        <div class="col-12 md:col-6" v-for="feature in features" :key="feature.title">
          <Card class="h-full border-1 surface-border shadow-4">
            <template #content>
              <div class="flex align-items-start gap-4">
                <Avatar :icon="feature.icon" class="flex-shrink-0 border-round-lg shadow-2" style="width: 48px; height: 48px; background: var(--p-green-400); color: #000;" />
                <div class="flex flex-column gap-1">
                  <h3 class="text-lg font-semibold text-white m-0">{{ feature.title }}</h3>
                  <p class="text-sm text-color-secondary line-height-3 m-0">{{ feature.description }}</p>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
const features = [
  {
    icon: 'pi pi-camera',
    title: 'Monitorización Visual',
    description: 'Visualiza tu impresora en tiempo real a través de la cámara conectada.'
  },
  {
    icon: 'pi pi-exclamation-triangle',
    title: 'Detección de Errores con IA',
    description: 'Un modelo de IA analiza cada frame buscando errores como spaghetti y warping.'
  },
  {
    icon: 'pi pi-pause',
    title: 'Control Remoto',
    description: 'Pausa o reanuda la impresión directamente desde la interfaz web.'
  },
  {
    icon: 'pi pi-chart-bar',
    title: 'Estado en Tiempo Real',
    description: 'Monitoriza temperaturas, progreso y estado de la impresora.'
  }
]
</script>
