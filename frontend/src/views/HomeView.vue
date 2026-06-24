<template>
  <main class="home">
    <HeroSection />

    <div class="content">
      <GameCardList
        :num="1"
        :title="recommendTitle"
        :subtitle="recommendSubtitle"
        type="recommendation"
      />

      <GameCardList
        :num="2"
        title="할인 중인 게임"
        type="discount"
        more-to="/explore?filter=sale"
      />

      <GameCardList
        :num="3"
        title="최근 출시 게임"
        type="new"
        more-to="/explore?filter=new"
      />
    </div>

    <FooterSection />
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import HeroSection from '@/components/home/HeroSection.vue'
import GameCardList from '@/components/home/GameCardList.vue'
import FooterSection from '@/components/home/FooterSection.vue'
import { useAuthStore } from '@/stores/auth'
import { wishlistAPI, recommendAPI } from '@/api/services'

const authStore = useAuthStore()

const hasWishlist = ref(false)
const hasRecommendLog = ref(false)

onMounted(async () => {
  if (!authStore.isLoggedIn) return
  try {
    const [wishlistRes, logsRes] = await Promise.all([
      wishlistAPI.list(),
      recommendAPI.logs(),
    ])
    const wishlistData = wishlistRes.data
    const logsData = logsRes.data
    hasWishlist.value = Array.isArray(wishlistData)
      ? wishlistData.length > 0
      : (wishlistData.results ?? []).length > 0
    hasRecommendLog.value = Array.isArray(logsData)
      ? logsData.length > 0
      : (logsData.results ?? []).length > 0
  } catch {
    // 데이터 없음으로 처리
  }
})

const isPersonalized = computed(
  () => authStore.isLoggedIn && (hasWishlist.value || hasRecommendLog.value)
)

const recommendTitle = computed(() =>
  isPersonalized.value ? 'AI 기반 취향 분석' : '오늘의 추천'
)
const recommendSubtitle = computed(() =>
  isPersonalized.value
    ? '찜 목록과 AI 검색 기록 기반 취향 분석'
    : '로그인 시 취향 분석 게임 추천'
)
</script>

<style scoped>
.home {
  background: #fafaf8;
}
.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 40px 0;
}
</style>