<template>
  <section class="section-card">
    <div class="section-header">
      <h3 class="section-title">획득 메달</h3>
      <RouterLink to="/profile/medals" class="view-all">전체 보기 &rsaquo;</RouterLink>
    </div>

    <div class="scroll-wrapper">
      <div class="cards-track" ref="track" @scroll="onScroll">
        <MedalBadge
          v-for="medal in medals"
          :key="medal.id"
          :medal="medal"
        />
       
      </div>

      <button v-if="scrollPos > 0" class="scroll-btn scroll-btn-left" @click="scrollLeft">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M11.78 5.22a.75.75 0 0 1 0 1.06L8.06 10l3.72 3.72a.75.75 0 1 1-1.06 1.06l-4.25-4.25a.75.75 0 0 1 0-1.06l4.25-4.25a.75.75 0 0 1 1.06 0Z" clip-rule="evenodd"/>
        </svg>
      </button>
      <button v-if="!atEnd" class="scroll-btn scroll-btn-right" @click="scrollRight">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M8.22 5.22a.75.75 0 0 1 1.06 0l4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.75.75 0 0 1-1.06-1.06L11.94 10 8.22 6.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd"/>
        </svg>
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import MedalBadge from './MedalBadge.vue'

defineProps({
  medals: { type: Array, default: () => [] },
})

const track = ref(null)
const scrollPos = ref(0)
const atEnd = ref(true)

function onScroll() {
  const el = track.value
  if (!el) return
  scrollPos.value = el.scrollLeft
  atEnd.value = el.scrollLeft + el.clientWidth >= el.scrollWidth - 4
}

function scrollRight() {
  track.value?.scrollBy({ left: 800, behavior: 'smooth' })
}

function scrollLeft() {
  track.value?.scrollBy({ left: -800, behavior: 'smooth' })
}

onMounted(() => {
  nextTick(() => {
    const el = track.value
    if (!el) return
    atEnd.value = el.scrollWidth <= el.clientWidth + 4
  })
})
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
  margin-bottom: 20px;
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1510;
  margin: 0;
}
.view-all {
  font-size: 13px;
  color: #6b6256;
  text-decoration: none;
}
.view-all:hover {
  color: #c96012;
}

.scroll-wrapper {
  position: relative;
}

.cards-track {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  padding-bottom: 4px;
}
.cards-track::-webkit-scrollbar { display: none; }

.cards-track :deep(.medal-badge) {
  flex-shrink: 0;
  flex: none;
  width: 148px;
  scroll-snap-align: start;
}

.quest-card {
  flex-shrink: 0;
  width: 148px;
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 8px;
  border-radius: 12px;
  background: #fffbf0;
  border: 1.5px dashed #e0c97a;
  text-decoration: none;
  color: inherit;
  transition: background 0.15s, border-color 0.15s;
  cursor: pointer;
}
.quest-card:hover {
  background: #fff5d6;
  border-color: #c8a96a;
}

.quest-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #fef3cd;
  display: flex;
  align-items: center;
  justify-content: center;
}
.quest-icon svg {
  width: 32px;
  height: 32px;
}

.quest-name {
  font-size: 12px;
  font-weight: 600;
  color: #1a1510;
  text-align: center;
  margin: 0;
  line-height: 1.3;
}
.quest-sub {
  font-size: 12px;
  font-weight: 700;
  color: #b8922a;
  text-align: center;
  margin: 0;
  line-height: 1.3;
}

.scroll-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #fff;
  border: 1px solid #e8e4d9;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1a1510;
  transition: background 0.15s;
  z-index: 1;
}
.scroll-btn-left { left: -14px; }
.scroll-btn-right { right: -14px; }
.scroll-btn:hover { background: #f0ece3; }
.scroll-btn svg {
  width: 16px;
  height: 16px;
}
</style>
