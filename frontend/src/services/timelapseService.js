/**
 * Servicio de timelapses (Firebase).
 *
 * Gestiona la subida de vídeos timelapse a Firebase Storage
 * y su registro en la colección "videos" de Firestore.
 */
import { auth, db, storage } from './firebase'
import { ref as storageRef, uploadBytesResumable, getDownloadURL, deleteObject } from 'firebase/storage'
import { collection, addDoc, deleteDoc, doc, Timestamp } from 'firebase/firestore'

/**
 * Sube un blob de timelapse a Firebase Storage y crea el documento en Firestore.
 * Devuelve { id, downloadURL }.
 */
export async function uploadTimelapseBlob(blob, filename) {
  const user = auth.currentUser
  if (!user) throw new Error('Usuario no autenticado')

  // Subir archivo a Storage
  const path = `videos/${user.uid}/${filename}`
  const ref = storageRef(storage, path)
  await uploadBytesResumable(ref, blob)

  // Obtener URL de descarga
  const url = await getDownloadURL(ref)

  // Registrar en Firestore
  const docRef = await addDoc(collection(db, 'videos'), {
    userId: user.uid,
    name: filename,
    size: blob.size || 0,
    date: Timestamp.now(),
    storagePath: ref.fullPath,
    downloadURL: url,
  })

  return { id: docRef.id, downloadURL: url }
}

/**
 * Elimina un vídeo tanto de Firestore como de Storage.
 */
export async function deleteTimelapse(videoId, storagePath) {
  await deleteDoc(doc(db, 'videos', videoId))
  await deleteObject(storageRef(storage, storagePath))
}
