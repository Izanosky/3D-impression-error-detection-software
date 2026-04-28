import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useUserStore } from './user'
import { updateUser, getUserByUid } from '../services/usersService'
import { guardarRegistro } from '../services/printHistoryService'

export const usePrinterStore = defineStore('printer', () => {
    const STORAGE_KEY = 'printer_monitor_backend_url'

    // ─── Estado reactivo ──────────────────────────────────────────────
    const backendUrl = ref('')
    const wsConectado = ref(false)
    const subiendo = ref(false)
    const archivosGcode = ref([])
    const urlStream = ref('')
    const mensajeCancelacionAuto = ref('')
    const ultimoFrame = ref('')  // Último frame capturado de la cámara (data URL)

    let websocket = null

    const estado = ref({
        connected: false,
        state: 'Desconocido',
        temperatures: { bed: {}, tool0: {} },
        job: { file: '', progress: 0, time_elapsed: 0, time_remaining: 0 }
    })

    const detecciones = ref({
        has_errors: false,
        total_detections: 0,
        classes: {}
    })

    // ─── Getters (propiedades computadas) ─────────────────────────────
    const estaImprimiendo = computed(() =>
        estado.value.state?.toLowerCase().includes('print')
    )

    const estaPausada = computed(() =>
        estado.value.state?.toLowerCase().includes('paus')
    )

    const tieneArchivo = computed(() => {
        const archivo = estado.value.job?.file
        return !!archivo && archivo !== 'Sin archivo' && archivo !== '' && archivo !== 'null' && archivo !== null
    })

    // ─── WebSocket ────────────────────────────────────────────────────

    // Construye la URL del WebSocket a partir de la IP del backend
    function obtenerUrlWs() {
        let base = backendUrl.value
        if (!base) return null
        base = base.replace(/^https?:\/\//, '')
        return `ws://${base}/ws`
    }

    // Establece la conexión WebSocket con el backend
    function conectarWebSocket() {
        const urlWs = obtenerUrlWs()
        if (!urlWs) return

        console.log('Conectando a WebSocket:', urlWs)
        websocket = new WebSocket(urlWs)

        websocket.onopen = () => {
            console.log('WebSocket conectado')
            wsConectado.value = true
            // Construir la URL del stream de la cámara usando la IP base
            const baseIp = backendUrl.value.split(':')[0]
            urlStream.value = `http://${baseIp}/webcam/?action=stream`
        }

        websocket.onmessage = (event) => {
            try {
                const mensaje = JSON.parse(event.data)

                if (mensaje.type === 'update') {
                    // Actualizar el estado de la impresora
                    if (mensaje.data.status) {
                        estado.value = mensaje.data.status
                    }
                } else if (mensaje.type === 'command_result') {
                    // Resultado de un comando enviado (pausar, cancelar, etc.)
                    console.log(`Comando ${mensaje.action}: ${mensaje.success ? 'OK' : 'Error'}`)
                }
            } catch (error) {
                console.error('Error procesando mensaje WebSocket:', error)
            }
        }

        websocket.onclose = () => {
            console.log('WebSocket desconectado')
            wsConectado.value = false
            estado.value.connected = false
            urlStream.value = ''
        }

        websocket.onerror = (error) => {
            console.error('Error WebSocket:', error)
            wsConectado.value = false
        }
    }

    // Cierra la conexión WebSocket
    function desconectarWebSocket() {
        if (websocket) {
            websocket.close()
            websocket = null
        }
    }

    // Envía un comando a OctoPrint a través del WebSocket
    function enviarComando(accion) {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify({ action: accion }))
        }
    }

    // ─── Acciones de impresión ────────────────────────────────────────

    function pausarImpresion() { enviarComando('pause') }
    function reanudarImpresion() { enviarComando('resume') }
    function iniciarImpresion() { enviarComando('start') }

    // Cancela la impresión manualmente y registra la cancelación en el historial
    async function cancelarImpresion() {
        // Guardamos el frame y nombre del archivo ANTES de cancelar
        const frame = ultimoFrame.value
        const nombreArchivo = estado.value.job?.file || 'Desconocido'

        // Enviamos el comando de cancelar a OctoPrint
        enviarComando('cancel')

        // Registramos la cancelación en el historial, aunque no haya frame
        try {
            await guardarRegistro('cancelada', frame, nombreArchivo)
            console.log('[Historial] Impresión cancelada registrada')
        } catch (e) {
            console.error('[Historial] Error registrando cancelación:', e)
        }
    }

    // Registra en el historial que la impresión se detuvo por un error de la IA
    async function registrarError() {
        const frame = ultimoFrame.value
        const nombreArchivo = estado.value.job?.file || 'Desconocido'

        try {
            await guardarRegistro('error', frame, nombreArchivo)
            console.log('[Historial] Impresión con error registrada')
        } catch (e) {
            console.error('[Historial] Error registrando fallo:', e)
        }
    }

    // ─── Gestión de archivos ──────────────────────────────────────────

    // Sube un archivo .gcode al servidor de OctoPrint
    async function subirGcode(archivo) {
        if (!backendUrl.value) return { success: false, error: 'No hay URL del backend' }

        subiendo.value = true
        try {
            const formData = new FormData()
            formData.append('file', archivo)

            const respuesta = await fetch(`http://${backendUrl.value}/api/upload`, {
                method: 'POST',
                body: formData
            })
            const resultado = await respuesta.json()
            await obtenerArchivos()
            return resultado
        } catch (error) {
            return { success: false, error: error.message }
        } finally {
            subiendo.value = false
        }
    }

    // Obtiene la lista de archivos .gcode disponibles en OctoPrint
    async function obtenerArchivos() {
        if (!backendUrl.value) return
        try {
            const respuesta = await fetch(`http://${backendUrl.value}/api/files`)
            const datos = await respuesta.json()
            archivosGcode.value = datos.files || []
        } catch (error) {
            console.error('Error obteniendo archivos:', error)
            archivosGcode.value = []
        }
    }

    // Selecciona un archivo .gcode en OctoPrint para imprimir
    async function seleccionarArchivo(nombre) {
        if (!backendUrl.value) return false
        try {
            const respuesta = await fetch(`http://${backendUrl.value}/api/files/select/${nombre}`, {
                method: 'POST'
            })
            const resultado = await respuesta.json()
            return resultado.success
        } catch (error) {
            console.error('Error seleccionando archivo:', error)
            return false
        }
    }

    // ─── Conexión y configuración ─────────────────────────────────────

    // Conecta al backend: establece WebSocket y carga los archivos
    async function conectar() {
        if (!backendUrl.value) return
        desconectarWebSocket()
        conectarWebSocket()
        await obtenerArchivos()
    }

    // Limpia el mensaje de cancelación automática
    function limpiarMensajeCancelacion() {
        mensajeCancelacionAuto.value = ''
    }

    // Guarda la nueva IP del backend en localStorage y en el perfil del usuario
    function guardarConfiguracion(url) {
        backendUrl.value = url.replace(/^https?:\/\//, '')
        localStorage.setItem(STORAGE_KEY, backendUrl.value)

        // Si el usuario está logueado, guardar la IP en su perfil de Firestore
        const userStore = useUserStore()
        if (userStore.currentUser) {
            updateUser(userStore.currentUser.uid, { printerIp: backendUrl.value })
                .catch(err => console.error('Error guardando IP en el perfil:', err))
        }
    }

    // Inicializa el store: carga la URL guardada y conecta automáticamente
    function inicializar() {
        const urlGuardada = localStorage.getItem(STORAGE_KEY)
        if (urlGuardada) {
            backendUrl.value = urlGuardada
            conectar()
        }
    }

    // ─── Detección automática de fin de impresión exitosa ─────────────
    // Cuando la impresora pasa de "imprimiendo" a "no imprimiendo" y el progreso
    // era mayor o igual al 99%, registramos que la impresión terminó bien.
    let _estabImprimiendo = false
    watch(estaImprimiendo, async (imprimiendoAhora) => {
        if (_estabImprimiendo && !imprimiendoAhora) {
            const progreso = estado.value.job?.progress || 0
            if (progreso >= 99) {
                const frame = ultimoFrame.value
                const nombreArchivo = estado.value.job?.file || 'Desconocido'
                try {
                    await guardarRegistro('finalizada', frame, nombreArchivo)
                    console.log('[Historial] Impresión finalizada registrada')
                } catch (e) {
                    console.error('[Historial] Error registrando finalización:', e)
                }
            }
        }
        _estabImprimiendo = imprimiendoAhora
    })

    // ─── Sincronizar IP desde el perfil del usuario al hacer login ────
    const userStore = useUserStore()
    watch(() => userStore.currentUser, async (usuario) => {
        if (usuario) {
            try {
                const datosUsuario = await getUserByUid(usuario.uid)
                if (datosUsuario && datosUsuario.printerIp) {
                    console.log('Sincronizando IP desde el perfil:', datosUsuario.printerIp)
                    backendUrl.value = datosUsuario.printerIp
                    localStorage.setItem(STORAGE_KEY, backendUrl.value)

                    if (!wsConectado.value) {
                        conectar()
                    }
                }
            } catch (err) {
                console.error('Error obteniendo IP del perfil del usuario:', err)
            }
        }
    }, { immediate: true })

    // ─── Interfaz pública del store ───────────────────────────────────
    return {
        // Estado
        backendUrl,
        wsConectado,
        subiendo,
        archivosGcode,
        estado,
        detecciones,
        urlStream,
        mensajeCancelacionAuto,
        ultimoFrame,

        // Getters
        estaImprimiendo,
        estaPausada,
        tieneArchivo,

        // Acciones
        conectar,
        desconectarWebSocket,
        enviarComando,
        pausarImpresion,
        reanudarImpresion,
        cancelarImpresion,
        iniciarImpresion,
        subirGcode,
        obtenerArchivos,
        seleccionarArchivo,
        guardarConfiguracion,
        inicializar,
        limpiarMensajeCancelacion,
        registrarError,
    }
})
