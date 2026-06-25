import { ref } from 'vue'
import { gameAPI } from '@/api/services'

export function useGameSuggest() {
  const suggestions = ref([])
  const activeIdx = ref(-1)
  let timer = null
  let latestVal = ''

  // @input 이벤트에서 e.target.value를 넘기면 IME 조합 중인 글자도 포함
  function trigger(inputVal) {
    latestVal = inputVal
    clearTimeout(timer)
    activeIdx.value = -1
    if (!inputVal.trim()) {
      suggestions.value = []
      return
    }
    timer = setTimeout(async () => {
      const current = latestVal.trim()
      if (!current) { suggestions.value = []; return }
      try {
        const { data } = await gameAPI.suggest(current)
        suggestions.value = data
      } catch {
        suggestions.value = []
      }
    }, 280)
  }

  function onKeydown(e, onSelectSuggestion, onFallbackEnter) {
    if (e.key === 'ArrowDown' && suggestions.value.length) {
      e.preventDefault()
      activeIdx.value = Math.min(activeIdx.value + 1, suggestions.value.length - 1)
    } else if (e.key === 'ArrowUp' && suggestions.value.length) {
      e.preventDefault()
      activeIdx.value = Math.max(activeIdx.value - 1, -1)
    } else if (e.key === 'Enter') {
      if (activeIdx.value >= 0 && suggestions.value.length) {
        e.preventDefault()
        onSelectSuggestion(suggestions.value[activeIdx.value])
      } else if (onFallbackEnter) {
        e.preventDefault()
        onFallbackEnter()
      }
    } else if (e.key === 'Escape') {
      suggestions.value = []
      activeIdx.value = -1
    }
  }

  function clear() {
    suggestions.value = []
    activeIdx.value = -1
    clearTimeout(timer)
  }

  return { suggestions, activeIdx, trigger, onKeydown, clear }
}
