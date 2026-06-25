import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useNotificationStore = defineStore('notifications', () => {
  const refreshKey = ref(0)

  function refresh() {
    refreshKey.value++
  }

  return { refreshKey, refresh }
})
