<template>
  <div class="app-container">
    <Toast />
    <ConfirmDialog />

    <!-- Barra de navegación -->
    <Menubar :model="menuItems"
      class="border-none border-radius-0 border-bottom-1 surface-border sticky top-0 z-5 shadow-2">
      <template #start>
        <div class="flex align-items-center gap-2 mr-4 cursor-pointer" @click="router.push('/')">
          <i class="pi pi-print"
            style="font-size: 1.25rem; background: var(--p-green-400); color: #000; padding: 0.4rem; border-radius: 8px;"></i>
          <span class="text-xl font-bold text-primary">PrintErr</span>
        </div>
      </template>

      <template #item="{ item, props, hasSubmenu }">
        <router-link v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
          <a :href="href" v-bind="props.action" @click="navigate" class="flex align-items-center">
            <span :class="item.icon" />
            <span class="ml-2">{{ item.label }}</span>
          </a>
        </router-link>
        <a v-else :href="item.url" :target="item.target" v-bind="props.action" class="flex align-items-center">
          <span :class="item.icon" />
          <span class="ml-2">{{ item.label }}</span>
          <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down ml-2" />
        </a>
      </template>

      <template #end>
        <div class="flex align-items-center gap-3">
          <!-- Indicador de estado de la impresora -->
          <div v-if="userStore.currentUser"
            class="flex align-items-center gap-2 px-2 py-1 border-round bg-white-alpha-10 cursor-default"
            v-tooltip.bottom="store.estado.connected ? 'Impresora conectada' : 'Impresora desconectada'">
            <span class="status-dot" :class="store.estado.connected ? 'status-online' : 'status-offline'"></span>
            <span class="text-xs font-semibold hidden md:block"
              :class="store.estado.connected ? 'text-green-400' : 'text-red-400'">
              {{ store.estado.connected ? 'Conectada' : 'Desconectada' }}
            </span>
          </div>

          <template v-if="!userStore.currentUser">
            <Button label="Iniciar Sesión" icon="pi pi-sign-in" @click="router.push('/login')" class="p-button-sm" />
          </template>
          <template v-else>
            <div
              class="flex align-items-center cursor-pointer p-1 pr-3 border-round bg-transparent hover:bg-white-alpha-10 transition-colors transition-duration-150"
              @click="toggleUserMenu" aria-haspopup="true" aria-controls="user_menu">
              <Avatar icon="pi pi-user" shape="circle" class="bg-primary text-white font-bold mr-2" />
              <span class="font-medium text-sm hidden md:block text-color">{{ userStore.userName }}</span>
              <i class="pi pi-angle-down ml-2 text-sm text-color-secondary"></i>
            </div>
            <TieredMenu ref="userMenuRef" id="user_menu" :model="userMenuItems" popup />
          </template>
        </div>
      </template>
    </Menubar>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePrinterStore } from './stores/printer'
import { useUserStore } from './stores/user'
import { signOut } from './services/authService'

const router = useRouter()
const store = usePrinterStore()
const userStore = useUserStore()

const userMenuRef = ref(null)

const menuItems = ref([
  { label: 'Inicio', icon: 'pi pi-home', route: '/' },
  { label: 'Monitorización', icon: 'pi pi-desktop', route: '/monitor' },
  { label: 'Historial', icon: 'pi pi-history', route: '/history' }
])

const userMenuItems = ref([
  {
    label: 'Configuración',
    icon: 'pi pi-cog',
    command: () => router.push('/settings')
  },
  { separator: true },
  {
    label: 'Cerrar sesión',
    icon: 'pi pi-sign-out',
    command: async () => {
      await signOut()
      router.push('/login')
    }
  }
])

function toggleUserMenu(event) {
  userMenuRef.value.toggle(event)
}

onMounted(() => {
  store.inicializar()
})

onUnmounted(() => {
  store.desconectarWebSocket()
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

:deep(.p-menubar) {
  padding: 0.5rem 1.5rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.status-online {
  background-color: #4ade80;
  box-shadow: 0 0 6px rgba(74, 222, 128, 0.6);
  animation: pulse-green 2s ease-in-out infinite;
}

.status-offline {
  background-color: #f87171;
  box-shadow: 0 0 4px rgba(248, 113, 113, 0.4);
}

@keyframes pulse-green {
  0%, 100% { box-shadow: 0 0 4px rgba(74, 222, 128, 0.4); }
  50% { box-shadow: 0 0 10px rgba(74, 222, 128, 0.8); }
}
</style>
