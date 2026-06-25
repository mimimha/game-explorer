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
      <div
        v-for="(game, index) in games.slice(0, authStore.isLoggedIn ? 5 : 4)"
        :key="game.id || index"
        class="today-wrap"
      >
        <GameCard :game="game" :show-wishlist="true" />
      </div>

      <div v-if="!authStore.isLoggedIn" class="login-nudge-card">
        <img :src="cardOneImg" alt="1번 카드" class="nudge-card-img" />
        <div class="nudge-overlay">
          <p class="nudge-sub">로그인 하고</p>
          <p class="nudge-main">나만의 게임 취향을<br />분석 받아보세요.</p>
        </div>
      </div>
    </div>

    <!-- 할인 / 최신 섹션: 배너 + 2열 리스트 -->
    <div v-else class="banner-grid">
      <!-- 왼쪽 배너 -->
      <div class="banner-left">
        <img v-if="type === 'discount'" :src="card2Img" alt="할인 배너" class="banner-img" />
        <img v-else-if="type === 'new'" :src="card3Img" alt="신작 배너" class="banner-img" />
        <div v-else class="banner-img-placeholder">
          <span>이미지</span>
        </div>

        <div class="banner-bottom">
          <h3 class="banner-title">
            {{ type === 'discount' ? '이번 주 할인 모음' : '이번 주 신작' }}
          </h3>
          <p class="banner-desc">
            {{ type === 'discount' ? '다양한 게임을 특별한 가격에!' : '새롭게 출시된 게임을 만나보세요!' }}
          </p>
          <RouterLink
            :to="type === 'discount' ? '/explore?filter=sale' : '/explore?filter=new'"
            class="banner-more-btn"
          >
            {{ type === 'discount' ? '할인 게임 보러가기' : '신작 게임 보러가기' }} ›
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

@media (max-width: 960px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.today-wrap {
  position: relative;
  min-width: 0;
}
/* 로그인 유도 카드 */
.login-nudge-card {
  position: relative;
  min-width: 0;
  border: 1px solid #D8C4A3;
  border-radius: 12px;
  overflow: hidden;
}
.nudge-card-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.nudge-overlay {
  position: absolute;
  inset: 0;
  padding: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 4px;
  text-align: center;
}
.nudge-sub {
  font-family: 'Jua', sans-serif;
  font-size: 16px;
  color: #7a4e25;
  margin: 0;
}
.nudge-main {
  font-family: 'Jua', sans-serif;
  font-size: 18px;
  color: #7a491b;
  margin: 0;
  line-height: 1.4;
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
  border: 1px solid #D8C4A3;
  border-radius: 12px;
  overflow: hidden;
}
.banner-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.banner-img-placeholder {
  position: absolute;
  inset: 0;
  background: #FFF0D6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #9e8c78;
}
.banner-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 14px 20px 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: linear-gradient(to top, rgba(255,247,230,0.98) 80%, transparent 100%);
}
.banner-title {
  font-size: 16px;
  font-weight: 700;
  color: #3A2410;
  margin: 0;
  font-family: 'Pretendard', sans-serif;
}
.banner-desc {
  font-size: 12px;
  color: #6B5A45;
  margin: 0;
  font-family: 'Pretendard', sans-serif;
}
.banner-more-btn {
  display: block;
  text-align: center;
  margin-top: 8px;
  padding: 10px;
  border-radius: 999px;
  background: #D97706;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  text-decoration: none;
  transition: background 0.15s;
  font-family: 'Pretendard', sans-serif;
}
.banner-more-btn:hover {
  background: #B45309;
}

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
  background: linear-gradient(90deg, #FFF0D6 25%, #F2D9A8 50%, #FFF0D6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 12px;
  margin-bottom: 8px;
}
.skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, #FFF0D6 25%, #F2D9A8 50%, #FFF0D6 75%);
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