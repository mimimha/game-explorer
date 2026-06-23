<template>
  <section class="section">
    <SectionHeader
      :num="num"
      :title="title"
      :subtitle="subtitle"
      :more-to="moreTo"
      :show-arrows="showArrows"
      @prev="onPrev"
      @next="onNext"
    />

    <!-- 로딩 스켈레톤 -->
    <div v-if="loading" class="card-grid">
      <div v-for="i in 6" :key="i" class="skeleton-card">
        <div class="skeleton-thumb"></div>
        <div class="skeleton-line w80"></div>
        <div class="skeleton-line w50"></div>
      </div>
    </div>

    <!-- 취향 분석 섹션 -->
    <div v-else-if="type === 'recommendation'" class="card-grid">
      <div v-if="!authStore.isLoggedIn" class="login-nudge-card">
        <p>로그인하고<br /><strong>나만의 취향</strong>을<br />분석받아보세요!</p>
        <RouterLink to="/login" class="nudge-btn">로그인 / 회원가입</RouterLink>
      </div>

      <div
        v-for="(game, index) in games.slice(0, authStore.isLoggedIn ? 6 : 5)"
        :key="game.id || index"
        class="today-wrap"
      >
        <span v-if="index === 0" class="today-label">오늘의 추천</span>
        <GameCard :game="game" :show-wishlist="true" />
      </div>
    </div>

    <!-- 할인 / 최신 섹션: 배너 + 2열 리스트 -->
    <div v-else class="banner-grid">
      <!-- 왼쪽 배너 -->
      <div class="banner-left">
        <div class="banner-image">
          <span class="banner-placeholder">
            {{ type === 'discount' ? '프로모션 배너 / 키아트' : '신작 스포트라이트 / 키아트' }}
          </span>
        </div>
        <h3 class="banner-title">
          {{ type === 'discount' ? '이번 주 할인 모음' : '이번 주 신작' }}
        </h3>
        
        <RouterLink
          :to="type === 'discount' ? '/games?filter=sale' : '/games?filter=new'"
          class="banner-more-btn"
        >
          더 보기
        </RouterLink>
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

function onPrev() {}
function onNext() {}
</script>

<style scoped>
.section {
  margin-bottom: 56px;
}

/* 취향 분석 그리드 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.today-wrap {
  position: relative;
}
.today-label {
  position: absolute;
  top: -10px;
  left: 10px;
  background: #1e3a5f;
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  z-index: 1;
}

/* 로그인 유도 카드 */
.login-nudge-card {
  background: #f0ece3;
  border: 1.5px dashed #c8c2b4;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 12px;
  gap: 10px;
  text-align: center;
  font-size: 13px;
  color: #6b6256;
  line-height: 1.5;
}
.login-nudge-card strong { color: #1a1510; }
.nudge-btn {
  display: block;
  background: #1a1510;
  color: white;
  border-radius: 8px;
  padding: 9px 14px;
  font-size: 12px;
  font-weight: 700;
  text-decoration: none;
}
.nudge-btn:hover { background: #1e3a5f; }
.nudge-sub { font-size: 10px; color: #9e9585; }

/* 배너 그리드 (할인/최신) */
.banner-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
}

.banner-left {
  background: #f0ece3;
  border: 1px solid #e8e4d9;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.banner-image {
  flex: 1;
  min-height: 200px;
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
.banner-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1510;
}
.banner-sub {
  font-size: 13px;
  color: #9e9585;
}
.banner-more-btn {
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
.banner-more-btn:hover { background: #e8e2d5; }

.banner-right {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: repeat(3, auto);
  gap: 12px;
  align-content: start;
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