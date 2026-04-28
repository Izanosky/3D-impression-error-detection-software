import { defineStore } from 'pinia'
import { ref } from 'vue'
import { subscribeToAuth } from '@/services/authService'
import { getUserName } from '@/services/usersService'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref(null)
  const userName = ref('')
  let unsubscribe = null

  function startAuthListener() {
    if (unsubscribe) return
    unsubscribe = subscribeToAuth(async (user) => {
      currentUser.value = user
      if (user) {
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