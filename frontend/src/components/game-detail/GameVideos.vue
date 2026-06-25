<template>
  <section class="videos-section">
    <div class="section-header">
      <div class="header-left">
        <h2 class="section-title">트레일러 / 공략 영상</h2>
      </div>
    </div>

    <div v-if="videos.length" class="carousel">
      <div class="track" ref="trackEl">
        <a
          v-for="v in videos"
          :key="v.id"
          :href="v.video_url"
          target="_blank"
          rel="noopener"
          class="video-card"
        >
          <!-- 썸네일 -->
          <div class="thumb">
            <img v-if="v.thumbnail_url" :src="v.thumbnail_url" :alt="v.title" />
            <div v-else class="thumb-placeholder">
              <svg viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
                <rect width="120" height="80" fill="#e8e2d5"/>
                <line x1="0" y1="0" x2="120" y2="80" stroke="#c8c2b4" stroke-width="1"/>
                <line x1="120" y1="0" x2="0" y2="80" stroke="#c8c2b4" stroke-width="1"/>
              </svg>
            </div>
            <!-- 재생 버튼 오버레이 -->
            <div class="play-overlay">
              <div class="play-btn">
                <svg viewBox="0 0 24 24" fill="currentColor" width="20">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
            </div>
          </div>

          <!-- 메타 -->
          <div class="video-meta">
            <p class="video-title">{{ v.title }}</p>
            <p class="video-info">{{ videoInfo(v) }}</p>
          </div>
        </a>

      </div>

      <button class="arrow-right" @click="trackEl?.scrollBy({ left: 310, behavior: 'smooth' })" :class="{ hidden: !canRight }">
        <svg fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" width="14">
          <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>
        </svg>
      </button>
    </div>

    <p v-if="!videos.length" class="coming-soon">추후 업데이트 예정</p>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

defineProps({
  gameId: { type: [String, Number], default: null },
  videos: { type: Array, default: () => [] },
})

// 채널 · 조회수 · 날짜 중 있는 것만 표시 (YouTube 검색엔 조회수 없음)
function videoInfo(v) {
  return [v.channel, v.views ? `${v.views} 조회수` : '', v.uploaded_at]
    .filter(Boolean).join(' · ')
}

const trackEl = ref(null)
const canRight = ref(false)

function onScroll() {
  const el = trackEl.value
  if (!el) return
  canRight.value = el.scrollLeft + el.clientWidth < el.scrollWidth - 4
}

const ro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(() => nextTick(onScroll)) : null
onMounted(() => { nextTick(onScroll); if (ro && trackEl.value) ro.observe(trackEl.value) })
onBeforeUnmount(() => ro?.disconnect())
</script>

<style scoped>
.videos-section {
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 14px;
  padding: 28px 32px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 6px;
}
.header-left { display: flex; align-items: baseline; gap: 10px; }
.section-title { font-size: 18px; font-weight: 800; color: #1a1510; margin: 0; }
.game-id-label {
  font-size: 11px;
  font-weight: 600;
  color: #9e9585;
  background: #f0ece3;
  border-radius: 4px;
  padding: 2px 6px;
}
.section-sub { font-size: 13px; color: #9e9585; margin: 0 0 20px; }

/* 캐러셀 */
.carousel { position: relative; }
.track {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 4px;
  scroll-behavior: smooth;
}
.track::-webkit-scrollbar { display: none; }

/* 카드 */
.video-card {
  flex-shrink: 0;
  width: 280px;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.15s;
}
.video-card:hover { transform: translateY(-2px); }

.thumb {
  position: relative;
  aspect-ratio: 16/9;
  background: #e8e2d5;
  border-radius: 10px;
  overflow: hidden;
}
.thumb img { width: 100%; height: 100%; object-fit: cover; }
.thumb-placeholder {
  width: 100%; height: 100%;
}
.thumb-placeholder svg { width: 100%; height: 100%; display: block; }

.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.15);
  transition: background 0.15s;
}
.video-card:hover .play-overlay { background: rgba(0,0,0,0.3); }
.play-btn {
  width: 44px; height: 44px;
  background: rgba(255,255,255,0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1a1510;
  padding-left: 3px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.video-meta { padding: 0 2px; }
.video-title {
  font-size: 13px;
  font-weight: 600;
  color: #1a1510;
  margin: 0 0 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.video-info { font-size: 11px; color: #9e9585; margin: 0; }

/* 오른쪽 화살표 */
.arrow-right {
  position: absolute;
  top: 50%;
  right: -14px;
  transform: translateY(-60%);
  width: 32px; height: 32px;
  background: #fff;
  border: 1.5px solid #ddd8cc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #3d3529;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.15s;
  z-index: 2;
}
.arrow-right:hover { border-color: #1e3a5f; color: #1e3a5f; }
.arrow-right.hidden { opacity: 0; pointer-events: none; }

/* 스켈레톤 */
.thumb-placeholder-skeleton {
  background: linear-gradient(90deg, #f0ece3 25%, #e8e2d5 50%, #f0ece3 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
.sk-line {
  height: 11px;
  background: linear-gradient(90deg, #f0ece3 25%, #e8e2d5 50%, #f0ece3 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 999px;
  margin-bottom: 6px;
}
.w80 { width: 80%; }
.w50 { width: 50%; }
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.coming-soon {
  font-size: 13px;
  color: #9e9585;
  font-style: italic;
  margin: 18px 0 0;
}
</style>