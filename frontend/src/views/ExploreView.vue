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
        @delete="onDeleteHistory"
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
import { onBeforeRouteLeave } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useExploreStore } from '@/stores/explore'
import { gameAPI, recommendAPI } from '@/api/services'
import AiRecommendPanel from '@/components/explore/AiRecommendPanel.vue'
import SearchPanel from '@/components/explore/SearchPanel.vue'
import RecentHistory from '@/components/explore/RecentHistory.vue'
import GameResultGrid from '@/components/explore/GameResultGrid.vue'
import ToastAlert from '@/components/common/ToastAlert.vue'

const authStore = useAuthStore()
const exploreStore = useExploreStore()
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
// 검색(라이브러리)은 '서버 페이지네이션'(20개/페이지) → 게임이 늘어도 응답 일정.
// AI 추천은 결과 전체(≤10)를 한 화면에 표시(페이지네이션 없음).
const LIB_PAGE_SIZE = 20
const aiPage = ref(1)              // AI 결과 페이지(사실상 1)
const searchPage = ref(1)          // 검색 결과 페이지(서버에 요청)
const searchTotalCount = ref(0)    // 검색 전체 결과 수(서버 count)

const pageSize = computed(() =>
  resultMode.value === 'ai' ? Math.max(1, resultGames.value.length) : LIB_PAGE_SIZE)
const currentPage = computed(() => resultMode.value === 'ai' ? aiPage.value : searchPage.value)
const totalCount = computed(() =>
  resultMode.value === 'ai' ? resultGames.value.length : searchTotalCount.value)
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

// 서버가 이미 현재 페이지만 내려줌(검색) / AI는 전체 → resultGames 를 그대로 그린다
const pagedGames = computed(() => resultGames.value)

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

// AI 추천 응답(results: [{game, reason, match_score}]) → 카드 배열
// 관련도 match%(최고점=100% 기준 백분율)를 카드에 부여 → GameCard가 표시
function toRecGames(data) {
  const results = data?.results ?? (Array.isArray(data) ? data : [])
  const top = Math.max(1, ...results.map(r => (r && r.match_score) || 0))
  return results.map(r => {
    if (!r || !r.game) return r
    return {
      ...r.game,
      reason: r.reason,
      match: Math.max(1, Math.round((r.match_score || 0) / top * 100)),
    }
  })
}

// 추천 기록(과거 질의 목록) 로드 — 로그인 상태에서만
async function loadRecentHistory() {
  if (!authStore.isLoggedIn) return
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

onMounted(async () => {
  // 추천 기록은 복원 여부와 무관하게 항상 로드 → 상세 갔다 뒤로가기 해도 기록 유지
  await loadRecentHistory()

  const saved = exploreStore.restore()
  if (saved) {
    if (saved.resultMode === 'ai') {
      // AI 추천 결과에서 상세로 갔다 뒤로가기 → 그리드는 '전체 게임 목록'을 보여준다.
      // 추천 기록 태그는 유지되며(위에서 로드), 태그를 누르면(onRestoreHistory)
      // 그 추천에 해당하는 AI 게임들만 다시 보인다.
      activePanel.value = saved.activePanel || 'ai'
      searchKeyword.value = ''
      searchFilters.value = null
      searchSort.value = 'recent'
      runSearch()                 // 키워드·필터 없음 → 전체 게임
      return
    }
    // 검색 모드: 검색 조건 복원 후 그 페이지를 서버에서 재조회(페이지네이션 일관성).
    // (서버 분할이라 캐시된 한 페이지만으론 count 가 없어 페이지바가 깨짐 → 재조회)
    resultMode.value = 'search'
    searchKeyword.value = saved.searchKeyword
    searchSort.value = saved.searchSort
    searchFilters.value = saved.searchFilters
    searchPage.value = saved.currentPage || 1
    activePanel.value = saved.activePanel
    await nextTick()
    if (saved.searchKeyword) searchPanelRef.value?.setKeyword(saved.searchKeyword)
    runSearch(false)            // 저장된 페이지 그대로 재조회 → 결과·count 복원
    return
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

onBeforeRouteLeave((to) => {
  if (to.name === 'game-detail') {
    exploreStore.save({
      resultMode: resultMode.value,
      resultGames: resultGames.value,
      searchKeyword: searchKeyword.value,
      searchSort: searchSort.value,
      searchFilters: searchFilters.value,
      submitted: submitted.value,
      currentPage: currentPage.value,
      activePanel: activePanel.value,
    })
  } else {
    exploreStore.clear()
  }
})

watch(() => exploreStore.resetSignal, () => {
  submitted.value = false
  resultGames.value = []
  searchKeyword.value = ''
  searchFilters.value = null
  resultMode.value = 'ai'
  aiPage.value = 1
  searchPage.value = 1
  activePanel.value = 'ai'
  searchSort.value = 'recent'
  searchPanelRef.value?.reset?.()
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

async function runSearch(resetPage = true) {
  resultMode.value = 'search'
  submitted.value = true
  searchLoading.value = true
  if (resetPage) searchPage.value = 1   // 새 검색/정렬 → 1페이지부터
  resultGames.value = []
  try {
    const params = buildParams()
    params.page = searchPage.value       // 서버에 페이지 요청
    params.page_size = LIB_PAGE_SIZE
    const res = await gameAPI.list(params)
    const data = res.data
    // 서버 페이지네이션 응답 {count, results}. (혹시 배열이면 그대로 호환)
    if (Array.isArray(data)) {
      resultGames.value = data
      searchTotalCount.value = data.length
    } else {
      resultGames.value = data.results ?? []
      searchTotalCount.value = data.count ?? resultGames.value.length
    }
  } catch {
    toastRef.value?.show('검색 중 오류가 발생했어요.', 'error')
  } finally {
    searchLoading.value = false
  }
}

// 정렬 변경 시 재조회(1페이지부터)
function onSortChange(value) {
  searchSort.value = value
  runSearch()
}

// 페이지네이션 — 검색은 해당 페이지를 서버에서 재조회, AI는 전체라 페이지 의미 없음
function onPageChange(page) {
  if (resultMode.value === 'search') {
    searchPage.value = page
    runSearch(false)                     // 페이지 리셋 없이 그 페이지만 재조회
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
    resultGames.value = toRecGames(data)
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
}

async function onDeleteHistory(h) {
  try {
    await recommendAPI.logDelete(h.id)
    recentHistory.value = recentHistory.value.filter(item => item.id !== h.id)
  } catch {
    toastRef.value?.show('삭제 중 오류가 발생했어요.', 'error')
  }
}

async function onRestoreHistory(h) {
  resultMode.value = 'ai'
  submitted.value = true
  restoreLoading.value = true
  aiPage.value = 1
  resultGames.value = []

  try {
    const { data } = await recommendAPI.logDetail(h.id)
    resultGames.value = toRecGames(data)
  } catch {
    toastRef.value?.show('기록 불러오기 중 오류가 발생했어요.', 'error')
  } finally {
    restoreLoading.value = false
  }
}
</script>

<style scoped>
.explore {
  background: #faf5ec;
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