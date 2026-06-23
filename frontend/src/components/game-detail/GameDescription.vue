<template>
  <section class="desc-section">
    <h2 class="section-title">게임 소개</h2>
    <p class="desc-text">{{ description }}</p>
  </section>
</template>

<script setup>
defineProps({
  description: { type: String, default: '' },
})
</script>

<style scoped>
.desc-section {
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 14px;
  padding: 28px 32px;
  margin-bottom: 20px;
}
.section-title {
  font-size: 18px;
  font-weight: 800;
  color: #1a1510;
  margin: 0 0 16px;
}
.desc-text {
  font-size: 14px;
  color: #3d3529;
  line-height: 1.85;
  white-space: pre-line;
  margin: 0;
}
</style>