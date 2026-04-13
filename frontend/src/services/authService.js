/**
 * Servicio de autenticación.
 *
 * Funciones para registrar, iniciar sesión, cerrar sesión
 * y recuperar contraseña usando Firebase Auth.
 */
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  sendPasswordResetEmail
} from 'firebase/auth'
import { auth } from './firebase'
import { addUser } from './usersService'

/** Devuelve el UID del usuario autenticado actual, o null. */
export const getCurrentUserUUID = () => auth.currentUser?.uid

/** Registra un nuevo usuario con email/contraseña y lo guarda en Firestore. */
export const signUp = async (emailValue, passwordValue, nameValue) => {
  await createUserWithEmailAndPassword(auth, emailValue, passwordValue)
  await addUser({ email: emailValue, displayName: nameValue })
}

/** Inicia sesión con email y contraseña. */
export const signIn = (email, password) =>
  signInWithEmailAndPassword(auth, email, password)

/** Cierra la sesión actual. */
export const signOut = () => firebaseSignOut(auth)

/** Envía un correo para restablecer la contraseña. */
export const resetPassword = (email) =>
  sendPasswordResetEmail(auth, email)

/** Se suscribe a cambios en el estado de autenticación. */
export const subscribeToAuth = (callback) =>
  onAuthStateChanged(auth, (user) => callback(user))
