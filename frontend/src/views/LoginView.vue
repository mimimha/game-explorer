<template>
  <div class="auth-wrapper">
    <div class="auth-card">

      <div class="auth-header">
        <div class="logo">🎮 방구석 탐험대</div>
        <h1>로그인</h1>
        <p v-if="justRegistered">가입이 완료됐어요! 로그인해주세요 🎉</p>
        <p v-else>반가워요, 오늘도 즐거운 게임 되세요</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form" novalidate>

        <div class="form-group" :class="{ error: errors.email }">
          <label for="email">이메일</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="your@email.com"
            autocomplete="email"
            @blur="validateField('email')"
            @input="clearError('email')"
            ref="emailRef"
          />
          <span class="field-msg" v-if="errors.email">{{ errors.email }}</span>
        </div>

        <div class="form-group" :class="{ error: errors.password }">
          <div class="label-row">
            <label for="password">비밀번호</label>
            <!-- <router-link to="/forgot-password" class="forgot-link">비밀번호를 잊으셨나요?</router-link> -->
          </div>
          <div class="input-with-toggle">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="비밀번호 입력"
              autocomplete="current-password"
              @blur="validateField('password')"
              @input="clearError('password')"
              @keyup.enter="handleLogin"
            />
            <button type="button" class="toggle-pw" @click="showPassword = !showPassword" tabindex="-1">
              {{ showPassword ? '숨기기' : '보기' }}
            </button>
          </div>
          <span class="field-msg" v-if="errors.password">{{ errors.password }}</span>
        </div>

        <div class="options-row">
          <label class="checkbox-label">
            <input type="checkbox" v-model="form.remember" />
            <span class="custom-check"></span>
            <span>로그인 유지</span>
          </label>
        </div>

        <div class="form-error-banner" v-if="apiError">
          <span>{{ apiError }}</span>
        </div>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          <span v-else>로그인</span>
        </button>

      </form>

      <div class="auth-footer">
        아직 계정이 없으신가요?
        <router-link to="/register">회원가입</router-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authAPI, accountAPI } from '@/api/services'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const emailRef = ref(null)

const justRegistered = computed(() => route.query.registered === '1')

const form = reactive({
  email: '',
  password: '',
  remember: false,
})

const errors = reactive({})
const showPassword = ref(false)
const isLoading = ref(false)
const apiError = ref('')

onMounted(() => {
  emailRef.value?.focus()
})

const rules = {
  email: (v) => {
    if (!v) return '이메일을 입력해주세요'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return '올바른 이메일 형식이 아니에요'
    return ''
  },
  password: (v) => {
    if (!v) return '비밀번호를 입력해주세요'
    return ''
  },
}

const validateField = (field) => {
  const msg = rules[field]?.(form[field]) ?? ''
  if (msg) errors[field] = msg
  else delete errors[field]
  return !msg
}

const clearError = (field) => {
  delete errors[field]
  apiError.value = ''
}

const validateAll = () => {
  return ['email', 'password'].map(validateField).every(Boolean)
}

const handleLogin = async () => {
  apiError.value = ''
  if (!validateAll()) return

  isLoading.value = true
  try {
    const { data } = await authAPI.login({ email: form.email, password: form.password })
    const token = data.key
    if (form.remember) {
      localStorage.setItem('token', token)
    } else {
      sessionStorage.setItem('token', token)
      localStorage.setItem('token', token)
    }
    const meRes = await accountAPI.getMe()
    authStore.login(meRes.data, token)
    router.push('/')
  } catch (err) {
    const status = err?.response?.status
    if (status === 400 || status === 401) {
      apiError.value = '이메일 또는 비밀번호가 올바르지 않아요'
    } else {
      apiError.value = '로그인 중 오류가 발생했어요. 잠시 후 다시 시도해주세요.'
    }
  } finally {
    isLoading.value = false
  }
}

const loginWithSocial = (provider) => {
  // TODO: 소셜 로그인 연동
  console.log(`${provider} 로그인`)
}
</script>

<style scoped>
/* ── 레이아웃 ── */
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7f7f5;
  padding: 40px 16px;
}

.auth-card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 24px rgba(0,0,0,0.05);
  padding: 48px 44px;
  width: 100%;
  max-width: 440px;
}

/* ── 헤더 ── */
.auth-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: #111;
  margin-bottom: 20px;
}

.auth-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #111;
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}

.auth-header p {
  font-size: 14px;
  color: #888;
  margin: 0;
}

/* ── 폼 ── */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

label {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.forgot-link {
  font-size: 12px;
  color: #888;
  text-decoration: none;
}

.forgot-link:hover {
  color: #111;
  text-decoration: underline;
}

input[type="email"],
input[type="password"],
input[type="text"] {
  width: 100%;
  padding: 11px 14px;
  border: 1.5px solid #e8e8e8;
  border-radius: 10px;
  font-size: 14px;
  color: #111;
  background: #fafafa;
  outline: none;
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
}

input:focus {
  border-color: #111;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(17,17,17,0.06);
}

.form-group.error input {
  border-color: #e53e3e;
  background: #fff8f8;
}

/* ── 비밀번호 토글 ── */
.input-with-toggle {
  position: relative;
}

.input-with-toggle input {
  padding-right: 60px;
}

.toggle-pw {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 12px;
  color: #888;
  cursor: pointer;
  padding: 4px;
  font-weight: 500;
}

.toggle-pw:hover { color: #111; }

/* ── 필드 메시지 ── */
.field-msg {
  font-size: 12px;
  color: #e53e3e;
}

/* ── 옵션 행 ── */
.options-row {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #444;
}

.checkbox-label input[type="checkbox"] {
  display: none;
}

.custom-check {
  width: 18px;
  height: 18px;
  min-width: 18px;
  border: 1.5px solid #ddd;
  border-radius: 5px;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.15s, background 0.15s;
}

.checkbox-label input:checked + .custom-check {
  background: #111;
  border-color: #111;
}

.checkbox-label input:checked + .custom-check::after {
  content: '';
  display: block;
  width: 5px;
  height: 9px;
  border: 2px solid #fff;
  border-top: none;
  border-left: none;
  transform: rotate(45deg) translate(-1px, -1px);
}

/* ── 에러 배너 ── */
.form-error-banner {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  color: #c53030;
  font-size: 13px;
  padding: 12px 14px;
  border-radius: 8px;
}

/* ── 버튼 ── */
.btn-primary {
  width: 100%;
  padding: 13px;
  background: #111;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 4px;
}

.btn-primary:hover:not(:disabled) { background: #222; }
.btn-primary:active:not(:disabled) { transform: scale(0.99); }
.btn-primary:disabled { background: #ccc; cursor: not-allowed; }

/* ── 스피너 ── */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── 구분선 ── */
.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 24px 0 16px;
  color: #ccc;
  font-size: 12px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #eee;
}

/* ── 소셜 버튼 ── */
.social-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-social {
  width: 100%;
  padding: 11px;
  background: #fff;
  border: 1.5px solid #e8e8e8;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: border-color 0.15s, background 0.15s;
}

.btn-social:hover {
  border-color: #ccc;
  background: #fafafa;
}

/* ── 푸터 ── */
.auth-footer {
  margin-top: 28px;
  text-align: center;
  font-size: 13px;
  color: #888;
}

.auth-footer a {
  color: #111;
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
}

.auth-footer a:hover { text-decoration: underline; }

/* ── 반응형 ── */
@media (max-width: 480px) {
  .auth-card {
    padding: 36px 24px;
    border-radius: 12px;
  }
}
</style>
