<template>
  <RouterLink :to="`/games/${game.id || '#'}`" class="row-card">
    <div class="row-thumb">
      <img v-if="game.thumbnail" :src="game.thumbnail" :alt="game.title" />
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
        <span class="row-badge">-{{ game.discount_rate || 20 }}%</span>
        <span class="row-original">₩{{ formatPrice(game.original_price || 15000) }}</span>
        <span class="row-final">₩{{ formatPrice(game.price || 12000) }}</span>
      </div>
      <div v-else class="row-tags">
        <span v-for="tag in (game.tags || ['태그'])" :key="tag" class="tag">{{ tag }}</span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
import { RouterLink } from 'vue-router'
defineProps({
  game: { type: Object, default: () => ({}) },
  showPrice: { type: Boolean, default: false }
})
function formatPrice(p) {
  return Number(p).toLocaleString('ko-KR')
}
</script>

<style scoped>
.row-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border: 1px solid #e8e4d9;
  border-radius: 10px;
  background: #fff;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.15s;
}
.row-card:hover {
  box-shadow: 0 4px 12px rgba(30,58,95,0.08);
}
.row-thumb {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: #f0ece3;
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
  font-size: 13px;
  font-weight: 600;
  color: #1a1510;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.row-price {
  display: flex;
  align-items: center;
  gap: 6px;
}
.row-badge {
  background: #1a1510;
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}
.row-original {
  font-size: 11px;
  color: #9e9585;
  text-decoration: line-through;
}
.row-final {
  font-size: 13px;
  font-weight: 700;
  color: #1e3a5f;
}
.row-tags {
  display: flex;
  gap: 4px;
}
.tag {
  font-size: 11px;
  color: #6b6256;
  background: #f0ece3;
  border-radius: 999px;
  padding: 2px 8px;
}
</style>