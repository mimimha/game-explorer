<template>
  <div class="panel" :class="{ active: isActive }" @click="$emit('activate')">
    <div class="panel-header">
      <h2>
        검색으로 찾기
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
        </svg>
      </h2>
      <p class="desc">키워드와 필터로 원하는 게임을 찾아보세요. (실제 보유 데이터 기준)</p>
    </div>

    <div class="search-wrap">
      <input
        v-model="keyword"
        type="text"
        placeholder="게임 제목을 검색하세요"
        class="search-input"
        @focus="$emit('activate')"
        @keydown.enter="handleSubmit"
      />
      <button class="search-btn" @click.stop="handleSubmit">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" width="16">
          <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
        </svg>
      </button>
    </div>

    <div class="filter-bar">
      <div class="filter-bar-left">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="14">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75" />
        </svg>
        필터
      </div>
      <button class="reset-btn" @click.stop="reset">초기화 ↺</button>
    </div>

    <div v-if="loading" class="opt-loading">필터 불러오는 중…</div>

    <template v-else>
      <!-- 장르 (다중) -->
      <div v-if="genreOptions.length" class="frow">
        <span class="flabel">장르</span>
        <div class="chips">
          <button
            v-for="g in genreOptions"
            :key="g.id"
            class="chip"
            :class="{ on: filters.genres.includes(g.id) }"
            @click.stop="toggleGenre(g.id)"
          >{{ g.label }} <span class="cnt">{{ g.count }}</span></button>
        </div>
      </div>

      <!-- 분위기/무드 (다중) -->
      <div v-if="moodOptions.length" class="frow">
        <span class="flabel">분위기</span>
        <div class="chips">
          <button
            v-for="m in moodOptions"
            :key="m.id"
            class="chip"
            :class="{ on: filters.moods.includes(m.id) }"
            @click.stop="toggleMood(m.id)"
          >{{ m.label }} <span class="cnt">{{ m.count }}</span></button>
        </div>
      </div>

      <!-- 플레이타임 (단일) -->
      <div v-if="playtimeOptions.length" class="frow">
        <span class="flabel">플레이타임</span>
        <div class="chips">
          <button
            v-for="o in playtimeOptions"
            :key="o.value"
            class="chip"
            :class="{ on: filters.playtime === o.value }"
            @click.stop="filters.playtime = o.value"
          >{{ o.label }}<span v-if="o.count != null" class="cnt">{{ o.count }}</span></button>
        </div>
      </div>

      <!-- 플레이 인원 (다중) -->
      <div v-if="playModeOptions.length" class="frow">
        <span class="flabel">인원</span>
        <div class="chips">
          <button
            v-for="o in playModeOptions"
            :key="o.key"
            class="chip"
            :class="{ on: filters.playModes.includes(o.key) }"
            @click.stop="togglePlayMode(o.key)"
          >{{ o.label }} <span class="cnt">{{ o.count }}</span></button>
        </div>
      </div>

      <!-- 플랫폼 (다중, 그룹) -->
      <div v-if="platformBuckets.length" class="frow">
        <span class="flabel">플랫폼</span>
        <div class="chips">
          <button
            v-for="b in platformBuckets"
            :key="b.key"
            class="chip"
            :class="{ on: filters.platforms.includes(b.key) }"
            @click.stop="togglePlatform(b.key)"
          >{{ b.label }}</button>
        </div>
      </div>

      <!-- 가격 (단일) -->
      <div v-if="priceOptions.length" class="frow">
        <span class="flabel">가격</span>
        <div class="chips">
          <button
            v-for="o in priceOptions"
            :key="o.value"
            class="chip"
            :class="{ on: filters.price === o.value }"
            @click.stop="filters.price = o.value"
          >{{ o.label }}</button>
        </div>
      </div>

      <!-- 평점 (단일) -->
      <div v-if="ratingOptions.length" class="frow">
        <span class="flabel">평점</span>
        <div class="chips">
          <button
            v-for="o in ratingOptions"
            :key="o.value"
            class="chip"
            :class="{ on: filters.rating === o.value }"
            @click.stop="filters.rating = o.value"
          >{{ o.label }}</button>
        </div>
      </div>

      <!-- 할인 중 (토글) -->
      <div v-if="onSaleCount > 0" class="frow">
        <span class="flabel">기타</span>
        <div class="chips">
          <button
            class="chip"
            :class="{ on: filters.onSale }"
            @click.stop="filters.onSale = !filters.onSale"
          >할인 중 <span class="cnt">{{ onSaleCount }}</span></button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { gameAPI } from '@/api/services'

defineProps({
  isActive: { type: Boolean, default: false },
})
const emit = defineEmits(['activate', 'submit', 'reset'])

// ── 표시용 매핑(데이터에 새 값이 생기면 영문 그대로 노출) ──
const GENRE_KO = {
  Action: '액션', Shooter: '슈팅', RPG: 'RPG', Indie: '인디',
  Adventure: '어드벤처', Puzzle: '퍼즐', Platformer: '플랫포머',
  'Massively Multiplayer': '대규모 멀티', Simulation: '시뮬레이션',
  Sports: '스포츠', Racing: '레이싱', Arcade: '아케이드',
}
// 플랫폼 버킷 → 실제 적재된 platform_name 들
const PLATFORM_BUCKETS_DEF = [
  { key: 'Windows', label: 'Windows', names: ['PC'] },
  { key: 'Mac', label: 'Mac', names: ['macOS'] },
  { key: 'Linux', label: 'Linux', names: ['Linux'] },
  { key: 'Mobile', label: '모바일', names: ['Android', 'iOS'] },
]
const NON_CONSOLE = new Set(['PC', 'macOS', 'Linux', 'Android', 'iOS', 'Web'])

const keyword = ref('')
const loading = ref(true)
const options = ref({
  genres: [], platforms: [], moods: [], price: {}, metacritic: {},
  playtime: {}, player_mode: {}, on_sale_count: 0,
})

const filters = ref({
  genres: [],        // genre tag_id 배열
  platforms: [],     // 버킷 key 배열
  moods: [],         // mood_id 배열
  playModes: [],     // 'single' | 'multi' | 'coop' 배열
  playtime: 'all',   // all | short | medium | long
  price: 'all',      // all | free | 5000 | 10000 | 20000 | 20000+
  rating: 'all',     // all | 90 | 80 | 70
  onSale: false,
})

const genreOptions = computed(() =>
  (options.value.genres || []).map(g => ({
    id: g.id, count: g.count, label: GENRE_KO[g.name] ?? g.name,
  })),
)

// 적재된 플랫폼 이름 집합 기준으로 버킷 구성(없는 버킷은 숨김, 콘솔은 동적 산출)
const platformBuckets = computed(() => {
  const present = new Set((options.value.platforms || []).map(p => p.name))
  const buckets = PLATFORM_BUCKETS_DEF
    .map(b => ({ ...b, names: b.names.filter(n => present.has(n)) }))
    .filter(b => b.names.length)
  const consoleNames = [...present].filter(n => !NON_CONSOLE.has(n))
  if (consoleNames.length) {
    buckets.push({ key: 'Console', label: '콘솔', names: consoleNames })
  }
  return buckets
})

const priceOptions = computed(() => {
  const p = options.value.price || {}
  if (p.max == null) return []
  const free = p.free_count ? ` (${p.free_count})` : ''
  return [
    { value: 'all', label: '전체' },
    { value: 'free', label: `무료${free}` },
    { value: '5000', label: '5천원 이하' },
    { value: '10000', label: '1만원 이하' },
    { value: '20000', label: '2만원 이하' },
    { value: '20000+', label: '2만원 이상' },
  ]
})

const ratingOptions = computed(() => {
  const m = options.value.metacritic || {}
  if (m.max == null) return []
  const opts = [{ value: 'all', label: '전체' }]
  for (const t of [90, 80, 70]) {
    if (m.max >= t) opts.push({ value: String(t), label: `${t}점 이상` })
  }
  return opts
})

const onSaleCount = computed(() => options.value.on_sale_count || 0)

// 무드 — 백엔드가 한국어 라벨로 내려줌
const moodOptions = computed(() =>
  (options.value.moods || []).map(m => ({ id: m.id, count: m.count, label: m.name })),
)

// 플레이타임 버킷 (개수 0인 구간은 숨김)
const PLAYTIME_DEF = [
  { key: 'short', label: '짧은 (~10시간)' },
  { key: 'medium', label: '보통 (10~40시간)' },
  { key: 'long', label: '긴 (40시간~)' },
]
const playtimeOptions = computed(() => {
  const b = options.value.playtime?.buckets
  if (!b) return []
  const opts = [{ value: 'all', label: '전체', count: null }]
  for (const d of PLAYTIME_DEF) {
    if ((b[d.key] || 0) > 0) opts.push({ value: d.key, label: d.label, count: b[d.key] })
  }
  return opts.length > 1 ? opts : []
})

// 플레이 인원 (개수 0인 모드는 숨김)
const PLAYMODE_DEF = [
  { key: 'single', label: '싱글' },
  { key: 'multi', label: '멀티' },
  { key: 'coop', label: '협동' },
]
const playModeOptions = computed(() => {
  const pm = options.value.player_mode || {}
  return PLAYMODE_DEF
    .filter(d => (pm[d.key] || 0) > 0)
    .map(d => ({ key: d.key, label: d.label, count: pm[d.key] }))
})

function toggleGenre(id) {
  const i = filters.value.genres.indexOf(id)
  if (i === -1) filters.value.genres.push(id)
  else filters.value.genres.splice(i, 1)
}
function togglePlatform(key) {
  const i = filters.value.platforms.indexOf(key)
  if (i === -1) filters.value.platforms.push(key)
  else filters.value.platforms.splice(i, 1)
}
function toggleMood(id) {
  const i = filters.value.moods.indexOf(id)
  if (i === -1) filters.value.moods.push(id)
  else filters.value.moods.splice(i, 1)
}
function togglePlayMode(key) {
  const i = filters.value.playModes.indexOf(key)
  if (i === -1) filters.value.playModes.push(key)
  else filters.value.playModes.splice(i, 1)
}

// 선택된 버킷 key → 실제 platform_name 배열로 변환
function resolvePlatformNames() {
  const map = Object.fromEntries(platformBuckets.value.map(b => [b.key, b.names]))
  return filters.value.platforms.flatMap(k => map[k] || [])
}

function handleSubmit() {
  emit('submit', {
    keyword: keyword.value,
    filters: {
      genres: [...filters.value.genres],
      platforms: resolvePlatformNames(),
      moods: [...filters.value.moods],
      playModes: [...filters.value.playModes],
      playtime: filters.value.playtime,
      price: filters.value.price,
      rating: filters.value.rating,
      onSale: filters.value.onSale,
    },
  })
}

function reset() {
  keyword.value = ''
  filters.value = {
    genres: [], platforms: [], moods: [], playModes: [], playtime: 'all',
    price: 'all', rating: 'all', onSale: false,
  }
  emit('reset')
}

function setKeyword(kw) {
  keyword.value = kw
}

defineExpose({ reset, setKeyword })

onMounted(async () => {
  try {
    const { data } = await gameAPI.filterOptions()
    options.value = data
  } catch (e) {
    console.error('필터 옵션 로드 실패:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.panel {
  background: #fff;
  border: 1.5px solid #e8e4d9;
  border-radius: 16px;
  padding: 28px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.panel.active {
  border-color: #1e3a5f;
  box-shadow: 0 0 0 3px rgba(30,58,95,0.07);
  cursor: default;
}
.panel-header h2 {
  font-size: 18px;
  font-weight: 800;
  color: #1a1510;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.icon { width: 16px; color: #1e3a5f; }
.desc { font-size: 13px; color: #9e9585; }

.search-wrap { position: relative; display: flex; align-items: center; }
.search-input {
  width: 100%;
  padding: 12px 44px 12px 16px;
  border: 1px solid #e8e4d9;
  border-radius: 10px;
  font-size: 14px;
  color: #1a1510;
  background: #fafaf8;
  outline: none;
  font-family: inherit;
  transition: border-color 0.15s;
}
.search-input:focus { border-color: #1e3a5f; background: #fff; }
.search-input::placeholder { color: #c8c2b4; }
.search-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  color: #9e9585;
  display: flex;
  align-items: center;
  padding: 0;
  transition: color 0.15s;
}
.search-btn:hover { color: #1e3a5f; }

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 600;
  color: #3d3529;
}
.filter-bar-left { display: flex; align-items: center; gap: 6px; }
.reset-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: #9e9585;
  cursor: pointer;
  font-family: inherit;
}
.reset-btn:hover { color: #1e3a5f; }

.opt-loading { font-size: 13px; color: #9e9585; padding: 8px 0; }

.frow {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.flabel {
  flex-shrink: 0;
  width: 52px;
  font-size: 13px;
  font-weight: 600;
  color: #6b6256;
  padding-top: 7px;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 12px;
  border: 1px solid #ddd8cc;
  border-radius: 999px;
  background: #fff;
  font-size: 13px;
  color: #3d3529;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.chip:hover { border-color: #1e3a5f; color: #1e3a5f; }
.chip.on {
  border-color: #1e3a5f;
  color: #fff;
  background: #1e3a5f;
}
.cnt {
  font-size: 11px;
  opacity: 0.7;
}
</style>
