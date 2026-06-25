<template>
  <section class="section-card">
    <div class="section-header">
      <h3 class="section-title">획득 메달</h3>
    </div>
    <div class="medal-grid">
      <MedalBadge
        v-for="medal in visibleMedals"
        :key="medal.id"
        :medal="medal"
      />
      <MedalBadge v-if="medals.length < MAX_DISPLAY" :locked="true" />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import MedalBadge from './MedalBadge.vue'

const MAX_DISPLAY = 6

const props = defineProps({
  medals: { type: Array, default: () => [] },
})

const visibleMedals = computed(() => props.medals.slice(0, MAX_DISPLAY - 1))
</script>

<style scoped>
.section-card {
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 16px;
  padding: 24px 28px;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1510;
  margin: 0;
}
.view-all {
  font-size: 13px;
  color: #6b6256;
  text-decoration: none;
}
.view-all:hover {
  color: #1e3a5f;
}
.medal-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.medal-grid > * {
  flex: 1;
  min-width: 80px;
  max-width: 120px;
}
</style>
