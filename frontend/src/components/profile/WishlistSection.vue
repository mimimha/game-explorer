<template>
  <section class="section-card">
    <div class="section-header">
      <h3 class="section-title">찜한 게임</h3>
      <RouterLink to="/wishlist" class="view-all">전체 보기 &rsaquo;</RouterLink>
    </div>

    <div v-if="games.length === 0" class="empty">
      아직 찜한 게임이 없어요.
    </div>

    <div v-else class="scroll-wrapper">
      <div class="cards-track" ref="track" @scroll="onScroll">
        <RouterLink
          v-for="game in games"
          :key="game.id"
          :to="`/games/${game.id}`"
          class="game-card"
        >
          <div class="card-thumb">
            <img v-if="game.capsule_url" :src="game.capsule_url" :alt="game.title" />
            <div v-else class="thumb-placeholder">
              <svg viewBox="0 0 80 60" xmlns="http://www.w3.org/2000/svg">
                <rect width="80" height="60" fill="#e8e2d5"/>
                <line x1="0" y1="0" x2="80" y2="60" stroke="#c8c2b4" stroke-width="1"/>
                <line x1="80" y1="0" x2="0" y2="60" stroke="#c8c2b4" stroke-width="1"/>
              </svg>
            </div>
          </div>
          <div class="card-body">
            <p class="card-title">{{ game.title }}</p>
            <p class="card-date">{{ formatDate(game.wishlisted_at) }} 찜</p>
          </div>
        </RouterLink>
      </div>

      <button v-if="games.length > 3 && scrollPos > 0" class="scroll-btn scroll-btn-left" @click="scrollLeft">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M11.78 5.22a.75.75 0 0 1 0 1.06L8.06 10l3.72 3.72a.75.75 0 1 1-1.06 1.06l-4.25-4.25a.75.75 0 0 1 0-1.06l4.25-4.25a.75.75 0 0 1 1.06 0Z" clip-rule="evenodd"/>
        </svg>
      </button>
      <button v-if="games.length > 3 && !atEnd" class="scroll-btn scroll-btn-right" @click="scrollRight">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M8.22 5.22a.75.75 0 0 1 1.06 0l4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.75.75 0 0 1-1.06-1.06L11.94 10 8.22 6.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd"/>
        </svg>
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

defineProps({
  games: { type: Array, default: () => [] },
})

const track = ref(null)
const scrollPos = ref(0)
const atEnd = ref(false)

function onScroll() {
  const el = track.value
  if (!el) return
  scrollPos.value = el.scrollLeft
  atEnd.value = el.scrollLeft + el.clientWidth >= el.scrollWidth - 4
}

function scrollRight() {
  track.value?.scrollBy({ left: 200, behavior: 'smooth' })
}

function scrollLeft() {
  track.value?.scrollBy({ left: -200, behavior: 'smooth' })
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\. /g, '.').replace(/\.$/, '')
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
.view-all {
  font-size: 13px;
  color: #6b6256;
  text-decoration: none;
}
.view-all:hover { color: #1e3a5f; }

.empty {
  font-size: 14px;
  color: #9e9585;
  text-align: center;
  padding: 24px 0;
}

.scroll-wrapper {
  position: relative;
}
.cards-track {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  padding-bottom: 4px;
}
.cards-track::-webkit-scrollbar { display: none; }

.game-card {
  flex-shrink: 0;
  width: 160px;
  scroll-snap-align: start;
  text-decoration: none;
  color: inherit;
  border: 1px solid #e8e4d9;
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.15s, box-shadow 0.15s;
}
.game-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(30, 58, 95, 0.1);
}

.card-thumb {
  aspect-ratio: 4/3;
  overflow: hidden;
  background: #f0ece3;
}
.card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.thumb-placeholder svg {
  width: 100%;
  height: 100%;
}

.card-body {
  padding: 10px 12px;
}
.card-title {
  font-size: 13px;
  font-weight: 600;
  color: #1a1510;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-date {
  font-size: 11px;
  color: #9e9585;
  margin: 0;
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
