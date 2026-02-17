// src/stores/user.js
import { defineStore } from 'pinia'
import { ref, onMounted, onUnmounted } from 'vue'
import { subscribeToAuth } from '@/services/authService'
import { getUserName } from '@/services/usersService'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref(null)
  const userName = ref('')
  let unsubscribe = null

  const startAuthListener = () => {
    if (unsubscribe) return
    unsubscribe = subscribeToAuth(async (user) => {
      currentUser.value = user
      if (user) {
        try {
          const name = await getUserName(user.uid)
          userName.value = name || user.email // Fallback to email if no name
        } catch (e) {
          console.error('Error fetching user name:', e)
          userName.value = user.email
        }
      } else {
        userName.value = ''
      }
    })
  }

  const stopAuthListener = () => {
    if (unsubscribe) unsubscribe()
    unsubscribe = null
  }

  const usuarioLogueado = () => {
    return currentUser.value !== null
  }

  onMounted(startAuthListener)
  onUnmounted(stopAuthListener)

  return { currentUser, userName, startAuthListener, stopAuthListener, usuarioLogueado }
})