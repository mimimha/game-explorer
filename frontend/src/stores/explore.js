import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useExploreStore = defineStore('explore', () => {
  const savedState = ref(null)
  const resetSignal = ref(0)

  function save(state) {
    savedState.value = state
  }

  function restore() {
    const s = savedState.value
    savedState.value = null
    return s
  }

  function clear() {
    savedState.value = null
  }

  function requestReset() {
    savedState.value = null
    resetSignal.value++
  }

  return { savedState, resetSignal, save, restore, clear, requestReset }
})
