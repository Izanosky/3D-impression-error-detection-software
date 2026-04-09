<template>
  <div class="flex flex-column p-4 md:p-6 mx-auto w-full gap-4" style="max-width: 960px;">
    <main class="flex flex-column gap-4 w-full">
      <div class="flex align-items-center justify-content-between flex-wrap gap-3">
        <h1 class="text-3xl font-bold text-white m-0 flex align-items-center gap-3">
          <i class="pi pi-video text-primary-400 text-3xl"></i>
          Biblioteca de Timelapses
        </h1>
        <div class="flex gap-2">
          <Button label="Actualizar" icon="pi pi-refresh" severity="secondary" outlined :loading="loading" @click="fetchTimelapses" />
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading && timelapses.length === 0" class="flex flex-column align-items-center justify-content-center p-6 bg-black-alpha-20 border-round-xl border-1 surface-border">
        <i class="pi pi-spin pi-spinner text-primary text-5xl mb-3"></i>
        <p class="text-color-secondary m-0">Cargando timelapses...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex flex-column align-items-center justify-content-center p-6 bg-black-alpha-20 border-round-xl border-1 surface-border">
        <i class="pi pi-exclamation-triangle text-orange-400 text-5xl mb-3"></i>
        <p class="text-color-secondary m-0 mb-3">{{ error }}</p>
        <Button label="Reintentar" icon="pi pi-refresh" @click="fetchTimelapses" />
      </div>

      <!-- Empty State -->
      <div v-else-if="timelapses.length === 0" class="flex flex-column align-items-center justify-content-center p-6 bg-black-alpha-20 border-round-xl border-1 surface-border">
        <i class="pi pi-video text-color-secondary text-5xl mb-3 opacity-50"></i>
        <p class="text-color m-0 text-lg">No hay timelapses disponibles</p>
        <p class="text-color-secondary m-0 text-sm mt-1">Los timelapses de tus impresiones aparecerán aquí</p>
      </div>

      <!-- Timelapse Grid -->
      <div v-else class="grid">
        <div v-for="tl in timelapses" :key="tl.name" class="col-12 md:col-6 lg:col-4 xl:col-3">
          <Card class="bg-black-alpha-20 border-1 surface-border shadow-4 h-full flex flex-column hover:-translate-y-1 transition-transform transition-duration-200 cursor-pointer" @click="openPlayer(tl)" :pt="{ body: { class: 'p-0 flex-grow-1 flex flex-column' }, content: { class: 'p-0 flex-grow-1 flex flex-column' } }">
            <template #content>
              <!-- Thumbnail / Preview -->
              <div class="relative h-10rem bg-primary-reverse flex align-items-center justify-content-center border-round-top overflow-hidden bg-black-alpha-50 group">
                <i class="pi pi-play-circle text-5xl text-white-alpha-50 hover:text-white transition-colors"></i>
                <div class="absolute top-0 right-0 m-2">
                  <Tag :value="getExtension(tl.name)" severity="info" class="bg-black-alpha-50 font-bold" />
                </div>
              </div>

              <!-- Info -->
              <div class="p-3 flex flex-column gap-2 flex-grow-1">
                <span class="font-semibold text-overflow-ellipsis overflow-hidden white-space-nowrap" :title="tl.name">{{ tl.name }}</span>
                <div class="flex align-items-center gap-3 text-xs text-color-secondary">
                  <span v-if="tl.size" class="flex align-items-center gap-1"><i class="pi pi-file"></i> {{ formatSize(tl.size) }}</span>
                  <span v-if="tl.date" class="flex align-items-center gap-1"><i class="pi pi-calendar"></i> {{ tl.date }}</span>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex border-top-1 surface-border">
                <Button icon="pi pi-download" class="flex-1 border-radius-0 border-none p-3" severity="secondary" text @click.stop="downloadTimelapse(tl)" v-tooltip="'Descargar'" />
                <div class="border-left-1 surface-border"></div>
                <Button icon="pi pi-trash" class="flex-1 border-radius-0 border-none p-3 hover:text-red-400" severity="secondary" text @click.stop="confirmDelete(tl)" v-tooltip="'Eliminar'" />
              </div>
            </template>
          </Card>
        </div>
      </div>

      <!-- Video Player Dialog -->
      <Dialog v-model:visible="playerVisible" modal :header="currentTimelapse?.name" :style="{ width: '80vw', maxWidth: '900px' }" :breakpoints="{ '960px': '90vw' }" @hide="onPlayerHide">
        <video
          ref="videoPlayer"
          :src="currentVideoUrl"
          controls
          autoplay
          class="w-full border-round bg-black"
        ></video>
      </Dialog>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePrinterStore } from '../stores/printer'
import { useUserStore } from '../stores/user'
import { db, storage } from '../services/firebase'
import { collection, query, where, getDocs, deleteDoc, doc } from 'firebase/firestore'
import { ref as storageRef, getDownloadURL, deleteObject } from 'firebase/storage'
import { useConfirm } from 'primevue/useconfirm'

import Button from 'primevue/button'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'

const store = usePrinterStore()
const userStore = useUserStore()
const confirm = useConfirm()

const timelapses = ref([])
const loading = ref(false)
const error = ref(null)

const playerVisible = ref(false)
const currentTimelapse = ref(null)
const videoPlayer = ref(null)

const currentVideoUrl = computed(() => {
  if (!currentTimelapse.value || !currentTimelapse.value.storagePath) return ''
  return currentTimelapse.value.downloadUrl || ''
})

onMounted(() => {
  fetchTimelapses()
})

async function fetchTimelapses() {
  if (!userStore.currentUser) {
    error.value = 'Usuario no autenticado'
    return
  }

  loading.value = true
  error.value = null

  try {
    const q = query(
      collection(db, 'videos'),
      where('userId', '==', userStore.currentUser.uid)
    )
    const querySnapshot = await getDocs(q)
    const videos = []
    for (const docSnap of querySnapshot.docs) {
      const data = docSnap.data()
      const videoData = {
        id: docSnap.id,
        name: data.name,
        size: data.size,
        date: data.date,
        storagePath: data.storagePath,
        userId: data.userId
      }
      
      try {
        const url = await getDownloadURL(storageRef(storage, data.storagePath))
        videoData.downloadUrl = url
      } catch (e) {
        console.error('Error getting download URL:', e)
        videoData.downloadUrl = ''
      }
      videos.push(videoData)
    }
    timelapses.value = videos
  } catch (e) {
    error.value = 'Error al cargar los videos. Verifica tu conexión.'
    console.error('Error fetching videos:', e)
  } finally {
    loading.value = false
  }
}

function openPlayer(tl) {
  currentTimelapse.value = tl
  playerVisible.value = true
}

function onPlayerHide() {
  if (videoPlayer.value) {
    videoPlayer.value.pause()
  }
  currentTimelapse.value = null
}

async function downloadTimelapse(tl) {
  if (!tl.downloadUrl) return
  const a = document.createElement('a')
  a.href = tl.downloadUrl
  a.download = tl.name
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

function confirmDelete(tl) {
  confirm.require({
    message: `¿Estás seguro de que quieres eliminar ${tl.name}?`,
    header: 'Confirmar eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Eliminar',
    acceptClass: 'p-button-danger',
    rejectLabel: 'Cancelar',
    accept: async () => {
      try {
        await deleteDoc(doc(db, 'videos', tl.id))
        await deleteObject(storageRef(storage, tl.storagePath))
        timelapses.value = timelapses.value.filter(t => t.id !== tl.id)
      } catch (e) {
        console.error('Error deleting video:', e)
      }
    }
  })
}

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

function getExtension(name) {
  const parts = name.split('.')
  return parts.length > 1 ? parts.pop().toUpperCase() : 'VIDEO'
}
</script>

<style scoped>
/* Relying mostly on PrimeFlex classes incorporated above */
</style>
