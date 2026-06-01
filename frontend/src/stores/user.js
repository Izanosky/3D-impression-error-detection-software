import { defineStore } from 'pinia'
import { ref } from 'vue'
import { subscribeToAuth, isSigningUp } from '@/services/authService'
import { getUserName } from '@/services/usersService'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref(null)
  const userName = ref('')
  let unsubscribe = null

  // Esto lo hacemos para mantener el estado del usuario al recargar la pagina
  function startAuthListener() {
    if (unsubscribe) return // Si ya hay un listener, no hacemos nada
    unsubscribe = subscribeToAuth(async (user) => {
      // Si estamos en proceso de registro, ignoramos el evento para evitar el flash
      if (isSigningUp) return
      // Solo consideramos al usuario como autenticado si ha verificado su email
      // Esto evita el flash de "logueado" durante el registro antes de cerrar sesion
      const usuarioVerificado = user?.emailVerified ? user : null
      currentUser.value = usuarioVerificado
      if (usuarioVerificado) { // Si hay usuario logeado, obtenemos su nombre
        try {
          const name = await getUserName(user.uid)
          userName.value = name || user.email
        } catch (e) {
          console.error('Error fetching user name:', e)
          userName.value = user.email
        }
      } else {
        userName.value = ''
      }
    })
  }

  function stopAuthListener() {
    if (unsubscribe) unsubscribe()
    unsubscribe = null
  }

  // Iniciar el listener automáticamente al crear el store
  startAuthListener()

  return { currentUser, userName, startAuthListener, stopAuthListener }
})