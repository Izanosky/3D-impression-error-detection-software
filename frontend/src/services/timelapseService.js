// src/services/timelapseService.js
import { auth, db, storage } from './firebase'
import { ref as storageRef, uploadBytesResumable, getDownloadURL, deleteObject } from 'firebase/storage'
import { collection, addDoc, deleteDoc, doc, Timestamp } from 'firebase/firestore'

/**
 * Sube un blob de timelapse a Firebase Storage y crea el documento en Firestore.
 * Devuelve un objeto con el id del documento y la URL de descarga.
 */
export async function uploadTimelapseBlob(blob, filename) {
  const user = auth.currentUser
  if (!user) throw new Error('Usuario no autenticado')

  const path = `videos/${user.uid}/${filename}`
  const ref = storageRef(storage, path)

  // sube el fichero (resumable por si es grande)
  await uploadBytesResumable(ref, blob)

  // obtener URL de descarga para mostrarla inmediatamente si se desea
  const url = await getDownloadURL(ref)

  const docRef = await addDoc(collection(db, 'videos'), {
    userId: user.uid,
    name: filename,
    size: blob.size || 0,
    date: Timestamp.now(),
    storagePath: ref.fullPath,
    downloadURL: url
  })

  return { id: docRef.id, downloadURL: url }
}

/**
 * Borra el vídeo tanto de Firestore como de Storage.
 */
export async function deleteTimelapse(videoId, storagePath) {
  await deleteDoc(doc(db, 'videos', videoId))
  await deleteObject(storageRef(storage, storagePath))
}
