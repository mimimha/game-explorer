<template>
  <section class="section">
    <SectionHeader
      :num="num"
      :title="title"
      :subtitle="subtitle"
      :more-to="moreTo"
      :show-arrows="showArrows"
    />

    <!-- 로딩 스켈레톤 -->
    <div v-if="loading" class="card-grid">
      <div v-for="i in 5" :key="i" class="skeleton-card">
        <div class="skeleton-thumb"></div>
        <div class="skeleton-line w80"></div>
        <div class="skeleton-line w50"></div>
      </div>
    </div>

    <!-- 취향 분석 섹션 -->
    <div v-else-if="type === 'recommendation'" class="card-grid">
      <div v-if="!authStore.isLoggedIn" class="login-nudge-card">
        <div class="nudge-thumb">
          <img :src="cardOneImg" alt="1번 카드" class="nudge-card-img" />
          <div class="nudge-overlay">
            <p class="nudge-sub">로그인 하고</p>
            <p class="nudge-main">나만의 게임 취향을</p>
            <p class="nudge-sub">분석 받아보세요.</p>
          </div>
        </div>
      </div>

      <div
        v-for="(game, index) in games.slice(0, authStore.isLoggedIn ? 5 : 4)"
        :key="game.id || index"
        class="today-wrap"
      >
  
        <GameCard :game="game" :show-wishlist="true" />
      </div>
    </div>

    <!-- 할인 / 최신 섹션: 배너 + 2열 리스트 -->
    <div v-else class="banner-grid">
      <!-- 왼쪽 배너 -->
      <div class="banner-left" :class="{ 'banner-left--img': type === 'discount' || type === 'new' }">
        <!-- 할인: 전체 이미지 -->
        <img v-if="type === 'discount'" :src="card2Img" alt="할인 배너" class="banner-bg-img" />

        <!-- 신작: 전체 이미지 -->
        <img v-else-if="type === 'new'" :src="card3Img" alt="신작 배너" class="banner-bg-img" />

        <!-- 그 외: 키아트 플레이스홀더 -->
        <div v-else class="banner-image">
          <span class="banner-placeholder">신작 스포트라이트 / 키아트</span>
        </div>

        <div class="banner-bottom">
          <h3 class="banner-title">
            {{ type === 'discount' ? '이번 주 할인 모음' : '이번 주 신작' }}
          </h3>
          <RouterLink
            :to="type === 'discount' ? '/explore?filter=sale' : '/explore?filter=new'"
            class="banner-more-btn"
          >
            더 보기
          </RouterLink>
        </div>
      </div>

      <!-- 오른쪽 2열 3행 리스트 -->
      <div class="banner-right">
        <GameCardRow
          v-for="(game, i) in (games.length ? games.slice(0, 6) : Array(6).fill({}))"
          :key="i"
          :game="game"
          :show-price="type === 'discount'"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import GameCard from './GameCard.vue'
import GameCardRow from './GameCardRow.vue'
import SectionHeader from './SectionHeader.vue'
import { useAuthStore } from '@/stores/auth'
import { fetchGames } from '@/services/api'
import cardOneImg from '@/assets/1번 카드.png'
import card2Img from '@/assets/2번 카드.png'
import card3Img from '@/assets/3번 카드.png'

const props = defineProps({
  num: { type: Number, required: true },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  type: { type: String, default: 'new' },
  moreTo: { type: String, default: '' },
  showArrows: { type: Boolean, default: false }
})

const authStore = useAuthStore()
const games = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    games.value = await fetchGames(props.type)
  } catch (e) {
    console.error('게임 목록 로드 실패:', e)
  } finally {
    loading.value = false
  }
})

</script>

<style scoped>
.section {
  margin-bottom: 56px;
}

/* 취향 분석 그리드 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.today-wrap {
  position: relative;
  min-width: 0;
}
.login-nudge-card {
  min-width: 0;
}
/* 로그인 유도 카드 */
.login-nudge-card {
  min-width: 0;
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.nudge-thumb {
  position: relative;
  flex: 1;
  overflow: hidden;
}
.nudge-card-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.nudge-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 20px;
  text-align: center;
}
.nudge-sub {
  font-family: 'Jua', sans-serif;
  font-size: 15px;
  color: #3d2b1f;
  margin: 0;
  line-height: 1.3;
}
.nudge-main {
  font-family: 'Jua', sans-serif;
  font-size: 22px;
  color: #3d2b1f;
  margin: 2px 0;
  line-height: 1.3;
}
/* 배너 그리드 (할인/최신) */
.banner-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
}

.banner-left {
  position: relative;
  height: 340px;
  background: #f0ece3;
  border: 1px solid #e8e4d9;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-sizing: border-box;
  overflow: hidden;
}
.banner-left--img {
  padding: 0;
  border: none;
  background: none;
}
.banner-bg-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
  z-index: 0;
}
.banner-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px 20px;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: linear-gradient(to top, rgba(0,0,0,0.55) 0%, transparent 100%);
}
.banner-left:not(.banner-left--img) .banner-bottom {
  position: static;
  background: none;
  padding: 0;
  gap: 12px;
}
.banner-image {
  flex: 1;
  min-height: 0;
  background: #e0dbd0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.banner-placeholder {
  font-size: 12px;
  color: #9e9585;
}
.banner-left--img .banner-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1510;
}
.banner-left:not(.banner-left--img) .banner-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1510;
}
.banner-left--img .banner-more-btn {
  display: block;
  text-align: center;
  padding: 10px;
  border: 1px solid rgba(255,255,255,0.6);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  text-decoration: none;
  transition: background 0.15s;
  background: rgba(255,255,255,0.15);
}
.banner-left--img .banner-more-btn:hover {
  background: rgba(255,255,255,0.3);
}
.banner-left:not(.banner-left--img) .banner-more-btn {
  display: block;
  text-align: center;
  padding: 10px;
  border: 1px solid #c8c2b4;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #3d3529;
  text-decoration: none;
  transition: background 0.15s;
}
.banner-left:not(.banner-left--img) .banner-more-btn:hover { background: #e8e2d5; }

.banner-right {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: repeat(3, 1fr);
  gap: 12px;
  align-content: stretch;
}

/* 스켈레톤 */
.skeleton-card { border-radius: 12px; overflow: hidden; }
.skeleton-thumb {
  aspect-ratio: 4/3;
  background: linear-gradient(90deg, #f0ece3 25%, #e8e2d5 50%, #f0ece3 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 12px;
  margin-bottom: 8px;
}
.skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, #f0ece3 25%, #e8e2d5 50%, #f0ece3 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 999px;
  margin-bottom: 6px;
}
.w80 { width: 80%; }
.w50 { width: 50%; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>