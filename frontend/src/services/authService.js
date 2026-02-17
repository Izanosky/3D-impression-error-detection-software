// src/services/authService.js
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  sendPasswordResetEmail
} from 'firebase/auth'
import { auth } from './firebase'
import { addUser } from './usersService'

export const getCurrentUserUUID = () => auth.currentUser?.uid

export const signUp = async (emailValue, passwordValue, nameValue) => {
  await createUserWithEmailAndPassword(auth, emailValue, passwordValue)
  await addUser({ email: emailValue, displayName: nameValue })
}

export const signIn = (email, password) =>
  signInWithEmailAndPassword(auth, email, password)

export const signOut = () => firebaseSignOut(auth)

export const resetPassword = (email) =>
  sendPasswordResetEmail(auth, email)

export const subscribeToAuth = (callback) =>
  onAuthStateChanged(auth, (user) => callback(user))

