/**
 * Servicio de usuarios.
 *
 * Operaciones CRUD sobre la colección "users" de Firestore:
 * crear, buscar por email/UID, obtener nombre y actualizar perfil.
 */
import { db } from './firebase'
import {
  collection,
  addDoc,
  doc,
  updateDoc,
  query,
  where,
  getDocs,
  serverTimestamp,
} from 'firebase/firestore'
import { getCurrentUserUUID } from './authService'

// Referencia a la colección "users"
const colRef = collection(db, 'users')

/** Crea un nuevo documento de usuario en Firestore. */
export const addUser = (data) =>
  addDoc(colRef, { ...data, Uid: getCurrentUserUUID(), createdAt: serverTimestamp() })

/** Busca un usuario por su email. Devuelve el documento o null. */
export const getUserByMail = async (email) => {
  const q = query(colRef, where('email', '==', email))
  const snapshot = await getDocs(q)
  return snapshot.empty ? null : { id: snapshot.docs[0].id, ...snapshot.docs[0].data() }
}

/** Busca un usuario por su UID de Firebase Auth. Devuelve el documento o null. */
export const getUserByUid = async (uid) => {
  const q = query(colRef, where('Uid', '==', uid))
  const snapshot = await getDocs(q)
  return snapshot.empty ? null : { id: snapshot.docs[0].id, ...snapshot.docs[0].data() }
}

/** Obtiene el nombre del usuario dado su UID (o el del usuario actual). */
export const getUserName = async (uid = null) => {
  const uuid = uid || getCurrentUserUUID()
  const q = query(colRef, where('Uid', '==', uuid))
  const snapshot = await getDocs(q)
  if (!snapshot.empty) {
    return snapshot.docs[0].data().displayName
  }
  return null
}

/** Actualiza los datos de un usuario buscándolo por UID. */
export const updateUser = async (uid, data) => {
  const q = query(colRef, where('Uid', '==', uid))
  const snapshot = await getDocs(q)
  if (!snapshot.empty) {
    const docRef = doc(db, 'users', snapshot.docs[0].id)
    await updateDoc(docRef, data)
    return true
  }
  return false
}