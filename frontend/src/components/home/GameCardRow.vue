<template>
  <RouterLink :to="game.id ? `/games/${game.id}` : '#'" class="row-card">
    <div class="row-thumb">
      <img v-if="game.capsule_url" :src="game.capsule_url" :alt="game.title" />
      <div v-else class="row-thumb-placeholder">
        <svg viewBox="0 0 60 60"><rect width="60" height="60" fill="#e8e2d5"/>
          <line x1="0" y1="0" x2="60" y2="60" stroke="#c8c2b4" stroke-width="1"/>
          <line x1="60" y1="0" x2="0" y2="60" stroke="#c8c2b4" stroke-width="1"/>
        </svg>
      </div>
    </div>
    <div class="row-info">
      <p class="row-title">{{ game.title || '게임 제목' }}</p>
      <div v-if="showPrice" class="row-price">
        <span v-if="discountRate" class="row-badge">-{{ discountRate }}%</span>
        <span v-if="discountRate" class="row-original">{{ formatPrice(game.initial_price) }}</span>
        <span class="row-final">{{ formatPrice(game.final_price) }}</span>
      </div>
      <div v-else class="row-tags">
        <span v-for="name in genreNames.slice(0, 2)" :key="name" class="tag">{{ name }}</span>
        <span v-if="genreNames.length === 0" class="tag">태그</span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  game: { type: Object, default: () => ({}) },
  showPrice: { type: Boolean, default: false }
})

const discountRate = computed(() => {
  const init = props.game.initial_price
  const final = props.game.final_price
  if (init && final && Number(init) > Number(final)) {
    return Math.round((1 - Number(final) / Number(init)) * 100)
  }
  return null
})

const genreNames = computed(() => (props.game.genres || []).map(g => g.name))

function formatPrice(price) {
  if (price === null || price === undefined) return '무료'
  return '₩' + Number(price).toLocaleString('ko-KR')
}
</script>

<style scoped>
.row-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px;
  border: 1px solid #D8C4A3;
  border-radius: 12px;
  background: #FFFDF7;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.15s;
  height: 100%;
  box-sizing: border-box;
  font-family: 'Pretendard', sans-serif;
  align-items: flex-start;
}
.row-card:hover {
  box-shadow: 0 4px 12px rgba(58, 36, 16, 0.1);
}
.row-thumb {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  border-radius: 10px;
  overflow: hidden;
  background: #FFF0D6;
}
.row-thumb img {
  width: 100%; height: 100%; object-fit: cover;
}
.row-thumb-placeholder svg {
  width: 100%; height: 100%;
}
.row-info {
  flex: 1;
  min-width: 0;
}
.row-title {
  font-size: 16px;
  font-weight: 700;
  color: #2F2418;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'Pretendard', sans-serif;
}
.row-price {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.row-badge {
  background: #D97706;
  color: white;
  font-size: 13px;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 999px;
}
.row-original {
  font-size: 13px;
  color: #6B5A45;
  text-decoration: line-through;
}
.row-final {
  font-size: 16px;
  font-weight: 700;
  color: #3A2410;
}
.row-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.tag {
  font-size: 13px;
  color: #6B5A45;
  background: #FFF0D6;
  border-radius: 999px;
  padding: 3px 10px;
}
</style>