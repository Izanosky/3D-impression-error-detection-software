// Logica de gestion de los usuarios en Firebase
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

const colRef = collection(db, 'users')

export const addUser = (data) =>
  addDoc(colRef, { ...data, Uid: getCurrentUserUUID(), createdAt: serverTimestamp() })

// Obtener usuario por email
export const getUserByMail = async (email) => {
  const q = query(colRef, where('email', '==', email))
  const snapshot = await getDocs(q)
  return snapshot.empty ? null : { id: snapshot.docs[0].id, ...snapshot.docs[0].data() }
}

// Obtener usuario por Uid
export const getUserByUid = async (uid) => {
  const q = query(colRef, where('Uid', '==', uid))
  const snapshot = await getDocs(q)
  return snapshot.empty ? null : { id: snapshot.docs[0].id, ...snapshot.docs[0].data() }
}

// Obtener nombre de usuario
export const getUserName = async (uid = null) => {
  const uuid = uid || getCurrentUserUUID()
  const q = query(colRef, where('Uid', '==', uuid))
  const snapshot = await getDocs(q)
  if (!snapshot.empty) {
    return snapshot.docs[0].data().displayName
  }
  return null
}

// Actualizacion de los datos de un usuario
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