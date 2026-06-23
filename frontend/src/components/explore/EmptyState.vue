<template>
  <div class="empty">
    <!-- sparkle 아이콘 -->
    <svg v-if="icon === 'sparkle'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="40">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
    </svg>
    <!-- search 아이콘 -->
    <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="40">
      <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
    </svg>

    <p v-html="message"></p>

    <button v-if="showReset" class="reset-btn" @click="$emit('reset')">
      검색 조건 초기화
    </button>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: 'search' },       // 'sparkle' | 'search'
  message: { type: String, default: '' },
  showReset: { type: Boolean, default: false },
})
defineEmits(['reset'])
</script>

<style scoped>
.empty {
  border: 1.5px dashed #ddd8cc;
  border-radius: 14px;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #9e9585;
  text-align: center;
}
.empty svg { color: #c8c2b4; }
.empty p { font-size: 14px; line-height: 1.7; }
.empty :deep(strong) { color: #3d3529; }

.reset-btn {
  margin-top: 4px;
  padding: 10px 20px;
  border: 1.5px solid #ddd8cc;
  border-radius: 8px;
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  color: #3d3529;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}
.reset-btn:hover { border-color: #1e3a5f; color: #1e3a5f; }
</style>