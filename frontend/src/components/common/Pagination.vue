<template>
  <nav v-if="totalPages > 1" class="pagination">
    <button class="pg-btn" :disabled="currentPage === 1" @click="jump(-window)" aria-label="이전 묶음">«</button>
    <button class="pg-btn" :disabled="currentPage === 1" @click="go(currentPage - 1)" aria-label="이전">‹</button>
    <button
      v-for="p in pages"
      :key="p"
      class="pg-btn num"
      :class="{ active: p === currentPage }"
      @click="go(p)"
    >{{ p }}</button>
    <button class="pg-btn" :disabled="currentPage === totalPages" @click="go(currentPage + 1)" aria-label="다음">›</button>
    <button class="pg-btn" :disabled="currentPage === totalPages" @click="jump(window)" aria-label="다음 묶음">»</button>
  </nav>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, default: 1 },
  totalPages:  { type: Number, default: 1 },
  window:      { type: Number, default: 5 },   // 한 번에 보일 페이지 번호 수
})
const emit = defineEmits(['change'])

// 현재 페이지 주변으로 window 개의 번호만 노출
const pages = computed(() => {
  const total = props.totalPages
  const w = props.window
  let start = Math.max(1, props.currentPage - Math.floor(w / 2))
  let end = Math.min(total, start + w - 1)
  start = Math.max(1, end - w + 1)
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

function go(p) {
  if (p >= 1 && p <= props.totalPages && p !== props.currentPage) emit('change', p)
}

// 묶음 단위 이동(« »): window 만큼 점프, 범위 밖이면 양끝으로 클램프
function jump(delta) {
  go(Math.min(props.totalPages, Math.max(1, props.currentPage + delta)))
}
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: 28px;
}
.pg-btn {
  min-width: 34px;
  height: 34px;
  padding: 0 8px;
  border: 1px solid #e8e4d9;
  border-radius: 8px;
  background: #fff;
  color: #3d3529;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.pg-btn:hover:not(:disabled) { border-color: #1e3a5f; color: #1e3a5f; }
.pg-btn.active {
  background: #1e3a5f;
  border-color: #1e3a5f;
  color: #fff;
  font-weight: 700;
}
.pg-btn:disabled { opacity: 0.4; cursor: default; }
</style>
