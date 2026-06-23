<template>
  <main class="explore">
    <div class="inner">

      <div class="panels">
        <AiRecommendPanel
          :is-active="activePanel === 'ai'"
          :loading="aiLoading"
          @activate="activePanel = 'ai'"
          @submit="onAiSubmit"
        />
        <SearchPanel
          :is-active="activePanel === 'search'"
          @activate="activePanel = 'search'"
          @submit="onSearchSubmit"
          @reset="onSearchReset"
        />
      </div>

      <RecentHistory
        :history="recentHistory"
        @restore="onRestoreHistory"
      />

      <GameResultGrid
        :type="resultMode"
        :games="resultGames"
        :loading="aiLoading || searchLoading"
        :restore-loading="restoreLoading"
        :submitted="submitted"
        @reset="onSearchReset"
      />

    </div>

    <!-- 커스텀 토스트 -->
    <ToastAlert ref="toastRef" />
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { gameAPI, recommendAPI } from '@/api/services'
import AiRecommendPanel from '@/components/explore/AiRecommendPanel.vue'
import SearchPanel from '@/components/explore/SearchPanel.vue'
import RecentHistory from '@/components/explore/RecentHistory.vue'
import GameResultGrid from '@/components/explore/GameResultGrid.vue'
import ToastAlert from '@/components/common/ToastAlert.vue'

const authStore = useAuthStore()
const toastRef = ref(null)

const activePanel = ref('ai')
const resultMode = ref('ai')
const submitted = ref(false)
const aiLoading = ref(false)
const searchLoading = ref(false)
const restoreLoading = ref(false)
const resultGames = ref([])
const recentHistory = ref([])

function toGames(data) {
  return Array.isArray(data) ? data : (data.results ?? [])
}

onMounted(async () => {
  if (authStore.isLoggedIn) {
    try {
      const { data } = await recommendAPI.logs()
      const logs = Array.isArray(data) ? data : (data.results ?? [])
      recentHistory.value = logs.map(l => ({
        id: l.id,
        query: l.prompt_input,
        date: new Date(l.created_at).toLocaleDateString('ko-KR').replace(/\. /g, '.').slice(0, -1),
        count: l.result_count ?? 0,
      }))
    } catch {
      recentHistory.value = []
    }
  }
})

async function onAiSubmit({ prompt }) {
  if (!authStore.isLoggedIn) {
    toastRef.value?.show('로그인한 사용자만 AI 추천을 이용할 수 있습니다.', 'warning')
    return
  }

  resultMode.value = 'ai'
  submitted.value = true
  aiLoading.value = true
  resultGames.value = []

  try {
    const { data } = await recommendAPI.create({ prompt_input: prompt })
    resultGames.value = toGames(data.games ?? data)
    recentHistory.value.unshift({
      id: data.id ?? Date.now(),
      query: prompt,
      date: new Date().toLocaleDateString('ko-KR').replace(/\. /g, '.').slice(0, -1),
      count: resultGames.value.length,
    })
  } catch {
    toastRef.value?.show('추천 요청 중 오류가 발생했어요.', 'error')
  } finally {
    aiLoading.value = false
  }
}

async function onSearchSubmit({ keyword }) {
  resultMode.value = 'search'
  submitted.value = true
  searchLoading.value = true
  resultGames.value = []

  try {
    if (keyword.trim()) {
      const { data } = await gameAPI.list({ q: keyword.trim() })
      resultGames.value = toGames(data)
    }
  } catch {
    toastRef.value?.show('검색 중 오류가 발생했어요.', 'error')
  } finally {
    searchLoading.value = false
  }
}

function onSearchReset() {
  submitted.value = false
  resultGames.value = []
}

async function onRestoreHistory(h) {
  resultMode.value = 'ai'
  submitted.value = true
  restoreLoading.value = true
  resultGames.value = []

  try {
    const { data } = await recommendAPI.logDetail(h.id)
    resultGames.value = toGames(data.games ?? data)
  } catch {
    toastRef.value?.show('기록 불러오기 중 오류가 발생했어요.', 'error')
  } finally {
    restoreLoading.value = false
  }
}
</script>

<style scoped>
.explore {
  background: #fafaf8;
  min-height: 100vh;
  padding: 40px 0 80px;
}
.inner {
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 40px;
}
.panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 48px;
}
</style>