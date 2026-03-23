<template>
  <MenuBar :model="items">
    <template #start>
      <span class="material-symbols-outlined"></span>
    </template>

    <template #end>
      <div class="flex align-items-center gap-2">
        <Button icon="pi pi-bars" class="p-button-text" @click="toggle" aria-haspopup="true"
          aria-controls="overlay_tmenu" />
        <TieredMenu ref="menuVisible" id="overlay_tmenu" :model="menu_opciones" popup />
      </div>
    </template>
  </MenuBar>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { usePrinterStore } from '../stores/printer'
import { signOut } from '../services/authService'

import MenuBar from 'primevue/menubar'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import TieredMenu from 'primevue/tieredmenu'

const router = useRouter()
const userStore = useUserStore()
const printerStore = usePrinterStore()

const items = ref([
  {
    label: 'Inicio',
    icon: 'pi pi-home',
    command: () => {
      router.push('/')
    }
  },
  {
    label: 'Sobre Nosotros',
    icon: 'pi pi-info-circle',
    command: () => {
      router.push('/about')
    }
  },
  {
    label: 'Monitorización',
    icon: 'pi pi-desktop',
    command: () => {
      router.push('/monitor')
    }
  },
  {
    label: 'Biblioteca',
    icon: 'pi pi-video',
    command: () => {
      router.push('/timelapse')
    }
  }
])

const menuVisible = ref();
const menu_opciones = ref([
  {
    label: 'Configuración',
    icon: 'pi pi-cog',
    command: () => {
      router.push('/settings')
    }
  },
  {
    label: 'Cerrar sesión',
    icon: 'pi pi-sign-out',
    command: () => {
      signOut()
      router.push('/login')
    }
  },

]);

const toggle = (event) => {
  menuVisible.value.toggle(event);
};

</script>

<style scoped></style>
