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
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
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

const DUMMY_GAMES = Array.from({ length: 6 }, (_, i) => ({
  id: i + 1,
  title: '게임 제목',
  tags: ['장르', '플랫폼'],
  rating: 4.5,
}))

const recentHistory = ref([
  { id: 1, query: '스토리가 좋은 픽셀 RPG',      date: '2024.05.20', count: 6 },
  { id: 2, query: '멀티플레이 가능한 생존 게임',  date: '2024.05.18', count: 8 },
  { id: 3, query: '짧게 즐길 수 있는 퍼즐 게임', date: '2024.05.15', count: 5 },
  { id: 4, query: '감성적인 인디 게임 추천',      date: '2024.05.10', count: 7 },
])

async function onAiSubmit({ prompt }) {
  if (!authStore.isLoggedIn) {
    toastRef.value?.show('로그인한 사용자만 AI 추천을 이용할 수 있습니다.', 'warning')
    return
  }

  resultMode.value = 'ai'
  submitted.value = true
  aiLoading.value = true
  resultGames.value = []

  // TODO: POST /api/ai/recommend/ { prompt, filters }
  await new Promise(r => setTimeout(r, 1200))
  resultGames.value = DUMMY_GAMES
  aiLoading.value = false

  recentHistory.value.unshift({
    id: Date.now(),
    query: prompt,
    date: new Date().toLocaleDateString('ko-KR').replace(/\. /g, '.').slice(0, -1),
    count: DUMMY_GAMES.length,
  })
}

async function onSearchSubmit({ keyword }) {
  resultMode.value = 'search'
  submitted.value = true
  searchLoading.value = true
  resultGames.value = []

  // TODO: GET /api/games/search/?q=keyword
  await new Promise(r => setTimeout(r, 500))
  resultGames.value = keyword.trim() ? DUMMY_GAMES : []
  searchLoading.value = false
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

  // TODO: POST /api/ai/recommend/ { prompt: h.query }
  await new Promise(r => setTimeout(r, 900))
  resultGames.value = DUMMY_GAMES
  restoreLoading.value = false
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