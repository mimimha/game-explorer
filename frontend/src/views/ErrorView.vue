<template>
  <main class="error-page">
    <img src="@/assets/404.png" alt="페이지를 찾을 수 없습니다" class="error-img" />
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
.error-img {
  max-width: 600px;
  width: 90%;
  object-fit: contain;
}
</style>
