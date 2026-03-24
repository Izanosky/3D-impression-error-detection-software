import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useUserStore } from './user'
import { updateUser, getUserByUid } from '../services/usersService'
import { uploadTimelapseBlob } from '../services/timelapseService'
import { detectErrorsYolov8 } from '../services/inferenceService'

export const usePrinterStore = defineStore('printer', () => {
    // ── State ──
    const STORAGE_KEY = 'printer_monitor_backend_url'

    const showSettings = ref(false)
    const isFirstTime = ref(false)
    const backendUrl = ref('')
    const wsConnected = ref(false)
    const uploading = ref(false)
    const gcodeFiles = ref([])

    let websocket = null

    const status = ref({
        connected: false,
        state: 'Desconocido',
        temperatures: { bed: {}, tool0: {} },
        job: { file: '', progress: 0, time_elapsed: 0, time_remaining: 0 }
    })

    const detections = ref({
        has_errors: false,
        total_detections: 0,
        classes: {}
    })

    const streamUrl = ref('')

    const autoCancelledMessage = ref('')

    // ── Getters ──
    const isPrinting = computed(() =>
        status.value.state?.toLowerCase().includes('print')
    )

    const isPaused = computed(() =>
        status.value.state?.toLowerCase().includes('paus')
    )

    const hasFile = computed(() => {
        const file = status.value.job?.file
        return !!file && file !== 'Sin archivo' && file !== '' && file !== 'null' && file !== null
    })

    // Connection status: 'disconnected' | 'backend' | 'printer'
    const connectionStatus = computed(() => {
        if (!wsConnected.value) return 'disconnected'
        if (status.value.connected) return 'printer'
        return 'backend'
    })

    // ── Actions ──
    function getWsUrl() {
        let base = backendUrl.value
        if (!base) return null
        base = base.replace(/^https?:\/\//, '')
        return `ws://${base}/ws`
    }

    function connectWebSocket() {
        const wsUrl = getWsUrl()
        if (!wsUrl) return

        console.log('Conectando a WebSocket:', wsUrl)

        websocket = new WebSocket(wsUrl)

        websocket.onopen = async () => {
            console.log('WebSocket conectado')
            wsConnected.value = true
            
            // Obtener la IP base del backend (quitando el puerto ej: :8000)
            const baseIp = backendUrl.value.split(':')[0]
            
            // Construir la URL del stream en MJPEG directo de la cámara 
            // de OctoPrint asumiendo que está en el puerto :80 de esa misma IP.
            streamUrl.value = `http://${baseIp}/webcam/?action=stream`
        }
        
        websocket.onmessage = async (event) => {
            try {
                const message = JSON.parse(event.data)

                if (message.type === 'update') {
                    if (message.data.status) {
                        status.value = message.data.status
                    }
                } else if (message.type === 'timelapse_ready') {
                    console.log('[Timelapse] Nuevos timelapses disponibles:', message.files)
                    _autoUploadTimelapses(message.files)
                } else if (message.type === 'command_result') {
                    console.log(`Comando ${message.action}: ${message.success ? 'OK' : 'Error'}`)
                }
            } catch (error) {
                console.error('Error procesando mensaje WebSocket:', error)
            }
        }

        websocket.onclose = () => {
            console.log('WebSocket desconectado')
            wsConnected.value = false
            status.value.connected = false
            streamUrl.value = '' // Limpiar imagen congelada
        }

        websocket.onerror = (error) => {
            console.error('Error WebSocket:', error)
            wsConnected.value = false
        }
    }

    function disconnectWebSocket() {
        if (websocket) {
            websocket.close()
            websocket = null
        }
    }

    function sendCommand(action) {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify({ action }))
        }
    }

    function pausePrint() {
        sendCommand('pause')
    }

    function resumePrint() {
        sendCommand('resume')
    }

    function cancelPrint() {
        sendCommand('cancel')
    }

    function startPrint() {
        sendCommand('start')
    }

    async function uploadGcode(file) {
        if (!backendUrl.value) return { success: false, error: 'No backend URL' }

        uploading.value = true
        try {
            const formData = new FormData()
            formData.append('file', file)

            const response = await fetch(`http://${backendUrl.value}/api/upload`, {
                method: 'POST',
                body: formData
            })
            const result = await response.json()
            await fetchFiles()
            return result
        } catch (error) {
            return { success: false, error: error.message }
        } finally {
            uploading.value = false
        }
    }

    async function fetchFiles() {
        if (!backendUrl.value) return
        try {
            const response = await fetch(`http://${backendUrl.value}/api/files`)
            const data = await response.json()
            gcodeFiles.value = data.files || []
        } catch (error) {
            console.error('Error fetching files:', error)
            gcodeFiles.value = []
        }
    }

    async function selectFile(filename) {
        if (!backendUrl.value) return false
        try {
            const response = await fetch(`http://${backendUrl.value}/api/files/select/${filename}`, {
                method: 'POST'
            })
            const result = await response.json()
            return result.success
        } catch (error) {
            console.error('Error selecting file:', error)
            return false
        }
    }

    /**
     * Manual connect: establishes WebSocket + loads OctoPrint files.
     * Called explicitly from the UI "Conectar" button.
     */
    async function connect() {
        if (!backendUrl.value) return
        disconnectWebSocket()
        connectWebSocket()
        await fetchFiles()
    }

    function clearAutoCancelledMessage() {
        autoCancelledMessage.value = ''
    }

    async function _autoUploadTimelapses(files) {
        if (!backendUrl.value || !files || files.length === 0) return

        for (const f of files) {
            try {
                console.log(`[Timelapse] Descargando ${f.name}...`)
                const response = await fetch(
                    `http://${backendUrl.value}/api/timelapse/download/${encodeURIComponent(f.name)}`
                )
                if (!response.ok) {
                    console.error(`[Timelapse] Error descargando ${f.name}: HTTP ${response.status}`)
                    continue
                }
                const blob = await response.blob()
                console.log(`[Timelapse] Subiendo ${f.name} a Firebase...`)
                await uploadTimelapseBlob(blob, f.name)
                console.log(`[Timelapse] ${f.name} subido correctamente`)
            } catch (e) {
                console.error(`[Timelapse] Error procesando ${f.name}:`, e)
            }
        }
    }

    function onSettingsSaved(url) {
        backendUrl.value = url.replace(/^https?:\/\//, '')
        isFirstTime.value = false
        localStorage.setItem(STORAGE_KEY, backendUrl.value)

        // Save to user profile if logged in
        const userStore = useUserStore()
        if (userStore.currentUser) {
            updateUser(userStore.currentUser.uid, { printerIp: backendUrl.value })
                .catch(err => console.error('Error saving printer IP to profile:', err))
        }
    }

    function init() {
        const savedUrl = localStorage.getItem(STORAGE_KEY)
        if (savedUrl) {
            backendUrl.value = savedUrl
            connect() // Auto-conectar al refrescar o cargar la app inicial
        }
    }

    // Sync printer IP from user profile on login
    const userStore = useUserStore()
    watch(() => userStore.currentUser, async (user) => {
        if (user) {
            try {
                const userData = await getUserByUid(user.uid)
                if (userData && userData.printerIp) {
                    console.log('Syncing printer IP from profile:', userData.printerIp)
                    backendUrl.value = userData.printerIp
                    localStorage.setItem(STORAGE_KEY, backendUrl.value)
                    
                    if (!wsConnected.value) {
                        connect() // Reconectar al iniciar sesión si había IP vinculada
                    }
                }
            } catch (err) {
                console.error('Error fetching user printer IP:', err)
            }
        }
    }, { immediate: true })

    return {
        // State
        showSettings,
        isFirstTime,
        backendUrl,
        wsConnected,
        uploading,
        gcodeFiles,
        status,
        detections,
        streamUrl,
        autoCancelledMessage,
        // Getters
        isPrinting,
        isPaused,
        hasFile,
        connectionStatus,
        // Actions
        connect,
        connectWebSocket,
        disconnectWebSocket,
        sendCommand,
        pausePrint,
        resumePrint,
        cancelPrint,
        startPrint,
        uploadGcode,
        fetchFiles,
        selectFile,
        onSettingsSaved,
        init,
        clearAutoCancelledMessage
    }
})
