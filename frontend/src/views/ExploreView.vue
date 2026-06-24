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
          ref="searchPanelRef"
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
        :games="resultMode === 'search' ? pagedGames : resultGames"
        :loading="aiLoading || searchLoading"
        :restore-loading="restoreLoading"
        :submitted="submitted"
        :sort="searchSort"
        :total-count="totalCount"
        :current-page="currentPage"
        :total-pages="totalPages"
        @update:sort="onSortChange"
        @update:page="onPageChange"
        @reset="onSearchReset"
      />

    </div>

    <!-- 커스텀 토스트 -->
    <ToastAlert ref="toastRef" />
  </main>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { gameAPI, recommendAPI } from '@/api/services'
import AiRecommendPanel from '@/components/explore/AiRecommendPanel.vue'
import SearchPanel from '@/components/explore/SearchPanel.vue'
import RecentHistory from '@/components/explore/RecentHistory.vue'
import GameResultGrid from '@/components/explore/GameResultGrid.vue'
import ToastAlert from '@/components/common/ToastAlert.vue'

const authStore = useAuthStore()
const route = useRoute()
const toastRef = ref(null)
const searchPanelRef = ref(null)

const activePanel = ref('ai')
const resultMode = ref('ai')
const submitted = ref(false)
const aiLoading = ref(false)
const searchLoading = ref(false)
const restoreLoading = ref(false)
const resultGames = ref([])
const recentHistory = ref([])

// 프론트엔드 페이지네이션
const PAGE_SIZE = 20
const currentPage = ref(1)
const totalCount = computed(() => resultGames.value.length)
const totalPages = computed(() => Math.ceil(totalCount.value / PAGE_SIZE))
const pagedGames = computed(() =>
  resultGames.value.slice((currentPage.value - 1) * PAGE_SIZE, currentPage.value * PAGE_SIZE)
)

// 검색 모드 상태 (키워드 + 정렬 + 필터)
const searchKeyword = ref('')
const searchSort = ref('recent')   // recent | rating | price | discount
const searchFilters = ref(null)    // SearchPanel 에서 받은 구조화 필터

// 정렬값 → 백엔드 ordering 파라미터
const ORDERING = {
  recent: '-release_date',
  rating: '-metacritic_score',
  price: 'final_price',
}

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
  applyQueryFilter()
  if (route.query.q) applyQueryQ(route.query.q)
})

// 홈·Nav 검색 → ?q=keyword, 홈 카드 → ?filter=sale|new 로 진입 시 자동 검색
watch(() => route.query.filter, applyQueryFilter)
watch(() => route.query.q, applyQueryQ)

function applyQueryFilter() {
  const f = route.query.filter
  if (f === 'sale') {
    activePanel.value = 'search'
    searchSort.value = 'discount'
    runSearch()
  } else if (f === 'new') {
    activePanel.value = 'search'
    searchSort.value = 'recent'
    runSearch()
  }
}

async function applyQueryQ(q) {
  if (!q) return
  activePanel.value = 'search'
  searchKeyword.value = q
  // SearchPanel이 마운트된 후 setKeyword 호출
  await nextTick()
  searchPanelRef.value?.setKeyword(q)
  runSearch()
}

// 키워드 + 정렬 + 필터를 백엔드 list 파라미터로 합쳐 호출
function buildParams() {
  const params = {}
  if (searchKeyword.value.trim()) params.q = searchKeyword.value.trim()

  // 정렬
  if (searchSort.value === 'discount') {
    params.ordering = 'discount'   // 백엔드에서 할인 우선 + 이름순 처리
  } else {
    params.ordering = ORDERING[searchSort.value] ?? '-release_date'
  }

  // 구조화 필터
  const f = searchFilters.value
  if (f) {
    if (f.genres?.length) params.genre = f.genres
    if (f.platforms?.length) params.platform = f.platforms
    if (f.moods?.length) params.mood = f.moods
    if (f.playModes?.length) params.player_mode = f.playModes
    if (f.playtime && f.playtime !== 'all') params.playtime_bucket = f.playtime
    if (f.onSale) params.on_sale = true
    if (f.rating && f.rating !== 'all') params.metacritic_gte = f.rating
    if (f.price === 'free') params.free = true
    else if (f.price === '20000+') params.price_gte = 20000
    else if (f.price && f.price !== 'all') params.price_lte = f.price
  }
  return params
}

async function runSearch() {
  resultMode.value = 'search'
  submitted.value = true
  searchLoading.value = true
  currentPage.value = 1
  resultGames.value = []
  try {
    const res = await gameAPI.list(buildParams())
    resultGames.value = toGames(res.data)
  } catch {
    toastRef.value?.show('검색 중 오류가 발생했어요.', 'error')
  } finally {
    searchLoading.value = false
  }
}

function onPageChange(page) {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 정렬 셀렉트 변경 시 재조회
function onSortChange(value) {
  searchSort.value = value
  runSearch()
}

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

function onSearchSubmit({ keyword, filters }) {
  searchKeyword.value = keyword
  searchFilters.value = filters ?? null
  activePanel.value = 'search'
  runSearch()
}

function onSearchReset() {
  submitted.value = false
  resultGames.value = []
  searchKeyword.value = ''
  searchFilters.value = null
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