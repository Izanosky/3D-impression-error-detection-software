<template>
  <div class="app-container">
    <Toast />
    <ConfirmDialog />
    <!-- Global Settings Dialog -->
    <SettingsDialog v-model="store.showSettings" :isFirstTime="store.isFirstTime" @saved="store.onSettingsSaved" />

    <AppHeader />

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import SettingsDialog from './components/SettingsDialog.vue'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { usePrinterStore } from './stores/printer'

const store = usePrinterStore()

onMounted(() => {
  store.init()
})

onUnmounted(() => {
  store.disconnectWebSocket()
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--surface-ground);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
