<template>
  <section v-if="history.length" class="history">
    <div class="row">
      <div class="left">
        <h3 class="title">AI 최근 추천 기록</h3>
        <span class="sub">이전에 추천받은 내용을 다시 확인해보세요.</span>
      </div>
      <RouterLink to="/history" class="more">전체 보기 ›</RouterLink>
    </div>

    <!-- 캐러셀 래퍼 -->
    <div class="carousel">
      <!-- 왼쪽 화살표 -->
      <button
        class="arrow arrow-left"
        :class="{ hidden: !canScrollLeft }"
        @click="scroll(-1)"
        aria-label="이전"
      >
        <svg fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" width="14">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5"/>
        </svg>
      </button>

      <!-- 아이템 트랙 -->
      <div class="track" ref="trackEl" @scroll="onScroll">
        <button
          v-for="h in history"
          :key="h.id"
          class="item"
          @click="$emit('restore', h)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="16" class="clock-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
          </svg>
          <div class="item-text">
            <span class="query">"{{ h.query }}"</span>
            <span class="meta">{{ h.date }} · 결과 {{ h.count }}개</span>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" width="14" class="chevron">
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>
          </svg>
        </button>
      </div>

      <!-- 오른쪽 화살표 -->
      <button
        class="arrow arrow-right"
        :class="{ hidden: !canScrollRight }"
        @click="scroll(1)"
        aria-label="다음"
      >
        <svg fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" width="14">
          <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>
        </svg>
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  history: { type: Array, default: () => [] },
})
defineEmits(['restore'])

const trackEl = ref(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)

const SCROLL_AMOUNT = 248 // 카드 너비(220) + gap(12) + 여유

function scroll(dir) {
  trackEl.value?.scrollBy({ left: dir * SCROLL_AMOUNT, behavior: 'smooth' })
}

function onScroll() {
  const el = trackEl.value
  if (!el) return
  canScrollLeft.value = el.scrollLeft > 4
  canScrollRight.value = el.scrollLeft + el.clientWidth < el.scrollWidth - 4
}

function checkScroll() {
  nextTick(() => onScroll())
}

watch(() => props.history.length, checkScroll)
onMounted(checkScroll)

// 리사이즈 대응
const ro = typeof ResizeObserver !== 'undefined'
  ? new ResizeObserver(checkScroll)
  : null

onMounted(() => { if (ro && trackEl.value) ro.observe(trackEl.value) })
onBeforeUnmount(() => ro?.disconnect())
</script>

<style scoped>
.history { margin-bottom: 48px; }

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.left { display: flex; align-items: baseline; gap: 10px; }
.title { font-size: 18px; font-weight: 800; color: #1a1510; }
.sub { font-size: 13px; color: #9e9585; }
.more { font-size: 13px; font-weight: 600; color: #1e3a5f; text-decoration: none; }
.more:hover { opacity: 0.7; }

/* 캐러셀 컨테이너 — 화살표를 track 위에 float */
.carousel {
  position: relative;
}

/* 아이템 트랙 */
.track {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  scroll-behavior: smooth;
  padding: 4px 2px 8px;   /* 상하 여백으로 카드 shadow가 잘리지 않게 */
}
.track::-webkit-scrollbar { display: none; }

/* 화살표 공통 */
.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-60%);   /* 카드 중앙 정렬 (패딩 보정) */
  z-index: 10;
  width: 34px;
  height: 34px;
  background: #fff;
  border: 1.5px solid #ddd8cc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #3d3529;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
  transition: opacity 0.2s, border-color 0.15s, color 0.15s, box-shadow 0.15s;
}
.arrow:hover {
  border-color: #1e3a5f;
  color: #1e3a5f;
  box-shadow: 0 4px 14px rgba(30,58,95,0.14);
}
.arrow.hidden {
  opacity: 0;
  pointer-events: none;
}

.arrow-left  { left: -16px; }
.arrow-right { right: -16px; }

/* 카드 */
.item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 12px;
  padding: 14px 16px;
  cursor: pointer;
  text-align: left;
  flex-shrink: 0;
  width: 220px;
  transition: border-color 0.15s, box-shadow 0.15s;
  font-family: inherit;
}
.item:hover {
  border-color: #1e3a5f;
  box-shadow: 0 4px 12px rgba(30,58,95,0.08);
}
.clock-icon { color: #9e9585; flex-shrink: 0; }
.item-text { flex: 1; display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.query {
  font-size: 13px;
  font-weight: 600;
  color: #1a1510;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.meta { font-size: 11px; color: #9e9585; white-space: nowrap; }
.chevron { color: #c8c2b4; flex-shrink: 0; }
</style>