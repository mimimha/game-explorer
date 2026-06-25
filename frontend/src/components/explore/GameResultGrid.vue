<template>
  <section class="result">
    <!-- 헤더 -->
    <div class="row">
      <div class="left">
        <h3 class="title">{{ sectionTitle }}</h3>
        <span class="sub">{{ subtitle }}</span>
      </div>
      <div class="right">
        <template v-if="type === 'search'">
          <select :value="sort" @change="$emit('update:sort', $event.target.value)" class="sort-select">
            <option value="discount">정렬: 할인순</option>
            <option value="recent">정렬: 최신순</option>
            <option value="rating">정렬: 평점순</option>
            <option value="price">정렬: 가격순</option>
          </select>
        </template>
        <RouterLink v-else to="/explore" class="more-link">전체 보기 ›</RouterLink>
      </div>
    </div>

    <!-- 1. 제출 전 안내 -->
    <EmptyState
      v-if="!submitted && !loading && !restoreLoading"
      :icon="type === 'ai' ? 'sparkle' : 'search'"
      :message="type === 'ai'
        ? '원하는 게임을 위에서 설명하고 <strong>추천받기</strong> 버튼을 눌러보세요.'
        : '키워드나 필터로 게임을 검색해보세요.'"
    />

    <!-- 2. 히스토리 복원 로딩 — 점 세 개 애니메이션 -->
    <div v-else-if="restoreLoading" class="dots-state">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>

    <!-- 3. 일반 로딩 — 스켈레톤 -->
    <div v-else-if="loading" class="grid">
      <div v-for="i in 5" :key="i" class="skeleton-card">
        <div class="sk-thumb"></div>
        <div class="sk-line w70"></div>
        <div class="sk-line w50"></div>
        <div class="sk-line w30"></div>
      </div>
    </div>

    <!-- 4. 결과 없음 -->
    <EmptyState
      v-else-if="games.length === 0"
      icon="search"
      message="<strong>검색하신 목록이 없습니다.</strong><br />다른 키워드나 필터로 변경해보세요!"
      :show-reset="true"
      @reset="$emit('reset')"
    />

    <!-- 5. AI 추천 결과 — 캐러셀 -->
    <div v-else-if="type === 'ai'" class="carousel-wrap">
      <button class="carousel-btn" @click="scroll(-1)">
        <svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" width="14">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5"/>
        </svg>
      </button>
      <div class="grid" ref="carouselEl">
        <GameCard v-for="g in games" :key="g.id" :game="g" />
      </div>
      <button class="carousel-btn" @click="scroll(1)">
        <svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" width="14">
          <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>
        </svg>
      </button>
    </div>

    <!-- 6. 검색 결과 — 그리드 -->
    <div v-else class="grid">
      <GameCard v-for="g in games" :key="g.id" :game="g" />
    </div>

    <!-- 7. 페이지네이션 -->
    <div v-if="type === 'search' && totalPages > 1" class="pagination">
      <button class="pg-btn" :disabled="currentPage === 1" @click="$emit('update:page', currentPage - 1)">
        <svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" width="14">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5"/>
        </svg>
      </button>
      <button
        v-for="p in pageNumbers"
        :key="p"
        class="pg-num"
        :class="{ active: p === currentPage, ellipsis: p === '…' }"
        :disabled="p === '…'"
        @click="p !== '…' && $emit('update:page', p)"
      >{{ p }}</button>
      <button class="pg-btn" :disabled="currentPage === totalPages" @click="$emit('update:page', currentPage + 1)">
        <svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" width="14">
          <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>
        </svg>
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import GameCard from '../home/GameCard.vue'
import EmptyState from './EmptyState.vue'

const props = defineProps({
  type:           { type: String,  default: 'ai' },
  games:          { type: Array,   default: () => [] },
  loading:        { type: Boolean, default: false },
  restoreLoading: { type: Boolean, default: false },
  submitted:      { type: Boolean, default: false },
  sort:           { type: String,  default: 'recent' },
  totalCount:     { type: Number,  default: 0 },
  currentPage:    { type: Number,  default: 1 },
  totalPages:     { type: Number,  default: 1 },
})
defineEmits(['reset', 'update:sort', 'update:page'])

const viewMode = ref('grid')
const carouselEl = ref(null)

const sectionTitle = computed(() => props.type === 'ai' ? '추천 결과' : '검색 결과')
const subtitle = computed(() => {
  if (props.restoreLoading || props.loading) return ''
  if (props.type === 'ai') return 'AI 추천 결과입니다.'
  if (!props.submitted || props.totalCount === 0) return ''
  return `총 ${props.totalCount.toLocaleString()}개의 게임`
})

// 페이지 번호 목록 (앞뒤 2개 + 말줄임표)
const pageNumbers = computed(() => {
  const total = props.totalPages
  const cur = props.currentPage
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const pages = new Set([1, total, cur - 1, cur, cur + 1].filter(p => p >= 1 && p <= total))
  const sorted = [...pages].sort((a, b) => a - b)
  const result = []
  for (let i = 0; i < sorted.length; i++) {
    if (i > 0 && sorted[i] - sorted[i - 1] > 1) result.push('…')
    result.push(sorted[i])
  }
  return result
})

function scroll(dir) {
  carouselEl.value?.scrollBy({ left: dir * 220, behavior: 'smooth' })
}
</script>

<style scoped>
.result { margin-bottom: 48px; }

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.left { display: flex; align-items: baseline; gap: 10px; }
.title { font-size: 18px; font-weight: 800; color: #1a1510; }
.sub { font-size: 13px; color: #9e9585; min-height: 18px; }
.right { display: flex; align-items: center; gap: 8px; }
.more-link { font-size: 13px; font-weight: 600; color: #1e3a5f; text-decoration: none; }
.more-link:hover { opacity: 0.7; }

.sort-select {
  padding: 6px 12px;
  border: 1px solid #e8e4d9;
  border-radius: 8px;
  font-size: 13px;
  color: #3d3529;
  background: #fff;
  outline: none;
  cursor: pointer;
  font-family: inherit;
}
.view-btn {
  width: 32px; height: 32px;
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #9e9585;
  transition: all 0.15s;
}
.view-btn.active, .view-btn:hover { border-color: #1e3a5f; color: #1e3a5f; }

/* ── 점 세 개 로딩 ── */
.dots-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 56px 0;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #1e3a5f;
  opacity: 0;
  animation: dot-pop 1.2s ease-in-out infinite;
}
.dot:nth-child(1) { animation-delay: 0s; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-pop {
  0%, 80%, 100% { opacity: 0;   transform: scale(0.6); }
  40%           { opacity: 1;   transform: scale(1); }
}

/* 캐러셀 */
.carousel-wrap { display: flex; align-items: center; gap: 8px; }
.carousel-btn {
  width: 36px; height: 36px;
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #3d3529;
  transition: all 0.15s;
}
.carousel-btn:hover { border-color: #1e3a5f; color: #1e3a5f; }

/* 그리드 */
.grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
  flex: 1;
  overflow: hidden;
}

/* 스켈레톤 */
.skeleton-card { background: #fff; border-radius: 12px; overflow: hidden; border: 1px solid #e8e4d9; }
.sk-thumb {
  aspect-ratio: 4/3;
  background: linear-gradient(90deg, #f0ece3 25%, #e8e2d5 50%, #f0ece3 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
.sk-line {
  height: 11px;
  margin: 10px 12px 0;
  background: linear-gradient(90deg, #f0ece3 25%, #e8e2d5 50%, #f0ece3 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 999px;
}
.sk-line:last-child { margin-bottom: 12px; }
.w70 { width: 70%; }
.w50 { width: 50%; }
.w30 { width: 30%; }
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 페이지네이션 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-top: 28px;
}
.pg-btn, .pg-num {
  min-width: 34px;
  height: 34px;
  padding: 0 6px;
  border: 1px solid #e8e4d9;
  border-radius: 8px;
  background: #fff;
  font-size: 13px;
  color: #3d3529;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: inherit;
  transition: all 0.15s;
}
.pg-btn:hover:not(:disabled), .pg-num:hover:not(:disabled):not(.ellipsis) {
  border-color: #1e3a5f;
  color: #1e3a5f;
}
.pg-btn:disabled { opacity: 0.35; cursor: default; }
.pg-num.active {
  background: #1e3a5f;
  border-color: #1e3a5f;
  color: #fff;
  font-weight: 700;
}
.pg-num.ellipsis { border-color: transparent; background: none; cursor: default; color: #9e9585; }
</style>