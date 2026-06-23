// import { ref, computed } from 'vue'
// import { defineStore } from 'pinia'
// import { login as apiLogin, logout as apiLogout, fetchMyProfile } from '@/services/api'

// export const useAuthStore = defineStore('auth', () => {
//   const user = ref(null)
//   const loading = ref(false)

//   // 앱 시작 시 토큰이 있으면 프로필 가져오기
//   const token = localStorage.getItem('access_token')
//   if (token) {
//     fetchMyProfile()
//       .then(data => { user.value = data })
//       .catch(() => { user.value = null })
//   }

//   const isLoggedIn = computed(() => !!user.value)

//   async function login(username, password) {
//     loading.value = true
//     try {
//       const data = await apiLogin(username, password)
//       user.value = data.user
//       return data
//     } finally {
//       loading.value = false
//     }
//   }

//   async function logout() {
//     loading.value = true
//     try {
//       await apiLogout()
//     } finally {
//       user.value = null
//       loading.value = false
//     }
//   }

//   return { user, loading, isLoggedIn, login, logout }
// })