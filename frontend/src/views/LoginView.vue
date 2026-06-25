<template>
  <div class="login-page">
    <img src="@/assets/로그인배경.png" alt="" class="page-bg" />

    <div class="login-card">

      <h1 class="card-title">방구석 탐험대에<br>오신 것을 환영합니다!</h1>
      <p class="card-sub">로그인하고 더 많은 게임과 모험을 만나보세요.</p>

      <form @submit.prevent="handleLogin" class="login-form" novalidate>

        <div class="field-wrap" :class="{ error: errors.email }">
          <div class="input-row">
            <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
            </svg>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="이메일"
              autocomplete="email"
              @blur="validateFieldOnBlur('email')"
              @input="clearError('email')"
              ref="emailRef"
            />
          </div>
          <span class="field-msg" v-if="errors.email">{{ errors.email }}</span>
        </div>

        <div class="field-wrap" :class="{ error: errors.password }">
          <div class="input-row">
            <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
            </svg>
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="비밀번호"
              autocomplete="current-password"
              @blur="validateFieldOnBlur('password')"
              @input="clearError('password')"
              @keyup.enter="handleLogin"
            />
            <button type="button" class="toggle-pw" @click="showPassword = !showPassword" tabindex="-1">
              <svg v-if="showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
              </svg>
            </button>
          </div>
          <span class="field-msg" v-if="errors.password">{{ errors.password }}</span>
        </div>

        <div class="options-row">
          <label class="check-label">
            <input type="checkbox" v-model="form.remember" />
            <span class="custom-check"></span>
            <span>로그인 상태 유지</span>
          </label>
          <!-- <a href="#" class="forgot-link">비밀번호 찾기</a> -->
        </div>

        <div class="error-banner" v-if="apiError">{{ apiError }}</div>

        <button type="submit" class="btn-login" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          <span v-else>로그인</span>
        </button>

      </form>

      <router-link to="/register" class="btn-register">회원가입</router-link>


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

const validateFieldOnBlur = (field) => {
  if (!form[field]) return
  validateField(field)
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
</script>

<style scoped>
/* ── 페이지 레이아웃 ── */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  position: relative;
  overflow: hidden;
  background: #FFF7E6;
}

.page-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: left center;
  pointer-events: none;
  user-select: none;
}

/* ── 카드 ── */
.login-card {
  position: relative;
  z-index: 10;
  background: rgba(255, 253, 247, 0.96);
  border-radius: 24px;
  padding: 48px 44px;
  width: 460px;
  margin-right: 80px;
  box-shadow: 0 8px 48px rgba(58,36,16,0.18);
  backdrop-filter: blur(2px);
}

/* ── 타이틀 ── */
.card-title {
  font-size: 28px;
  font-weight: 800;
  color: #3A2410;
  margin: 0 0 10px;
  line-height: 1.35;
  letter-spacing: -0.5px;
}

.card-sub {
  font-size: 14px;
  color: #6B5A45;
  margin: 0 0 28px;
}

/* ── 폼 ── */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 12px;
}

.field-wrap {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.input-row {
  display: flex;
  align-items: center;
  border: 1.5px solid #D8C4A3;
  border-radius: 12px;
  background: #fff;
  transition: border-color 0.15s, box-shadow 0.15s;
  overflow: hidden;
}

.input-row:focus-within {
  border-color: #D97706;
  box-shadow: 0 0 0 3px rgba(217,119,6,0.1);
}

.field-wrap.error .input-row {
  border-color: #e53e3e;
}

.field-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: #9e9585;
  margin-left: 14px;
}

.input-row input {
  flex: 1;
  padding: 13px 12px;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #3A2410;
  outline: none;
  font-family: inherit;
}

.input-row input::placeholder { color: #b0a090; }

.toggle-pw {
  background: none;
  border: none;
  padding: 0 14px;
  cursor: pointer;
  color: #9e9585;
  display: flex;
  align-items: center;
}
.toggle-pw:hover { color: #3A2410; }
.toggle-pw svg { width: 18px; height: 18px; }

.field-msg {
  font-size: 12px;
  color: #e53e3e;
  padding-left: 4px;
}

/* ── 옵션 행 ── */
.options-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.check-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #6B5A45;
}

.check-label input[type="checkbox"] { display: none; }

.custom-check {
  width: 18px;
  height: 18px;
  min-width: 18px;
  border: 1.5px solid #D8C4A3;
  border-radius: 5px;
  background: #FFFDF7;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.15s, background 0.15s;
}

.check-label input:checked + .custom-check {
  background: #D97706;
  border-color: #D97706;
}

.check-label input:checked + .custom-check::after {
  content: '';
  display: block;
  width: 5px;
  height: 9px;
  border: 2px solid #fff;
  border-top: none;
  border-left: none;
  transform: rotate(45deg) translate(-1px, -1px);
}

.forgot-link {
  font-size: 13px;
  color: #6B5A45;
  text-decoration: none;
}
.forgot-link:hover { color: #D97706; text-decoration: underline; }

/* ── 에러 배너 ── */
.error-banner {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  color: #c53030;
  font-size: 13px;
  padding: 10px 14px;
  border-radius: 10px;
}

/* ── 버튼 ── */
.btn-login {
  width: 100%;
  padding: 14px;
  background: #D97706;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 4px;
  font-family: inherit;
}
.btn-login:hover:not(:disabled) { background: #B45309; }
.btn-login:active:not(:disabled) { transform: scale(0.99); }
.btn-login:disabled { background: #e8c07a; cursor: not-allowed; }

.btn-register {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 13px;
  background: transparent;
  color: #D97706;
  border: 1.5px solid #D97706;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  margin-top: 10px;
  box-sizing: border-box;
  font-family: inherit;
}
.btn-register:hover { background: #FFF0D6; }

/* ── 스피너 ── */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 반응형 ── */
@media (max-width: 900px) {
  .login-card {
    margin-right: 40px;
    width: 420px;
    padding: 40px 36px;
  }
}

@media (max-width: 600px) {
  .login-page {
    justify-content: center;
  }
  .login-card {
    margin: 0 16px;
    width: 100%;
    max-width: 460px;
    border-radius: 20px;
    padding: 36px 28px;
  }
}
</style>
