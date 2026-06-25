<template>
  <main class="error-page">
    <div class="error-content">
      <img src="@/assets/404.png" alt="페이지를 찾을 수 없습니다" class="error-img" />
      <p class="error-text">길을 잃었어요. 최대한 빠르게 길을 찾아볼게요.</p>
      <p class="error-text error-text-sub">조금만 기다려주세요.</p>
    </div>
  </main>
</template>

<style scoped>
.error-page {
  min-height: calc(100vh - 80px);
  background: #FFF7E6;
  display: flex;
  align-items: center;
  justify-content: center;
}
.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}
.error-text-sub {
  margin-top: -20px;
}
.error-img {
  max-width: 600px;
  width: 90%;
  object-fit: contain;
}
.error-text {
  max-width: 600px;
  width: 90%;
  font-size: 1.4rem;
  font-family: 'Jua', sans-serif;
  color: #6B5A45;
  text-align: center;
  line-height: 1.7;
}
</style>
