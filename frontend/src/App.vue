<template>
  <div class="app-container dark-mode">
    <AppHeader />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
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
}
</style>
