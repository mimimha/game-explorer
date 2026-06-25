<template>
  <div class="gallery">
    <!-- 메인 이미지 -->
    <div class="main-image">
      <img v-if="activeItem.url" :src="activeItem.url" :alt="activeItem.label" />
      <div v-else class="img-placeholder">
        <svg viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg" width="120">
          <rect width="120" height="80" fill="#e8e2d5"/>
          <line x1="0" y1="0" x2="120" y2="80" stroke="#c8c2b4" stroke-width="1"/>
          <line x1="120" y1="0" x2="0" y2="80" stroke="#c8c2b4" stroke-width="1"/>
        </svg>
        <span>{{ capsuleUrl ? '' : 'GAME.capsule_url 대표 이미지' }}</span>
      </div>
    </div>

    <!-- 썸네일 트랙 -->
    <div v-if="screenshots.length" class="thumb-row">
      <button class="arrow" @click="scrollTrack(-1)" :class="{ hidden: !canLeft }">
        <svg fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" width="13">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5"/>
        </svg>
      </button>

      <div class="track" ref="trackEl">
        <button
          v-for="(item, idx) in allItems"
          :key="item.id"
          class="thumb"
          :class="{ active: activeIdx === idx }"
          @click="activeIdx = idx"
        >
          <img v-if="item.url" :src="item.url" :alt="item.label" />
          <div v-else class="thumb-placeholder">
            <svg viewBox="0 0 60 45" xmlns="http://www.w3.org/2000/svg">
              <rect width="60" height="45" fill="#e8e2d5"/>
              <line x1="0" y1="0" x2="60" y2="45" stroke="#c8c2b4" stroke-width="1"/>
              <line x1="60" y1="0" x2="0" y2="45" stroke="#c8c2b4" stroke-width="1"/>
            </svg>
          </div>
          <span class="thumb-label">{{ item.label }}</span>
        </button>
      </div>

      <button class="arrow" @click="scrollTrack(1)" :class="{ hidden: !canRight }">
        <svg fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" width="13">
          <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>
        </svg>
      </button>
    </div>
    <p v-else class="coming-soon">추후 업데이트 예정</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  capsuleUrl:  { type: String, default: '' },
  screenshots: { type: Array,  default: () => [] },
})

const activeIdx = ref(0)
const trackEl = ref(null)
const canLeft = ref(false)
const canRight = ref(false)

// 대표 이미지 + 스크린샷 합치기
const allItems = computed(() => {
  const base = [{ id: 'main', url: props.capsuleUrl, label: '대표' }]
  return [...base, ...props.screenshots.filter(s => s.id !== 'main')]
})

const activeItem = computed(() => allItems.value[activeIdx.value] || {})

function scrollTrack(dir) {
  trackEl.value?.scrollBy({ left: dir * 110, behavior: 'smooth' })
}
function onScroll() {
  const el = trackEl.value
  if (!el) return
  canLeft.value  = el.scrollLeft > 4
  canRight.value = el.scrollLeft + el.clientWidth < el.scrollWidth - 4
}

const ro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(() => nextTick(onScroll)) : null
onMounted(() => {
  nextTick(onScroll)
  if (ro && trackEl.value) ro.observe(trackEl.value)
})
onBeforeUnmount(() => ro?.disconnect())
</script>

<style scoped>
.gallery {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 메인 이미지 */
.main-image {
  width: 100%;
  aspect-ratio: 16/10;
  border-radius: 12px;
  overflow: hidden;
  background: #e8e2d5;
  border: 1px solid #ddd8cc;
}
.main-image img { width: 100%; height: 100%; object-fit: cover; }
.img-placeholder {
  width: 100%; height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #9e9585;
  font-size: 12px;
}

/* 썸네일 행 */
.thumb-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.arrow {
  width: 28px; height: 28px;
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #ddd8cc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #3d3529;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  transition: all 0.15s;
}
.arrow:hover { border-color: #1e3a5f; color: #1e3a5f; }
.arrow.hidden { opacity: 0; pointer-events: none; }

.track {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  flex: 1;
  padding: 2px 0 4px;
  scroll-behavior: smooth;
}
.track::-webkit-scrollbar { display: none; }

.thumb {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  flex-shrink: 0;
  width: 96px;
  background: none;
  border: 2px solid transparent;
  border-radius: 8px;
  padding: 2px;
  cursor: pointer;
  transition: border-color 0.15s;
}
.thumb.active { border-color: #1e3a5f; }
.thumb:hover:not(.active) { border-color: #c8c2b4; }

.thumb img,
.thumb-placeholder {
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 6px;
  object-fit: cover;
  overflow: hidden;
}
.thumb-placeholder svg { width: 100%; height: 100%; display: block; }

.thumb-label {
  font-size: 10px;
  color: #9e9585;
  white-space: nowrap;
}
.thumb.active .thumb-label { color: #1e3a5f; font-weight: 600; }

.coming-soon {
  font-size: 13px;
  color: #9e9585;
  font-style: italic;
  margin: 4px 0 0;
}
</style>