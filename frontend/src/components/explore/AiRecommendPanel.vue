<template>
  <div class="panel" :class="{ active: isActive }" @click="$emit('activate')">
    <div class="panel-header">
      <h2>
        AI 추천
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon">
          <path d="M15.98 1.804a1 1 0 0 0-1.96 0l-.24 1.192a1 1 0 0 1-.784.785l-1.192.238a1 1 0 0 0 0 1.962l1.192.238a1 1 0 0 1 .785.785l.238 1.192a1 1 0 0 0 1.962 0l.238-1.192a1 1 0 0 1 .785-.785l1.192-.238a1 1 0 0 0 0-1.962l-1.192-.238a1 1 0 0 1-.785-.785l-.238-1.192ZM6.949 5.684a1 1 0 0 0-1.898 0l-.683 2.051a1 1 0 0 1-.633.633l-2.051.683a1 1 0 0 0 0 1.898l2.051.683a1 1 0 0 1 .633.633l.683 2.051a1 1 0 0 0 1.898 0l.683-2.051a1 1 0 0 1 .633-.633l2.051-.683a1 1 0 0 0 0-1.898l-2.051-.683a1 1 0 0 1-.633-.633L6.95 5.684Z" />
        </svg>
      </h2>
      <p class="desc">원하는 게임을 설명하면 AI가 추천해드려요.</p>
    </div>

    <div class="textarea-wrap">
      <textarea
        v-model="prompt"
        class="textarea"
        placeholder="예) 스토리가 좋은 픽셀 그래픽 RPG 추천해줘"
        maxlength="300"
        @focus="$emit('activate')"
        @keydown.enter.exact.prevent="handleSubmit"
      ></textarea>
      <div class="char-count">{{ prompt.length }} / 300</div>
    </div>

    <div class="footer-row">
      <div v-if="!authStore.isLoggedIn" class="login-notice">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="14">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
        </svg>
        로그인한 사용자만 AI 추천을 이용할 수 있습니다.
      </div>

      <button class="btn-recommend" @click.stop="handleSubmit" :disabled="loading">
        <span v-if="loading" class="spinner"></span>
        <svg v-else viewBox="0 0 20 20" fill="currentColor" width="14">
          <path d="M15.98 1.804a1 1 0 0 0-1.96 0l-.24 1.192a1 1 0 0 1-.784.785l-1.192.238a1 1 0 0 0 0 1.962l1.192.238a1 1 0 0 1 .785.785l.238 1.192a1 1 0 0 0 1.962 0l.238-1.192a1 1 0 0 1 .785-.785l1.192-.238a1 1 0 0 0 0-1.962l-1.192-.238a1 1 0 0 1-.785-.785l-.238-1.192Z" />
        </svg>
        {{ loading ? '추천 중...' : '추천받기 ✦' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

defineProps({
  isActive: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['activate', 'submit'])

const prompt = ref('')
function handleSubmit() {
  if (!prompt.value.trim()) return
  emit('submit', { prompt: prompt.value })
}

// 부모에서 prompt를 세팅할 수 있도록 expose
defineExpose({ setPrompt: (v) => { prompt.value = v } })
</script>

<style scoped>
.panel {
  background: #fff;
  border: 1.5px solid #e8e4d9;
  border-radius: 16px;
  padding: 28px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.panel.active {
  border-color: #c96012;
  box-shadow: 0 0 0 3px rgba(201,96,18,0.07);
  cursor: default;
}

.panel-header h2 {
  font-size: 18px;
  font-weight: 800;
  color: #1a1510;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.icon { width: 16px; color: #c96012; }
.desc { font-size: 13px; color: #9e9585; }

.textarea-wrap {
  background: #f7f5f0;
  border: 1px solid #e8e4d9;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: border-color 0.15s;
}
.textarea-wrap:focus-within {
  border-color: #c96012;
  background: #fff;
}

.textarea {
  width: 100%;
  height: 90px;
  resize: none;
  border: none;
  border-radius: 0;
  padding: 0;
  font-size: 14px;
  font-family: inherit;
  color: #1a1510;
  background: transparent;
  outline: none;
  line-height: 1.6;
}
.textarea::placeholder { color: #c8c2b4; }

.char-count { text-align: right; font-size: 11px; color: #c8c2b4; }

.footer-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.login-notice {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #9e9585;
  background: #f7f5f0;
  border-radius: 8px;
  padding: 10px 14px;
  flex: 1;
}
.login-link {
  margin-left: auto;
  font-size: 12px;
  font-weight: 600;
  color: #1e3a5f;
  text-decoration: none;
  border: 1px solid #1e3a5f;
  padding: 4px 10px;
  border-radius: 6px;
  transition: all 0.15s;
}
.login-link:hover { background: #1e3a5f; color: white; }

.btn-recommend {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  padding: 10px 22px;
  background: #c96012;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}
.btn-recommend:hover:not(:disabled) { background: #a84e0e; }
.btn-recommend:disabled { opacity: 0.6; cursor: default; }

.spinner {
  width: 12px; height: 12px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>