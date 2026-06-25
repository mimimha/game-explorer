<template>
  <ul v-if="suggestions.length" class="suggest-list" role="listbox">
    <li
      v-for="(s, i) in suggestions"
      :key="s.game_id"
      class="suggest-item"
      :class="{ active: i === activeIdx }"
      role="option"
      :aria-selected="i === activeIdx"
      @mousedown.prevent="$emit('select', s)"
      @mousemove="$emit('hover', i)"
    >
      <span class="suggest-title">{{ s.title_ko || s.title }}</span>
      <span v-if="s.title_ko && s.title_ko !== s.title" class="suggest-orig">{{ s.title }}</span>
    </li>
  </ul>
</template>

<script setup>
defineProps({
  suggestions: { type: Array, default: () => [] },
  activeIdx: { type: Number, default: -1 },
})
defineEmits(['select', 'hover'])
</script>

<style scoped>
.suggest-list {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.10);
  list-style: none;
  margin: 0;
  padding: 6px;
  z-index: 999;
  overflow: hidden;
}
.suggest-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.1s;
}
.suggest-item:hover,
.suggest-item.active {
  background: #f0ece3;
}
.suggest-title {
  font-size: 14px;
  color: #1a1510;
  font-weight: 500;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.suggest-orig {
  font-size: 12px;
  color: #9e9585;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}
</style>
