<template>
  <main class="home">
    <HeroSection />

    <div class="content">
      <GameCardList
        :num="1"
        title="취향 분석 · 오늘의 게임"
        subtitle="로그인 시 취향 기반 · 미로그인 시 랜덤 5개"
        type="recommendation"
        more-to="/games?type=recommendation"
      />

      <GameCardList
        :num="2"
        title="할인 중인 게임"
        type="discount"
        more-to="/games?filter=sale"
      />

      <GameCardList
        :num="3"
        title="최근 출시 게임"
        type="new"
        more-to="/games?filter=new"
      />
    </div>

    <FooterSection />
  </main>
</template>

<script setup>
import HeroSection from '@/components/home/HeroSection.vue'
import GameCardList from '@/components/home/GameCardList.vue'
import FooterSection from '@/components/home/FooterSection.vue'
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