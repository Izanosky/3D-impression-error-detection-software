// src/services/usersService.js
import { db } from './firebase'
import {
  collection,
  addDoc,
  doc,
  getDoc,
  deleteDoc,
  updateDoc,
  onSnapshot,
  query,
  orderBy,
  serverTimestamp,
  where,
  getDocs
} from 'firebase/firestore'
import { getCurrentUserUUID } from './authService'

const colRef = collection(db, 'users')

export const addUser = (data) =>
  addDoc(colRef, { ...data, Uid: getCurrentUserUUID(), createdAt: serverTimestamp() })

export const getUserByMail = async (email) => {
  const q = query(colRef, where('email', '==', email))
  const snapshot = await getDocs(q)
  return snapshot.empty ? null : { id: snapshot.docs[0].id, ...snapshot.docs[0].data() }
}

export const getUserByUid = async (uid) => {
  const q = query(colRef, where('Uid', '==', uid))
  const snapshot = await getDocs(q)
  return snapshot.empty ? null : { id: snapshot.docs[0].id, ...snapshot.docs[0].data() }
}

export const getUserName = async (uid = null) => {
  const uuid = uid || getCurrentUserUUID()
  const q = query(colRef, where('Uid', '==', uuid))
  const querySnapshot = await getDocs(q)
  if (!querySnapshot.empty) {
    const userDoc = querySnapshot.docs[0]
    return userDoc.data().displayName
  }
  return null
}

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

// Se que da escuchando y lanza una query cada vez que hay un cambio, con toda la información actualizada
// export const subscribeToItems = (callback) => {
//   const uuid = getCurrentUserUUID()
//   console.log('subscribeToItems - UUID del usuario:', uuid)
  
//   if (!uuid) {
//     console.warn('No hay usuario autenticado')
//     return () => {}
//   }
  
//   return onSnapshot(
//     query(colRef, where('Uid', '==', uuid), orderBy('createdAt', 'desc')),
//     snapshot => {
//       console.log('Snapshot recibido, documentos:', snapshot.docs.length)
//       const data = snapshot.docs.map(d => ({ id: d.id, ...d.data() }))
//       console.log('Datos procesados:', data)
//       callback(data)
//     },
//     error => {
//       console.error('Error en subscribeToItems:', error)
//     }
//   )
// }