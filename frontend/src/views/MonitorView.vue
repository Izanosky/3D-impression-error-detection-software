<template>
  <div class="monitor-view">
    <!-- Modal de configuración -->
    <SettingsDialog 
      v-model="store.showSettings" 
      :isFirstTime="store.isFirstTime"
      @saved="store.onSettingsSaved"
    />

    <main class="monitor-main">
      <!-- Panel de cámara -->
      <CameraView :snapshot-url="store.snapshotUrl" :detections="store.detections" />

      <!-- Panel lateral -->
      <aside class="sidebar">
        <PrinterStatus :status="store.status" />
        <ControlPanel 
          :is-printing="store.isPrinting"
          :is-paused="store.isPaused"
          @pause="store.pausePrint"
          @resume="store.resumePrint"
        />
      </aside>
    </main>
  </div>
</template>

<script setup>
import CameraView from '../components/CameraView.vue'
import PrinterStatus from '../components/PrinterStatus.vue'
import ControlPanel from '../components/ControlPanel.vue'
import SettingsDialog from '../components/SettingsDialog.vue'
import { usePrinterStore } from '../stores/printer'

const store = usePrinterStore()
</script>

<style scoped>
.monitor-view {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.monitor-main {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 1.5rem;
  padding: 1.5rem 2rem;
  flex: 1;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

@media (max-width: 1024px) {
  .monitor-main {
    grid-template-columns: 1fr;
  }
}
</style>
