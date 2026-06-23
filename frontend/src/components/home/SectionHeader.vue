<template>
  <div class="section-header">
    <div class="header-left">
      <span class="section-num">{{ String(num).padStart(2, '0') }}</span>
      <div>
        <h2 class="section-title">{{ title }}</h2>
        <p v-if="subtitle" class="section-sub">{{ subtitle }}</p>
      </div>
    </div>
    <RouterLink v-if="moreTo" :to="moreTo" class="more-link">
      더보기
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke-width="2" stroke="currentColor" width="14" height="14">
        <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
      </svg>
    </RouterLink>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
defineProps({
  num: { type: Number, required: true },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  moreTo: { type: String, default: '' }
})
</script>

<style scoped>
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.section-num {
  font-size: 13px;
  font-weight: 800;
  color: #c8c2b4;
  letter-spacing: 0.05em;
  background: #f0ece3;
  border: 1.5px solid #ddd8cc;
  border-radius: 8px;
  padding: 4px 10px;
  line-height: 1;
}

.section-title {
  font-size: 20px;
  font-weight: 800;
  color: #1a1510;
  margin: 0;
  letter-spacing: -0.01em;
}

.section-sub {
  font-size: 12px;
  color: #9e9585;
  margin: 2px 0 0;
}

.more-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
  color: #1e3a5f;
  text-decoration: none;
  transition: opacity 0.15s;
}
.more-link:hover {
  opacity: 0.7;
}
</style>