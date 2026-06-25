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
        :games="pagedGames"
        :loading="aiLoading || searchLoading"
        :restore-loading="restoreLoading"
        :submitted="submitted"
        :sort="searchSort"
        :current-page="currentPage"
        :total-pages="totalPages"
        :total-count="totalCount"
        @update:sort="onSortChange"
        @reset="onSearchReset"
        @page-change="onPageChange"
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
const resultGames = ref([])        // 원본 목록 (검색: 서버 페이지 / AI: 전체 ≤10)
const recentHistory = ref([])

// 페이지네이션 상태
const AI_PAGE_SIZE = 5
const LIB_PAGE_SIZE = 20           // 백엔드 PAGE_SIZE 와 일치
const aiPage = ref(1)              // AI 결과 클라이언트 페이지
const searchPage = ref(1)          // 검색 결과 서버 페이지
const searchTotalPages = ref(1)
const searchCount = ref(0)

// 화면에 실제로 그릴 항목
const pagedGames = computed(() => {
  if (resultMode.value === 'ai') {
    const start = (aiPage.value - 1) * AI_PAGE_SIZE
    return resultGames.value.slice(start, start + AI_PAGE_SIZE)
  }
  return resultGames.value         // 검색: 서버가 이미 페이지 슬라이스를 줌
})
const currentPage = computed(() => resultMode.value === 'ai' ? aiPage.value : searchPage.value)
const totalPages = computed(() => resultMode.value === 'ai'
  ? Math.max(1, Math.ceil(resultGames.value.length / AI_PAGE_SIZE))
  : searchTotalPages.value)
const totalCount = computed(() => resultMode.value === 'ai'
  ? resultGames.value.length : searchCount.value)

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

onMounted(async () => {
  if (authStore.isLoggedIn) {
    try {
      const { data } = await recommendAPI.logs()
      const logs = Array.isArray(data) ? data : (data.results ?? [])
      recentHistory.value = logs.map(l => ({
        id: l.log_id,
        query: l.prompt_input,
        date: new Date(l.created_at).toLocaleDateString('ko-KR').replace(/\. /g, '.').slice(0, -1),
        count: l.result_count ?? 0,
      }))
    } catch {
      recentHistory.value = []
    }
  }
  // 진입 쿼리에 따라: ?filter=sale|new → 해당 검색, ?q= → 키워드 검색,
  // 아무것도 없으면 기본으로 전체 게임 목록을 바로 보여준다.
  if (route.query.filter) {
    applyQueryFilter()
  } else if (route.query.q) {
    applyQueryQ(route.query.q)
  } else {
    activePanel.value = 'search'
    runSearch()
  }
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
  const params = { page: searchPage.value }
  if (searchKeyword.value.trim()) params.q = searchKeyword.value.trim()

  // 정렬 (할인순은 on_sale 필터 + 정가 내림차순)
  if (searchSort.value === 'discount') {
    params.on_sale = true
    params.ordering = '-initial_price'
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

async function runSearch(page = 1) {
  resultMode.value = 'search'
  submitted.value = true
  searchLoading.value = true
  searchPage.value = page
  resultGames.value = []
  try {
    const res = await gameAPI.list(buildParams())
    const data = res.data
    resultGames.value = Array.isArray(data) ? data : (data.results ?? [])
    searchCount.value = Array.isArray(data)
      ? data.length : (data.count ?? resultGames.value.length)
    searchTotalPages.value = Math.max(1, Math.ceil(searchCount.value / LIB_PAGE_SIZE))
  } catch {
    toastRef.value?.show('검색 중 오류가 발생했어요.', 'error')
  } finally {
    searchLoading.value = false
  }
}

// 정렬 셀렉트 변경 시 1페이지부터 재조회
function onSortChange(value) {
  searchSort.value = value
  runSearch(1)
}

// 페이지네이션 — 검색은 서버 재조회, AI는 클라이언트 슬라이스
function onPageChange(page) {
  if (resultMode.value === 'search') {
    runSearch(page)
  } else {
    aiPage.value = page
  }
}

async function onAiSubmit({ prompt }) {
  if (!authStore.isLoggedIn) {
    toastRef.value?.show('로그인한 사용자만 AI 추천을 이용할 수 있습니다.', 'warning')
    return
  }

  resultMode.value = 'ai'
  submitted.value = true
  aiLoading.value = true
  aiPage.value = 1
  resultGames.value = []

  try {
    const { data } = await recommendAPI.create({ prompt_input: prompt })
    // 추천 응답 results = [{game, reason, match_score}] → 카드용 game 으로 펴기
    resultGames.value = (data.results ?? data.games ?? []).map(r => r.game ?? r)
    recentHistory.value.unshift({
      id: data.log_id ?? Date.now(),
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
  searchPage.value = 1
  aiPage.value = 1
  searchTotalPages.value = 1
  searchCount.value = 0
}

async function onRestoreHistory(h) {
  resultMode.value = 'ai'
  submitted.value = true
  restoreLoading.value = true
  aiPage.value = 1
  resultGames.value = []

  try {
    const { data } = await recommendAPI.logDetail(h.id)
    resultGames.value = (data.results ?? data.games ?? []).map(r => r.game ?? r)
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