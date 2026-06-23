import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = computed(() => !!user.value)

  // 앱 시작 시 토큰 있으면 로그인 상태로
  const token = localStorage.getItem('access_token')
  if (token) {
    // 간단히 토큰 존재 여부로만 처리 (추후 /api/users/me/ 연동)
    user.value = { token }
  }

  function login(userData) {
    user.value = userData
  }

  function logout() {
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, isLoggedIn, login, logout }
})