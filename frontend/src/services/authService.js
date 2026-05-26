// Todo lo relacionado con autenticación proporcionado por FireBase
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
  sendEmailVerification
} from 'firebase/auth'
import { auth } from './firebase'
import { addUser } from './usersService'

export const getCurrentUserUUID = () => auth.currentUser?.uid

// Flag para indicar que estamos en proceso de registro
// El store lo usa para ignorar el onAuthStateChanged que se dispara durante el registro
export let isSigningUp = false

export const signUp = async (emailValue, passwordValue, nameValue) => {
  isSigningUp = true
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, emailValue, passwordValue)
    await addUser({ email: emailValue, displayName: nameValue })
    // Enviamos el correo de verificación al usuario recién creado
    await sendEmailVerification(userCredential.user)
    // Cerramos la sesión para que no pueda acceder sin verificar
    await firebaseSignOut(auth)
  } finally {
    isSigningUp = false
  }
}

export const signIn = (email, password) =>
  signInWithEmailAndPassword(auth, email, password)


export const signOut = () => firebaseSignOut(auth)

export const resetPassword = (email) =>
  sendPasswordResetEmail(auth, email)

export const subscribeToAuth = (callback) =>
  onAuthStateChanged(auth, (user) => callback(user))
