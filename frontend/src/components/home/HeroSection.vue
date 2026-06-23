<template>
  <section class="hero">
    <div class="hero-text">
      <h1>새로운 세계로의 탐험,<br />방구석 탐험대와 함께</h1>
      <p>
        당신의 취향에 맞는 인디 게임을 추천받고<br />
        다양한 게임을 탐험해보세요.
      </p>
      <button>탐험 시작하기</button>
    </div>

    <div class="hero-image">
      <!-- 나중에 이미지 / GIF -->
    </div>
  </section>
</template>

<style scoped>
.hero {
  display: flex;
  justify-content: space-between;
  background: #f4f6f8;
  padding: 48px;
  border-radius: 12px;
}
.hero-text h1 {
  font-size: 32px;
}
.hero-text button {
  margin-top: 16px;
}
.hero-image {
  width: 2100px;
  height: 840px;
  background: #e0e0e0;
}
</style>