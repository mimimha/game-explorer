<template>
  <section class="section-card">
    <div class="section-header">
      <h3 class="section-title">AI 추천 기록</h3>
    </div>

    <div v-if="!logs.length" class="empty">
      아직 AI 추천 기록이 없어요.
    </div>

    <div v-else class="carousel">
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

      <div class="track" ref="trackEl" @scroll="onScroll">
        <div v-for="log in logs" :key="log.log_id" class="item-wrap">
          <RouterLink :to="`/explore?log=${log.log_id}`" class="item">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="16" class="clock-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
            </svg>
            <div class="item-text">
              <span class="query">"{{ log.prompt_input }}"</span>
              <span class="meta">{{ formatDate(log.created_at) }} · 결과 {{ log.result_count ?? 0 }}개</span>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" width="14" class="chevron">
              <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>
            </svg>
          </RouterLink>
          <button class="delete-btn" @click="$emit('delete', log.log_id)" aria-label="삭제">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" width="10" height="10">
              <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"/>
            </svg>
          </button>
        </div>
      </div>

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
  logs: { type: Array, default: () => [] },
})

const emit = defineEmits(['delete'])

const trackEl = ref(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)
const SCROLL_AMOUNT = 248

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

watch(() => props.logs.length, checkScroll)
onMounted(checkScroll)

const ro = typeof ResizeObserver !== 'undefined'
  ? new ResizeObserver(checkScroll)
  : null

onMounted(() => { if (ro && trackEl.value) ro.observe(trackEl.value) })
onBeforeUnmount(() => ro?.disconnect())

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('ko-KR').replace(/\. /g, '.').slice(0, -1)
}
</script>

<style scoped>
.section-card {
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 16px;
  padding: 24px 28px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1510;
  margin: 0;
}

.empty {
  font-size: 14px;
  color: #9e9585;
  text-align: center;
  padding: 24px 0;
}

.carousel {
  position: relative;
}

.track {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  scroll-behavior: smooth;
  padding: 4px 2px 8px;
}
.track::-webkit-scrollbar { display: none; }

.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-60%);
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

.item-wrap {
  position: relative;
  flex-shrink: 0;
}

.delete-btn {
  position: absolute;
  top: -7px;
  right: -7px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #e53e3e;
  border: 2px solid #fff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  transition: background 0.15s;
  z-index: 1;
}
.delete-btn:hover { background: #c53030; }

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
  width: 220px;
  transition: border-color 0.15s, box-shadow 0.15s;
  text-decoration: none;
  color: inherit;
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
