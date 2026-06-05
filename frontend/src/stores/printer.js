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
    const errorConexion = ref('')

    // Array para acumular snapshots de progresion durante la impresion
    const progresion = ref([])
    let intervaloProgresion = null
    let fechaInicio = null

    let websocket = null

    // Estado actual de la impresora (se sincroniza con el backend a traves de WebSocket)
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

    // Establece la conexion WebSocket con el backend
    function conectarWebSocket(manual = false) {
        if (!backendUrl.value) return

        const base = backendUrl.value.replace(/^https?:\/\//, '') // Elimina el http:// o https:// de la URL
        websocket = new WebSocket(`ws://${base}/ws`) // Crea la conexion WebSocket con el backend

        // Se ejecuta cuando se establece la conexion WebSocket
        websocket.onopen = () => {
            wsConectado.value = true
            errorConexion.value = ''
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

        // Cerramos la conexion del web socket
        websocket.onclose = () => {
            wsConectado.value = false
            estado.value.connected = false
            urlStream.value = ''
        }

        // Error en la conexion con el WebSocket
        websocket.onerror = () => {
            wsConectado.value = false
            // Solo mostramos el error si la conexion fue manual (boton de conectar)
            if (manual) {
                errorConexion.value = `No se pudo conectar con el backend en ${backendUrl.value}. Verifica que el servidor esté en ejecución y la IP sea correcta.`
            }
        }
    }

    // Cierra la conexion WebSocket
    function desconectarWebSocket(accion = false) {
        if (accion) {
            localStorage.setItem('printer_monitor_auto_connect', 'false')
        }
        websocket?.close()
        websocket = null
        wsConectado.value = false
    }

    // Envia un comando a OctoPrint a traves del WebSocket especificado mediante los argumentos
    function enviarComando(accion) {
        if (websocket?.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify({ action: accion }))
        }
    }

    // ─── Registro de progresion (cada 20 segundos) ─────────────────────

    // Captura un snapshot de temperatura y progreso y lo añade al array
    function capturarSnapshot() {
        const temps = estado.value.temperatures || {}
        const progreso = estado.value.job?.progress || 0
        progresion.value.push({
            t: Date.now(),
            tempExtrusor: temps.tool0?.actual ?? null,
            tempCama: temps.bed?.actual ?? null,
            porcentaje: Math.round(progreso * 100) / 100,
        })
    }

    // Inicia el intervalo de captura de snapshots
    function iniciarRegistroProgresion() {
        detenerRegistroProgresion()
        progresion.value = []
        fechaInicio = Date.now()
        // Capturar el primer snapshot inmediatamente
        capturarSnapshot()
        intervaloProgresion = setInterval(capturarSnapshot, 10000) // cada 10s
    }

    // Detiene el intervalo de captura
    function detenerRegistroProgresion() {
        if (intervaloProgresion) {
            clearInterval(intervaloProgresion)
            intervaloProgresion = null
        }
    }

    // ─── Acciones de impresion ────────────────────────────────────────

    function pausarImpresion() { enviarComando('pausar') } // Definimos una funcion para la pausa
    function reanudarImpresion() { enviarComando('reanudar') } // Definimos una funcion para reanudar

    // Inicia la impresion y comienza a registrar la progresion
    function iniciarImpresion() {
        if (estado.value.job) estado.value.job.progress = 0
        enviarComando('iniciar')
        iniciarRegistroProgresion()
    }

    // Registra un evento en el historial (cancelada, error, finalizada)
    async function registrarEnHistorial(tipo) {
        // Capturamos el ultimo snapshot antes de guardar
        capturarSnapshot()
        detenerRegistroProgresion()
        const nombreArchivo = estado.value.job?.file || 'Desconocido'
        const datosProgresion = [...progresion.value]
        // Intentamos usar fechaInicio; si no existe, derivamos del primer snapshot
        // o del tiempo transcurrido que reporta OctoPrint
        let inicio = fechaInicio
        if (!inicio && datosProgresion.length > 0) {
            inicio = datosProgresion[0].t
        }
        if (!inicio) {
            const elapsed = estado.value.job?.time_elapsed || 0
            inicio = Date.now() - (elapsed * 1000)
        }
        progresion.value = []
        fechaInicio = null
        try {
            await guardarRegistro(tipo, nombreArchivo, datosProgresion, inicio)
        } catch (e) {
            console.error(`[Historial] Error registrando ${tipo}:`, e)
        }
    }

    // Cancela la impresion manualmente y registra la cancelacion
    async function cancelarImpresion() {
        enviarComando('cancelar')
        await registrarEnHistorial('cancelada')
    }

    // Registra que la impresion se detuvo por un error detectado por la IA
    async function registrarError() {
        await registrarEnHistorial('error')
    }

    // ─── Gestion de archivos ──────────────────────────────────────────

    // Subimos un archivo seleccionado desde el selector de la pagina
    async function subirGcode(archivo) {
        if (!backendUrl.value) return { success: false, error: 'No hay URL del backend' }

        subiendo.value = true
        try {
            const formData = new FormData()
            formData.append('file', archivo)

            // Hacemos un POST al endpoint /api/subir de nuestro backend para enviar el archivo
            const respuesta = await fetch(`http://${backendUrl.value}/api/subir`, {
                method: 'POST',
                body: formData
            })
            const resultado = await respuesta.json() // Obtenemos el resultado de la peticion
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
            const respuesta = await fetch(`http://${backendUrl.value}/api/archivos`)
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
            const respuesta = await fetch(`http://${backendUrl.value}/api/archivos/seleccionar/${nombre}`, {
                method: 'POST'
            })
            const resultado = await respuesta.json()
            return resultado.success
        } catch (error) {
            console.error('Error seleccionando archivo:', error)
            return false
        }
    }

    // ─── Conexion y configuracion

    // Nos conectamos a nuestro backend a traves de la IP que se guardo en localStorage
    async function conectar(manual = false) {
        if (!backendUrl.value) return
        desconectarWebSocket(false)
        localStorage.setItem('printer_monitor_auto_connect', 'true')
        conectarWebSocket(manual)
        await obtenerArchivos()
    }

    // Limpia el mensaje de cancelacion automatica
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
            const autoConnect = localStorage.getItem('printer_monitor_auto_connect') !== 'false'
            if (autoConnect) {
                conectar()
            }
        }
    }

    // ─── Watchers ─────────────────────────────────────────────────────

    // Detecta inicio y fin de impresion
    let printing = false
    watch(estaImprimiendo, async (imprimiendoAhora) => {
        if (!printing && imprimiendoAhora) {
            // Acaba de empezar a imprimir: iniciar registro de progresion
            // (por si se inicio desde OctoPrint directamente, no desde nuestra UI)
            if (!intervaloProgresion) {
                iniciarRegistroProgresion()
            }
        }
        if (printing && !imprimiendoAhora) {
            // Acaba de terminar de imprimir
            const progreso = estado.value.job?.progress || 0
            if (progreso >= 99) {
                await registrarEnHistorial('finalizada')
                if (estado.value.job) estado.value.job.progress = 0 // Reseteamos el progreso correctamente
            }
        }
        printing = imprimiendoAhora
    }, { immediate: true })

    // Sincroniza la IP desde el perfil del usuario al hacer login
    watch(() => userStore.currentUser, async (usuario) => {
        if (!usuario) return
        try {
            const datosUsuario = await getUserByUid(usuario.uid)
            if (datosUsuario?.printerIp) {
                backendUrl.value = datosUsuario.printerIp
                localStorage.setItem(STORAGE_KEY, backendUrl.value)
                const autoConnect = localStorage.getItem('printer_monitor_auto_connect') !== 'false'
                if (!wsConectado.value && autoConnect) conectar()
            }
        } catch (err) {
            console.error('Error obteniendo IP del perfil del usuario:', err)
        }
    }, { immediate: true })

    // Devolvemos las funciones definidas
    return {
        backendUrl, wsConectado, subiendo, archivosGcode,
        estado, detecciones, urlStream, mensajeCancelacionAuto, errorConexion,
        estaImprimiendo, estaPausada, tieneArchivo,
        conectar, desconectarWebSocket, enviarComando,
        pausarImpresion, reanudarImpresion, cancelarImpresion,
        iniciarImpresion, subirGcode, obtenerArchivos,
        seleccionarArchivo, guardarConfiguracion, inicializar,
        limpiarMensajeCancelacion, registrarError,
    }
})
