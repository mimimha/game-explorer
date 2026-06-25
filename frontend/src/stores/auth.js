import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = computed(() => !!user.value)

  const token = localStorage.getItem('token')
  if (token) {
    user.value = { token }
  }

  function login(userData, token) {
    localStorage.setItem('token', token)
    user.value = userData
  }

  function setProfile(userData) {
    if (user.value) {
      user.value = { ...user.value, ...userData }
    }
  }

  function logout() {
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, isLoggedIn, login, setProfile, logout }
})
