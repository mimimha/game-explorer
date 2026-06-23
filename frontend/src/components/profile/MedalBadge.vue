<template>
  <div class="medal-badge" :class="{ locked: locked }">
    <div class="medal-icon">
      <img v-if="!locked && medal?.icon_url" :src="medal.icon_url" :alt="medal.medal_name" />
      <span v-else-if="locked" class="locked-mark">?</span>
      <svg v-else class="default-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <component :is="'path'" v-bind="iconPath" />
      </svg>
    </div>
    <p class="medal-name">{{ locked ? '더 많은 메달을' : medal?.medal_name }}</p>
    <p class="medal-desc">{{ locked ? '획득해보세요!' : medal?.description }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  medal: { type: Object, default: null },
  locked: { type: Boolean, default: false },
})

const ICON_PATHS = {
  '게시글': { d: 'M16.862 4.487l1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10', fill: 'none', stroke: '#6b6256', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' },
  '스타': { d: 'M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z', fill: 'none', stroke: '#6b6256', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' },
  '공유': { d: 'M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0 0a2.25 2.25 0 1 0 3.935 2.186 2.25 2.25 0 0 0-3.935-2.186Zm0-12.814a2.25 2.25 0 1 0 3.933-2.185 2.25 2.25 0 0 0-3.933 2.185Z', fill: 'none', stroke: '#6b6256', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' },
  '탐험': { d: 'M16.5 18.75h-9m9 0a3 3 0 0 1 3 3h-15a3 3 0 0 1 3-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 0 1-.982-3.172M9.497 14.25a7.454 7.454 0 0 0 .981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 0 0 7.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 0 0 2.748 1.35m8.272-6.842V4.5c0 2.108-.966 3.99-2.48 5.228m2.48-5.492a46.32 46.32 0 0 1 2.916.52 6.003 6.003 0 0 1-5.395 4.972m0 0a6.726 6.726 0 0 1-2.749 1.35m0 0a6.772 6.772 0 0 1-3.044 0', fill: 'none', stroke: '#6b6256', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' },
  '게이머': { d: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z M15.91 11.672a.375.375 0 0 1 0 .656l-5.603 3.113a.375.375 0 0 1-.557-.328V8.887c0-.286.307-.466.557-.327l5.603 3.112Z', fill: 'none', stroke: '#6b6256', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' },
  'default': { d: 'M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z', fill: 'none', stroke: '#6b6256', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' },
}

const iconPath = computed(() => {
  if (!props.medal) return ICON_PATHS.default
  const name = props.medal.medal_name || ''
  for (const key of Object.keys(ICON_PATHS)) {
    if (name.includes(key)) return ICON_PATHS[key]
  }
  return ICON_PATHS.default
})
</script>

<style scoped>
.medal-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 8px;
  border-radius: 12px;
  background: #faf8f3;
  border: 1px solid #e8e4d9;
  transition: background 0.15s;
  min-width: 90px;
  flex: 1;
}
.medal-badge:not(.locked):hover {
  background: #f0ece3;
}
.medal-badge.locked {
  background: #f5f1e8;
  border-style: dashed;
  opacity: 0.65;
}

.medal-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #e8e4d9;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.medal-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.default-icon {
  width: 22px;
  height: 22px;
}
.locked-mark {
  font-size: 18px;
  font-weight: 700;
  color: #9e9585;
}

.medal-name {
  font-size: 12px;
  font-weight: 600;
  color: #1a1510;
  text-align: center;
  margin: 0;
  white-space: nowrap;
}
.medal-desc {
  font-size: 11px;
  color: #9e9585;
  text-align: center;
  margin: 0;
  white-space: nowrap;
}
</style>
