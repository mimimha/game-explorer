<script setup>
import { RouterLink } from 'vue-router'
import heroImg from '@/assets/hero.png'
</script>

<template>
  <section class="hero" :style="{ backgroundImage: `url(${heroImg})` }">
    <div class="hero-overlay" />
    <div class="hero-text">
      <span class="hero-badge">⭐ 새로운 세계가 기다리고 있어요!</span>
      <h1>
        새로운 세계로의 탐험,<br />
        <span class="hero-highlight">방구석 탐험대와 함께</span>
      </h1>
      <p>
        당신의 게임에 맞는 멋진 계획을 추천받고<br />
        다양한 커뮤니티를 만나보세요.
      </p>
      <div class="hero-buttons">
        <RouterLink to="/explore" class="hero-btn-primary">탐험 시작하기 ›</RouterLink>
        <RouterLink to="/community" class="hero-btn-outline">커뮤니티 둘러보기</RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  display: flex;
  align-items: center;
  background-size: cover;
  background-position: center;
  min-height: 720px;
  padding: 64px 48px 64px 10%;
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to right,
    rgba(255, 247, 230, 0.596) 0%,
    rgba(255, 247, 230, 0.212) 40%,
    rgba(255, 247, 230, 0.1) 65%,
    transparent 80%
  );
  pointer-events: none;
}

.hero-text {
  position: relative;
  z-index: 1;
  flex: 1;
  min-width: 0;
  max-width: 560px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  border: 1.5px solid #D97706;
  background: rgba(255, 247, 230, 0.85);
  color: #D97706;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Pretendard', sans-serif;
  margin-bottom: 16px;
}

.hero-text h1 {
  font-family: 'Jua', sans-serif;
  font-size: 52px;
  line-height: 1.25;
  word-break: keep-all;
  color: #3A2410;
  margin: 0 0 16px;
}

.hero-highlight {
  color: #D97706;
}

.hero-text p {
  font-family: 'Pretendard', sans-serif;
  font-size: 17px;
  color: #5A3512;
  margin: 0 0 28px;
  line-height: 1.7;
}

.hero-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-btn-primary {
  display: inline-flex;
  align-items: center;
  padding: 12px 28px;
  border-radius: 999px;
  background: #D97706;
  color: #fff;
  font-family: 'Pretendard', sans-serif;
  font-size: 15px;
  font-weight: 700;
  text-decoration: none;
  transition: background 0.15s;
}
.hero-btn-primary:hover {
  background: #B45309;
}

.hero-btn-outline {
  display: inline-flex;
  align-items: center;
  padding: 12px 28px;
  border-radius: 999px;
  border: 1.5px solid #3A2410;
  background: rgba(255, 247, 230, 0.7);
  color: #3A2410;
  font-family: 'Pretendard', sans-serif;
  font-size: 15px;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.15s;
}
.hero-btn-outline:hover {
  background: rgba(255, 247, 230, 0.95);
  border-color: #D97706;
  color: #D97706;
}
</style>
