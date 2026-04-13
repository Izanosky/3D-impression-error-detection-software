/**
 * Configuración de Firebase.
 *
 * Inicializa la app de Firebase y exporta los servicios
 * que usa la aplicación: Auth, Firestore y Storage.
 */
import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'
import { getStorage } from 'firebase/storage'

// Credenciales cargadas desde variables de entorno (.env.local)
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

const app = initializeApp(firebaseConfig)

// Servicios de Firebase exportados para uso en el resto de la app
export const auth = getAuth(app)                        // Autenticación
export const googleProvider = new GoogleAuthProvider()   // Proveedor de Google
export const db = getFirestore(app)                     // Base de datos Firestore
export const storage = getStorage(app)                  // Almacenamiento de archivos