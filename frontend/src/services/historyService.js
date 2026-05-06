// Servicio de historial de impresiones — guarda y recupera registros en Firebase
import { auth, db } from './firebase'
import { collection, addDoc, query, where, getDocs, deleteDoc, doc, orderBy, Timestamp } from 'firebase/firestore'

// Guarda un nuevo registro en el historial de impresiones.
// - estado: 'finalizada', 'cancelada' o 'error'
// - nombreArchivo: nombre del archivo .gcode que se estaba imprimiendo
export async function guardarRegistro(estado, nombreArchivo) {
    const usuario = auth.currentUser
    if (!usuario) throw new Error('Usuario no autenticado')

    // Creamos el registro en la colección 'historial_impresiones' de Firestore
    // Ya no usamos Firebase Storage ni subimos imágenes.
    await addDoc(collection(db, 'historial_impresiones'), {
        userId: usuario.uid,
        estado,
        nombreArchivo: nombreArchivo || 'Desconocido',
        fechaFin: Timestamp.now(),
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

    for (const documento of resultado.docs) {
        const datos = documento.data()

        registros.push({
            id: documento.id,
            estado: datos.estado,
            nombreArchivo: datos.nombreArchivo,
            fechaFin: datos.fechaFin,
        })
    }

    return registros
}

// Elimina un registro del historial
export async function eliminarRegistro(registro) {
    // Borrar el documento de la base de datos
    await deleteDoc(doc(db, 'historial_impresiones', registro.id))
}
