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
// 페이지네이션은 클라이언트 분할(백엔드가 전체 목록을 한 번에 내려줌)
const AI_PAGE_SIZE = 5
const LIB_PAGE_SIZE = 20
const aiPage = ref(1)              // AI 결과 페이지
const searchPage = ref(1)          // 검색 결과 페이지

const pageSize = computed(() => resultMode.value === 'ai' ? AI_PAGE_SIZE : LIB_PAGE_SIZE)
const currentPage = computed(() => resultMode.value === 'ai' ? aiPage.value : searchPage.value)
const totalCount = computed(() => resultGames.value.length)
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

// 화면에 실제로 그릴 항목 (AI는 전체, 검색은 현재 페이지만)
const pagedGames = computed(() => {
  if (resultMode.value === 'ai') return resultGames.value
  const start = (currentPage.value - 1) * pageSize.value
  return resultGames.value.slice(start, start + pageSize.value)
})

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

onMounted(async () => {
  const saved = exploreStore.restore()
  if (saved) {
    resultMode.value = saved.resultMode
    resultGames.value = saved.resultGames
    searchKeyword.value = saved.searchKeyword
    searchSort.value = saved.searchSort
    searchFilters.value = saved.searchFilters
    submitted.value = saved.submitted
    if (saved.resultMode === 'ai') aiPage.value = saved.currentPage || 1
    else searchPage.value = saved.currentPage || 1
    activePanel.value = saved.activePanel
    await nextTick()
    if (saved.searchKeyword) searchPanelRef.value?.setKeyword(saved.searchKeyword)
    return
  }

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

async function runSearch() {
  resultMode.value = 'search'
  submitted.value = true
  searchLoading.value = true
  searchPage.value = 1            // 새 검색 → 1페이지부터
  resultGames.value = []
  try {
    const res = await gameAPI.list(buildParams())
    const data = res.data
    // 백엔드가 전체 목록을 한 번에 줌 → 페이지 분할은 클라이언트(pagedGames)에서
    resultGames.value = Array.isArray(data) ? data : (data.results ?? [])
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

// 페이지네이션 — 둘 다 클라이언트 슬라이스(재조회 없음)
function onPageChange(page) {
  if (resultMode.value === 'search') {
    searchPage.value = page
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