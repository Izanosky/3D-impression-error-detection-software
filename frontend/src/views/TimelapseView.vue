<template>
  <div class="timelapse-view">
    <main class="timelapse-main">
      <div class="page-header">
        <h1 class="page-title">
          <i class="pi pi-video"></i>
          Biblioteca de Timelapses
        </h1>
        <div class="header-actions">
          <button class="refresh-btn" @click="fetchTimelapses" :disabled="loading">
            <i class="pi pi-refresh" :class="{ 'spin': loading }"></i>
            Actualizar
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading && timelapses.length === 0" class="state-container">
        <i class="pi pi-spin pi-spinner state-icon"></i>
        <p class="state-text">Cargando timelapses...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="state-container state-error">
        <i class="pi pi-exclamation-triangle state-icon"></i>
        <p class="state-text">{{ error }}</p>
        <button class="retry-btn" @click="fetchTimelapses">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="timelapses.length === 0" class="state-container">
        <i class="pi pi-video state-icon"></i>
        <p class="state-text">No hay timelapses disponibles</p>
        <p class="state-subtext">Los timelapses de tus impresiones aparecerán aquí</p>
      </div>

      <!-- Timelapse Grid -->
      <div v-else class="timelapse-grid">
        <div v-for="tl in timelapses" :key="tl.name" class="timelapse-card">
          <!-- Thumbnail / Preview -->
          <div class="card-preview" @click="openPlayer(tl)">
            <i class="pi pi-play-circle play-overlay"></i>
            <div class="card-format">{{ getExtension(tl.name) }}</div>
          </div>

          <!-- Info -->
          <div class="card-body">
            <h3 class="card-title" :title="tl.name">{{ tl.name }}</h3>
            <div class="card-meta">
              <span v-if="tl.size" class="meta-item">
                <i class="pi pi-file"></i> {{ formatSize(tl.size) }}
              </span>
              <span v-if="tl.date" class="meta-item">
                <i class="pi pi-calendar"></i> {{ tl.date }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="card-actions">
            <button class="action-btn action-download" @click="downloadTimelapse(tl)" title="Descargar">
              <i class="pi pi-download"></i>
            </button>
            <button class="action-btn action-delete" @click="confirmDelete(tl)" title="Eliminar">
              <i class="pi pi-trash"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Video Player Modal -->
      <Transition name="fade">
        <div v-if="playerVisible" class="modal-overlay" @click.self="closePlayer">
          <div class="modal-content">
            <div class="modal-header">
              <h2 class="modal-title">{{ currentTimelapse?.name }}</h2>
              <button class="modal-close" @click="closePlayer">
                <i class="pi pi-times"></i>
              </button>
            </div>
            <div class="modal-body">
              <video
                ref="videoPlayer"
                :src="currentVideoUrl"
                controls
                autoplay
                class="video-player"
              ></video>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Delete Confirmation Modal -->
      <Transition name="fade">
        <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
          <div class="modal-content modal-sm">
            <div class="modal-header">
              <h2 class="modal-title">Confirmar eliminación</h2>
              <button class="modal-close" @click="deleteTarget = null">
                <i class="pi pi-times"></i>
              </button>
            </div>
            <div class="modal-body">
              <p class="confirm-text">
                ¿Estás seguro de que quieres eliminar <strong>{{ deleteTarget.name }}</strong>?
              </p>
              <div class="confirm-actions">
                <button class="btn-cancel" @click="deleteTarget = null">Cancelar</button>
                <button class="btn-delete" @click="doDelete">Eliminar</button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
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

const store = usePrinterStore()
const userStore = useUserStore()

const timelapses = ref([])
const loading = ref(false)
const error = ref(null)
const playerVisible = ref(false)
const currentTimelapse = ref(null)
const deleteTarget = ref(null)
const videoPlayer = ref(null)

const apiBase = computed(() => {
  if (!store.backendUrl) return null
  return `http://${store.backendUrl}`
})

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
      // Get download URL
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

function closePlayer() {
  playerVisible.value = false
  currentTimelapse.value = null
  if (videoPlayer.value) {
    videoPlayer.value.pause()
  }
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
  deleteTarget.value = tl
}

async function doDelete() {
  if (!deleteTarget.value) return

  try {
    // Delete from Firestore
    await deleteDoc(doc(db, 'videos', deleteTarget.value.id))
    // Delete from Storage
    await deleteObject(storageRef(storage, deleteTarget.value.storagePath))
    // Remove from local list
    timelapses.value = timelapses.value.filter(t => t.id !== deleteTarget.value.id)
  } catch (e) {
    console.error('Error deleting video:', e)
  } finally {
    deleteTarget.value = null
  }
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
.timelapse-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.import-btn {
  background: #4caf50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.import-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.25px;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.page-title .pi {
  font-size: 1.3rem;
  color: var(--primary-color, #6366f1);
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.refresh-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ── State containers ── */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: var(--surface-card, #0f1028);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 14px;
}

.state-icon {
  font-size: 3rem;
  color: rgba(255, 255, 255, 0.2);
  margin-bottom: 1rem;
}

.state-error .state-icon {
  color: #f59e0b;
}

.state-text {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.state-subtext {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.35);
  margin-top: 0.5rem;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  border: none;
  background: var(--primary-color, #6366f1);
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #4f46e5;
}

/* ── Grid ── */
.timelapse-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.timelapse-card {
  background: var(--surface-card, #0f1028);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: border-color 0.2s, transform 0.2s;
}

.timelapse-card:hover {
  border-color: rgba(99, 102, 241, 0.3);
  transform: translateY(-2px);
}

/* ── Card Preview ── */
.card-preview {
  position: relative;
  height: 160px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.08));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  transition: background 0.2s;
}

.card-preview:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
}

.play-overlay {
  font-size: 3rem;
  color: rgba(255, 255, 255, 0.4);
  transition: color 0.2s, transform 0.2s;
}

.card-preview:hover .play-overlay {
  color: rgba(255, 255, 255, 0.8);
  transform: scale(1.1);
}

.card-format {
  position: absolute;
  top: 0.6rem;
  right: 0.6rem;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.5);
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

/* ── Card Body ── */
.card-body {
  padding: 1rem 1.25rem;
  flex: 1;
}

.card-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
  margin: 0 0 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
}

.meta-item .pi {
  font-size: 0.7rem;
}

/* ── Card Actions ── */
.card-actions {
  display: flex;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.7rem;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.45);
  cursor: pointer;
  transition: color 0.2s, background 0.2s;
  font-size: 0.9rem;
}

.action-btn:first-child {
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}

.action-download:hover {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.08);
}

.action-delete:hover {
  color: #f87171;
  background: rgba(248, 113, 113, 0.08);
}

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.modal-content {
  background: #0f1028;
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 16px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-sm {
  max-width: 420px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.modal-title {
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 1rem;
  cursor: pointer;
  padding: 0.3rem;
  border-radius: 6px;
  transition: color 0.2s, background 0.2s;
}

.modal-close:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.modal-body {
  padding: 1.5rem;
}

.video-player {
  width: 100%;
  border-radius: 10px;
  outline: none;
  background: #000;
}

.confirm-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  margin: 0 0 1.5rem;
  line-height: 1.5;
}

.confirm-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-cancel {
  padding: 0.55rem 1.25rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}

.btn-delete {
  padding: 0.55rem 1.25rem;
  border-radius: 8px;
  border: none;
  background: #ef4444;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-delete:hover {
  background: #dc2626;
}

/* ── Transitions ── */
.fade-enter-active {
  transition: opacity 0.2s ease;
}
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .timelapse-view {
    padding: 1.25rem;
  }

  .timelapse-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 600px) {
  .timelapse-grid {
    grid-template-columns: 1fr;
  }

  .modal-overlay {
    padding: 1rem;
  }
}
</style>
