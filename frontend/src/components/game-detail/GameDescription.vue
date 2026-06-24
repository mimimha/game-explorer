<template>
  <section class="desc-section">
    <h2 class="section-title">게임 소개</h2>
    <p class="desc-text">{{ shown }}</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 한글 번역(우선 표시). 아직 번역 전이면 빈 값.
  descriptionKo: { type: String, default: '' },
  // 원문(EN) — 번역이 없을 때만 폴백으로 사용(빈 화면 방지)
  description: { type: String, default: '' },
})

// 한글 번역만 보여주는 게 원칙. 미번역 게임은 빈 화면을 막기 위해 원문으로 폴백.
const shown = computed(() => props.descriptionKo || props.description)
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