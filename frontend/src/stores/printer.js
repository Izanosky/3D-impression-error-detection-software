import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePrinterStore = defineStore('printer', () => {
    // ── State ──
    const STORAGE_KEY = 'printer_monitor_backend_url'

    const showSettings = ref(false)
    const isFirstTime = ref(false)
    const backendUrl = ref('')
    const wsConnected = ref(false)

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

    const snapshotUrl = ref('')

    // ── Getters ──
    const isPrinting = computed(() =>
        status.value.state?.toLowerCase().includes('print')
    )

    const isPaused = computed(() =>
        status.value.state?.toLowerCase().includes('paus')
    )

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

        websocket.onopen = () => {
            console.log('WebSocket conectado')
            wsConnected.value = true
        }

        websocket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data)

                if (message.type === 'update') {
                    if (message.data.status) {
                        status.value = message.data.status
                    }
                    if (message.data.detections) {
                        detections.value = message.data.detections
                    }
                    if (message.data.snapshot) {
                        snapshotUrl.value = message.data.snapshot
                    }
                } else if (message.type === 'command_result') {
                    console.log(`Comando ${message.action}: ${message.success ? 'OK' : 'Error'}`)
                }
            } catch (error) {
                console.error('Error procesando mensaje WebSocket:', error)
            }
        }

        websocket.onclose = () => {
            console.log('WebSocket desconectado, reconectando en 3s...')
            wsConnected.value = false
            status.value.connected = false

            setTimeout(() => {
                if (backendUrl.value) {
                    connectWebSocket()
                }
            }, 3000)
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

    function onSettingsSaved(url) {
        backendUrl.value = url.replace(/^https?:\/\//, '')
        isFirstTime.value = false
        localStorage.setItem(STORAGE_KEY, backendUrl.value)
        disconnectWebSocket()
        connectWebSocket()
    }

    function init() {
        const savedUrl = localStorage.getItem(STORAGE_KEY)
        if (savedUrl) {
            backendUrl.value = savedUrl
            connectWebSocket()
        } else {
            isFirstTime.value = true
            showSettings.value = true
        }
    }

    return {
        // State
        showSettings,
        isFirstTime,
        backendUrl,
        wsConnected,
        status,
        detections,
        snapshotUrl,
        // Getters
        isPrinting,
        isPaused,
        // Actions
        connectWebSocket,
        disconnectWebSocket,
        sendCommand,
        pausePrint,
        resumePrint,
        onSettingsSaved,
        init
    }
})
