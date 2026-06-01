// Servicio para el historial de impresiones
import { db } from './firebase'
import {
    collection,
    addDoc,
    query,
    where,
    getDocs,
    deleteDoc,
    doc,
    orderBy,
    Timestamp,
} from 'firebase/firestore'
import { getCurrentUserUUID } from './authService'

// Definimos la coleccion
const colRef = collection(db, 'historial_impresiones')

// Función para guardar una registro en el historial de impresiones
// progresion: array de snapshots { t, tempExtrusor, tempCama, porcentaje }
// fechaInicioMs: timestamp en milisegundos del inicio de la impresión
export const guardarRegistro = (estado, nombreArchivo, progresion = [], fechaInicioMs = null) =>
    addDoc(colRef, {
        userId: getCurrentUserUUID(),
        estado,
        nombreArchivo: nombreArchivo || 'Desconocido',
        fechaInicio: fechaInicioMs ? Timestamp.fromMillis(fechaInicioMs) : null,
        fechaFin: Timestamp.now(),
        progresion,
    })


// Funcion para obtener el historial de impresiones 
export const obtenerHistorial = async () => {
    const q = query(
        colRef,
        where('userId', '==', getCurrentUserUUID()),
        orderBy('fechaFin', 'desc')
    )

    const snapshot = await getDocs(q)
    return snapshot.docs.map((documento) => ({
        id: documento.id,
        ...documento.data(),
    }))
}

// Funcion para eliminar un registro del historial
export const eliminarRegistro = (registro) =>
    deleteDoc(doc(db, 'historial_impresiones', registro.id))
