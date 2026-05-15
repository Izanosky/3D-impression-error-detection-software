import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useUserStore } from './user'
import { updateUser, getUserByUid } from '../services/usersService'
import { guardarRegistro } from '../services/historyService'

export const usePrinterStore = defineStore('printer', () => {
    const STORAGE_KEY = 'printer_monitor_backend_url' // Nombre de la clave en localStorage para guardar la URL

    const backendUrl = ref('') // URL del backend activa en memoria (se carga desde localStorage al iniciar)
    const wsConectado = ref(false)
    const subiendo = ref(false)
    const archivosGcode = ref([])
    const urlStream = ref('')
    const mensajeCancelacionAuto = ref('')

    let websocket = null

    // Estado actual de la impresora (se sincroniza con el backend a través de WebSocket)
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

    // Getters

    // Devuelve true si el estado de la impresora incluye 'print'
    const estaImprimiendo = computed(() =>
        estado.value.state?.toLowerCase().includes('print')
    )

    // Devuelve true si el estado de la impresora incluye 'pause'
    const estaPausada = computed(() =>
        estado.value.state?.toLowerCase().includes('pause')
    )

    const tieneArchivo = computed(() => {
        const archivo = estado.value.job?.file
        return !!archivo && archivo !== 'Sin archivo'
    })

    // WebSocket

    // Establece la conexión WebSocket con el backend
    function conectarWebSocket() {
        if (!backendUrl.value) return

        const base = backendUrl.value.replace(/^https?:\/\//, '') // Elimina el http:// o https:// de la URL
        websocket = new WebSocket(`ws://${base}/ws`) // Crea la conexión WebSocket con el backend

        // Se ejecuta cuando se establece la conexión WebSocket
        websocket.onopen = () => {
            wsConectado.value = true
            const baseIp = backendUrl.value.split(':')[0]
            urlStream.value = `http://${baseIp}/webcam/?action=stream`
        }

        // Se ejecuta cuando se recibe un mensaje del WebSocket
        websocket.onmessage = (event) => {
            try {
                const mensaje = JSON.parse(event.data)

                if (mensaje.type === 'update' && mensaje.data.status) {
                    estado.value = mensaje.data.status
                }
            } catch (error) {
                console.error('Error procesando mensaje WebSocket:', error)
            }
        }

        // Cerramos la conexión del web socket
        websocket.onclose = () => {
            wsConectado.value = false
            estado.value.connected = false
            urlStream.value = ''
        }

        // Error en la conexión con el WebSocket
        websocket.onerror = () => {
            wsConectado.value = false
        }
    }

    // Cierra la conexión WebSocket
    function desconectarWebSocket() {
        websocket?.close()
        websocket = null
    }

    // Envía un comando a OctoPrint a través del WebSocket especificado mediante los argumentos
    function enviarComando(accion) {
        if (websocket?.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify({ action: accion }))
        }
    }

    // ─── Acciones de impresión ────────────────────────────────────────

    function pausarImpresion() { enviarComando('pause') } // Definimos una función para la pausa
    function reanudarImpresion() { enviarComando('resume') } // Definimos una función para reanudar
    function iniciarImpresion() { enviarComando('start') } // Definimos una función para iniciar

    // Registra un evento en el historial (cancelada, error, finalizada)
    async function registrarEnHistorial(tipo) {
        const nombreArchivo = estado.value.job?.file || 'Desconocido'
        try {
            await guardarRegistro(tipo, nombreArchivo)
        } catch (e) {
            console.error(`[Historial] Error registrando ${tipo}:`, e)
        }
    }

    // Cancela la impresión manualmente y registra la cancelación
    async function cancelarImpresion() {
        enviarComando('cancel')
        await registrarEnHistorial('cancelada')
    }

    // Registra que la impresión se detuvo por un error detectado por la IA
    async function registrarError() {
        await registrarEnHistorial('error')
    }

    // ─── Gestión de archivos ──────────────────────────────────────────

    // Subimos un archivo seleccionado desde el selector de la página
    async function subirGcode(archivo) {
        if (!backendUrl.value) return { success: false, error: 'No hay URL del backend' }

        subiendo.value = true
        try {
            const formData = new FormData()
            formData.append('file', archivo)

            // Hacemos un POST al endpoint /api/upload de nuestro backend para enviar el archivo
            const respuesta = await fetch(`http://${backendUrl.value}/api/upload`, {
                method: 'POST',
                body: formData
            })
            const resultado = await respuesta.json() // Obtenemos el resultado de la petición
            await obtenerArchivos() // Obtenemos la lista actualizada de archivos
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
            // Como antes, utilizamos un endpoint definido en nuestro backend para obtener dichos ficheros
            const respuesta = await fetch(`http://${backendUrl.value}/api/files`)
            const datos = await respuesta.json()
            archivosGcode.value = datos.files || [] // Obtenemos los ficheros
        } catch (error) {
            console.error('Error obteniendo archivos:', error)
            archivosGcode.value = []
        }
    }

    // Selecciona un archivo de la lista para enviarlo a imprimir
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

    // ─── Conexión y configuración

    // Nos conectamos a nuestro backend a traves de la IP que se guardó en localStorage
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

    const userStore = useUserStore()

    // Guarda la IP del backend en localStorage y en el perfil del usuario
    function guardarConfiguracion(url) {
        backendUrl.value = url.replace(/^https?:\/\//, '')
        localStorage.setItem(STORAGE_KEY, backendUrl.value)

        if (userStore.currentUser) {
            updateUser(userStore.currentUser.uid, { printerIp: backendUrl.value })
                .catch(err => console.error('Error guardando IP en el perfil:', err))
        }
    }

    // Iniciamos el store con la url guardada y tratamos de conectar con el WebSocket
    function inicializar() {
        const urlGuardada = localStorage.getItem(STORAGE_KEY)
        if (urlGuardada) {
            backendUrl.value = urlGuardada
            conectar()
        }
    }

    // ─── Watchers ─────────────────────────────────────────────────────

    // Detecta fin de impresión exitosa cuando el progreso es mayor o igual al 99%
    let printing = false
    watch(estaImprimiendo, async (imprimiendoAhora) => {
        if (printing && !imprimiendoAhora) {
            const progreso = estado.value.job?.progress || 0
            if (progreso >= 99) {
                await registrarEnHistorial('finalizada')
            }
        }
        printing = imprimiendoAhora
    })

    // Sincroniza la IP desde el perfil del usuario al hacer login
    watch(() => userStore.currentUser, async (usuario) => {
        if (!usuario) return
        try {
            const datosUsuario = await getUserByUid(usuario.uid)
            if (datosUsuario?.printerIp) {
                backendUrl.value = datosUsuario.printerIp
                localStorage.setItem(STORAGE_KEY, backendUrl.value)
                if (!wsConectado.value) conectar()
            }
        } catch (err) {
            console.error('Error obteniendo IP del perfil del usuario:', err)
        }
    }, { immediate: true })

    // Devolvemos las funciones definidas
    return {
        backendUrl, wsConectado, subiendo, archivosGcode,
        estado, detecciones, urlStream, mensajeCancelacionAuto,
        estaImprimiendo, estaPausada, tieneArchivo,
        conectar, desconectarWebSocket, enviarComando,
        pausarImpresion, reanudarImpresion, cancelarImpresion,
        iniciarImpresion, subirGcode, obtenerArchivos,
        seleccionarArchivo, guardarConfiguracion, inicializar,
        limpiarMensajeCancelacion, registrarError,
    }
})
