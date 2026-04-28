// Servicio de historial de impresiones — guarda y recupera registros en Firebase
import { auth, db, storage } from './firebase'
import { ref as storageRef, uploadString, getDownloadURL, deleteObject } from 'firebase/storage'
import { collection, addDoc, query, where, getDocs, deleteDoc, doc, orderBy, Timestamp } from 'firebase/firestore'

// Guarda un nuevo registro en el historial de impresiones.
// - estado: 'finalizada', 'cancelada' o 'error'
// - captura: imagen en formato data URL (base64) del último frame de la cámara
// - nombreArchivo: nombre del archivo .gcode que se estaba imprimiendo
export async function guardarRegistro(estado, captura, nombreArchivo) {
    const usuario = auth.currentUser
    if (!usuario) throw new Error('Usuario no autenticado')

    // 1. Subimos la captura de pantalla a Firebase Storage
    const nombreCaptura = `captura_${Date.now()}.jpg`
    const ruta = `capturas/${usuario.uid}/${nombreCaptura}`
    const referencia = storageRef(storage, ruta)
    await uploadString(referencia, captura, 'data_url')

    // 2. Creamos el registro en la colección 'historial_impresiones' de Firestore
    await addDoc(collection(db, 'historial_impresiones'), {
        userId: usuario.uid,
        estado,
        nombreArchivo: nombreArchivo || 'Desconocido',
        fechaFin: Timestamp.now(),
        rutaCaptura: ruta,
    })
}

// Obtiene todos los registros del historial del usuario actual,
// ordenados del más reciente al más antiguo.
export async function obtenerHistorial() {
    const usuario = auth.currentUser
    if (!usuario) throw new Error('Usuario no autenticado')

    // Consultamos los registros del usuario ordenados por fecha descendente
    const consulta = query(
        collection(db, 'historial_impresiones'),
        where('userId', '==', usuario.uid),
        orderBy('fechaFin', 'desc')
    )

    const resultado = await getDocs(consulta)
    const registros = []

    // Para cada documento, intentamos obtener la URL de descarga de la captura
    for (const documento of resultado.docs) {
        const datos = documento.data()
        let urlCaptura = ''

        try {
            urlCaptura = await getDownloadURL(storageRef(storage, datos.rutaCaptura))
        } catch (e) {
            console.error('[Historial] Error obteniendo URL de la captura:', e)
        }

        registros.push({
            id: documento.id,
            estado: datos.estado,
            nombreArchivo: datos.nombreArchivo,
            fechaFin: datos.fechaFin,
            rutaCaptura: datos.rutaCaptura,
            urlCaptura,
        })
    }

    return registros
}

// Elimina un registro del historial:
// 1. Borra el documento de Firestore
// 2. Borra la captura de Firebase Storage
export async function eliminarRegistro(registro) {
    // Borrar el documento de la base de datos
    await deleteDoc(doc(db, 'historial_impresiones', registro.id))

    // Borrar la imagen de Storage (si falla no es crítico)
    try {
        await deleteObject(storageRef(storage, registro.rutaCaptura))
    } catch (e) {
        console.error('[Historial] Error eliminando captura de Storage:', e)
    }
}
