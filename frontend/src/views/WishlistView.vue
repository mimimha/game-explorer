<template>
  <main class="wishlist-page">
    <div class="inner">
      <div class="page-header">
        <RouterLink to="/profile" class="back-link">← 프로필로 돌아가기</RouterLink>
        <h1 class="page-title">찜한 게임</h1>
        <p class="page-sub">총 {{ games.length }}개</p>
      </div>

      <div v-if="loading" class="loading-wrap">
        <div class="dots-state">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>

      <div v-else-if="games.length === 0" class="empty">
        <p>아직 찜한 게임이 없어요.</p>
        <RouterLink to="/explore" class="explore-link">게임 둘러보기</RouterLink>
      </div>

      <div v-else class="grid">
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
            <div class="genre-tags">
              <span v-for="g in (game.genres || []).slice(0, 2)" :key="g.id" class="tag">{{ g.name }}</span>
            </div>
            <p class="card-date">{{ formatDate(game.wishlisted_at) }} 찜</p>
          </div>
        </RouterLink>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { wishlistAPI } from '@/api/services'

const loading = ref(true)
const games = ref([])

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\. /g, '.').replace(/\.$/, '')
}

onMounted(async () => {
  try {
    const { data } = await wishlistAPI.list()
    games.value = data.results ?? data
  } catch (e) {
    console.error('찜 목록 로드 실패:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.wishlist-page {
  background: #fafaf8;
  min-height: 100vh;
  padding: 24px 0 80px;
}
.inner {
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 40px;
}

.page-header {
  margin-bottom: 32px;
}
.back-link {
  font-size: 13px;
  color: #6b6256;
  text-decoration: none;
  display: inline-block;
  margin-bottom: 12px;
}
.back-link:hover { color: #1e3a5f; }
.page-title {
  font-size: 28px;
  font-weight: 800;
  color: #1a1510;
  margin: 0 0 4px;
  letter-spacing: -0.02em;
}
.page-sub {
  font-size: 14px;
  color: #9e9585;
  margin: 0;
}

.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 120px 0;
}
.dots-state {
  display: flex;
  align-items: center;
  gap: 10px;
}
.dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  background: #1e3a5f;
  opacity: 0;
  animation: dot-pop 1.2s ease-in-out infinite;
}
.dot:nth-child(1) { animation-delay: 0s; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes dot-pop {
  0%, 80%, 100% { opacity: 0; transform: scale(0.6); }
  40%           { opacity: 1; transform: scale(1); }
}

.empty {
  text-align: center;
  padding: 80px 0;
}
.empty p {
  font-size: 16px;
  color: #9e9585;
  margin: 0 0 16px;
}
.explore-link {
  display: inline-block;
  padding: 10px 24px;
  background: #1e3a5f;
  color: white;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s;
}
.explore-link:hover { background: #162d4a; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.game-card {
  text-decoration: none;
  color: inherit;
  border: 1px solid #e8e4d9;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  transition: transform 0.15s, box-shadow 0.15s;
}
.game-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(30, 58, 95, 0.1);
}

.card-thumb {
  aspect-ratio: 4/3;
  overflow: hidden;
  background: #f0ece3;
}
.card-thumb img {
  width: 100%; height: 100%;
  object-fit: cover;
}
.thumb-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
}
.thumb-placeholder svg { width: 100%; height: 100%; }

.card-body {
  padding: 12px 14px 14px;
}
.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1510;
  margin: 0 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
}
.tag {
  font-size: 11px;
  color: #6b6256;
  background: #f0ece3;
  border-radius: 999px;
  padding: 2px 8px;
}
.card-date {
  font-size: 11px;
  color: #9e9585;
  margin: 0;
}
</style>
