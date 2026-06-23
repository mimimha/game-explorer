<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="visible" class="toast" :class="type">
        <!-- 아이콘 -->
        <svg v-if="type === 'warning'" xmlns="http://www.w3.org/2000/svg" fill="none"
          viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="18">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
        </svg>
        <svg v-else-if="type === 'success'" xmlns="http://www.w3.org/2000/svg" fill="none"
          viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="18">
          <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none"
          viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="18">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
        </svg>

        <span class="msg">{{ message }}</span>

        <button class="close" @click="hide">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            stroke-width="2" stroke="currentColor" width="14">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
const type = ref('warning')   // 'warning' | 'success' | 'info'
let timer = null

function show(msg, t = 'warning', duration = 3000) {
  message.value = msg
  type.value = t
  visible.value = true
  clearTimeout(timer)
  timer = setTimeout(hide, duration)
}

function hide() {
  visible.value = false
  clearTimeout(timer)
}

defineExpose({ show })
</script>

<style scoped>
.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 8px 32px rgba(0,0,0,0.14);
  min-width: 280px;
  max-width: 420px;
  pointer-events: all;
}

/* 타입별 색상 */
.toast.warning {
  background: #fff8e6;
  border: 1.5px solid #f0c040;
  color: #7a5700;
}
.toast.warning svg { color: #e09900; }

.toast.success {
  background: #edfaf3;
  border: 1.5px solid #6dd49a;
  color: #1a5c38;
}
.toast.success svg { color: #27ae60; }

.toast.info {
  background: #eef3fa;
  border: 1.5px solid #93b4e0;
  color: #1e3a5f;
}
.toast.info svg { color: #1e3a5f; }

.msg { flex: 1; line-height: 1.5; }

.close {
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  opacity: 0.5;
  display: flex;
  align-items: center;
  padding: 0;
  flex-shrink: 0;
  transition: opacity 0.15s;
}
.close:hover { opacity: 1; }

/* 슬라이드 인/아웃 */
.toast-enter-active { transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1); }
.toast-leave-active { transition: all 0.2s ease-in; }
.toast-enter-from  { opacity: 0; transform: translateX(-50%) translateY(-12px) scale(0.95); }
.toast-leave-to    { opacity: 0; transform: translateX(-50%) translateY(-8px) scale(0.97); }
</style>