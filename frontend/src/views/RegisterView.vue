<template>
  <div class="register-page">
    <img src="@/assets/회원가입배경.png" alt="" class="page-bg" />

    <div class="register-card">

      <h1 class="card-title">탐험대에 합류하세요!</h1>
      <p class="card-sub">지금 가입하고 인디게임의 세계를 탐험해보세요.</p>

      <form @submit.prevent="handleRegister" class="register-form" novalidate>

        <!-- 이름 -->
        <div class="field-wrap" :class="{ error: errors.username }">
          <label class="field-label">이름 <span class="req">필수</span></label>
          <div class="input-row">
            <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
            </svg>
            <input
              v-model="form.username"
              type="text"
              placeholder="성함"
              autocomplete="username"
              @blur="validateField('username')"
              @input="clearError('username')"
            />
          </div>
          <span class="field-msg" v-if="errors.username">{{ errors.username }}</span>
        </div>

        <!-- 닉네임 -->
        <div class="field-wrap" :class="{ error: errors.nickname }">
          <label class="field-label">닉네임 <span class="req">필수</span></label>
          <div class="input-row">
            <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 6h.008v.008H6V6Z" />
            </svg>
            <input
              v-model="form.nickname"
              type="text"
              placeholder="게임에서 사용할 닉네임"
              autocomplete="nickname"
              @blur="validateField('nickname')"
              @input="clearError('nickname')"
            />
          </div>
          <span class="field-msg" v-if="errors.nickname">{{ errors.nickname }}</span>
          <span class="field-msg success" v-else-if="touched.nickname && form.nickname">사용 가능한 닉네임이에요</span>
        </div>

        <!-- 이메일 -->
        <div class="field-wrap" :class="{ error: errors.email }">
          <label class="field-label">이메일 <span class="req">필수</span></label>
          <div class="input-row">
            <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
            </svg>
            <input
              v-model="form.email"
              type="email"
              placeholder="your@email.com"
              autocomplete="email"
              @blur="validateField('email')"
              @input="clearError('email')"
            />
          </div>
          <span class="field-msg" v-if="errors.email">{{ errors.email }}</span>
        </div>

        <!-- 비밀번호 -->
        <div class="field-wrap" :class="{ error: errors.password }">
          <label class="field-label">비밀번호 <span class="req">필수</span></label>
          <div class="input-row">
            <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
            </svg>
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="8자 이상"
              autocomplete="new-password"
              @blur="validateField('password')"
              @input="clearError('password')"
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

        <!-- 비밀번호 확인 -->
        <div class="field-wrap" :class="{ error: errors.passwordConfirm }">
          <label class="field-label">비밀번호 확인 <span class="req">필수</span></label>
          <div class="input-row">
            <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
            </svg>
            <input
              v-model="form.passwordConfirm"
              type="password"
              placeholder="비밀번호 재입력"
              autocomplete="new-password"
              @blur="validateField('passwordConfirm')"
              @input="clearError('passwordConfirm')"
            />
          </div>
          <span class="field-msg" v-if="errors.passwordConfirm">{{ errors.passwordConfirm }}</span>
          <span class="field-msg success" v-else-if="touched.passwordConfirm && form.passwordConfirm && form.password === form.passwordConfirm">비밀번호가 일치해요</span>
        </div>

        <!-- 생년월일 -->
        <div class="field-wrap" :class="{ error: errors.birth_date }">
          <label class="field-label">생년월일 <span class="req">필수</span></label>
          <div class="birth-row">
            <div class="input-row birth-first">
              <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5" />
              </svg>
              <select v-model="birthYear" @change="syncBirthDate" class="select-input">
                <option value="">년</option>
                <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}년</option>
              </select>
            </div>
            <div class="input-row">
              <select v-model="birthMonth" @change="syncBirthDate" class="select-input">
                <option value="">월</option>
                <option v-for="m in 12" :key="m" :value="String(m).padStart(2,'0')">{{ m }}월</option>
              </select>
            </div>
            <div class="input-row">
              <select v-model="birthDay" @change="syncBirthDate" class="select-input">
                <option value="">일</option>
                <option v-for="d in dayOptions" :key="d" :value="String(d).padStart(2,'0')">{{ d }}일</option>
              </select>
            </div>
          </div>
          <span class="field-msg" v-if="errors.birth_date">{{ errors.birth_date }}</span>
        </div>

        <!-- 이용약관 -->
        <div class="field-wrap">
          <label class="check-label">
            <input type="checkbox" v-model="form.agreed" />
            <span class="custom-check"></span>
            <span>이용약관 및 개인정보처리방침에 동의합니다</span>
          </label>
          <span class="field-msg" v-if="errors.agreed">{{ errors.agreed }}</span>
        </div>

        <div class="error-banner" v-if="apiError">{{ apiError }}</div>

        <button type="submit" class="btn-submit" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          <span v-else>가입하기</span>
        </button>

      </form>

      <router-link to="/login" class="btn-login-link">이미 계정이 있으신가요?</router-link>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI, accountAPI } from '@/api/services'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  nickname: '',
  email: '',
  password: '',
  passwordConfirm: '',
  birth_date: '',
  agreed: false,
})

const errors = reactive({})
const touched = reactive({})
const showPassword = ref(false)
const isLoading = ref(false)
const apiError = ref('')

const birthYear  = ref('')
const birthMonth = ref('')
const birthDay   = ref('')

const currentYear = new Date().getFullYear()
const minYear = currentYear - 100
const maxYear = currentYear

const yearOptions = computed(() => {
  const arr = []
  for (let y = maxYear; y >= minYear; y--) arr.push(y)
  return arr
})

const dayOptions = computed(() => {
  if (!birthYear.value || !birthMonth.value) return Array.from({ length: 31 }, (_, i) => i + 1)
  const days = new Date(Number(birthYear.value), Number(birthMonth.value), 0).getDate()
  return Array.from({ length: days }, (_, i) => i + 1)
})

function syncBirthDate() {
  if (birthYear.value && birthMonth.value && birthDay.value) {
    form.birth_date = `${birthYear.value}-${birthMonth.value}-${birthDay.value}`
  } else {
    form.birth_date = ''
  }
  validateField('birth_date')
}

const rules = {
  username: (v) => {
    if (!v) return '이름을 입력해주세요'
    if (v.length < 2) return '이름은 2자 이상이어야 해요'
    return ''
  },
  nickname: (v) => {
    if (!v) return '닉네임을 입력해주세요'
    if (v.length < 2) return '닉네임은 2자 이상이어야 해요'
    if (v.length > 50) return '닉네임은 50자 이하로 입력해주세요'
    return ''
  },
  email: (v) => {
    if (!v) return '이메일을 입력해주세요'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return '올바른 이메일 형식이 아니에요'
    return ''
  },
  password: (v) => {
    if (!v) return '비밀번호를 입력해주세요'
    if (v.length < 8) return '비밀번호는 8자 이상이어야 해요'
    return ''
  },
  passwordConfirm: (v) => {
    if (!v) return '비밀번호 확인을 입력해주세요'
    if (v !== form.password) return '비밀번호가 일치하지 않아요'
    return ''
  },
  birth_date: (v) => {
    if (!v) return '생년월일을 입력해주세요'
    return ''
  },
  agreed: (v) => {
    if (!v) return '이용약관에 동의해주세요'
    return ''
  },
}

const validateField = (field) => {
  touched[field] = true
  const msg = rules[field]?.(form[field]) ?? ''
  if (msg) errors[field] = msg
  else delete errors[field]
  return !msg
}

const clearError = (field) => {
  delete errors[field]
}

const validateAll = () => {
  return ['username', 'nickname', 'email', 'password', 'passwordConfirm', 'birth_date', 'agreed']
    .map(validateField)
    .every(Boolean)
}

const handleRegister = async () => {
  apiError.value = ''
  if (!validateAll()) return

  isLoading.value = true
  try {
    const { data } = await authAPI.register({
      username: form.username,
      nickname: form.nickname,
      email: form.email,
      password1: form.password,
      password2: form.passwordConfirm,
      ...(form.birth_date ? { birth_date: form.birth_date } : {}),
    })
    const token = data.key
    localStorage.setItem('token', token)
    const meRes = await accountAPI.getMe()
    authStore.login(meRes.data, token)
    router.push({ name: 'home' })
  } catch (err) {
    const data = err?.response?.data
    const first = data && Object.values(data)[0]
    apiError.value = Array.isArray(first) ? first[0] : (first ?? '회원가입 중 오류가 발생했어요. 다시 시도해주세요.')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* ── 페이지 레이아웃 ── */
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  position: relative;
  padding: 48px 0;
  background: #FFF7E6;
}

.page-bg {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: left top;
  pointer-events: none;
  user-select: none;
}

/* ── 카드 ── */
.register-card {
  position: relative;
  z-index: 10;
  background: rgba(255, 253, 247, 0.96);
  border-radius: 24px;
  padding: 44px 44px;
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
  margin: 0 0 24px;
}

/* ── 폼 ── */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 12px;
}

.field-wrap {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field-label {
  font-size: 12px;
  font-weight: 600;
  color: #6B5A45;
}

.req {
  font-size: 11px;
  font-weight: 400;
  color: #9e9585;
  margin-left: 2px;
}

/* ── 인풋 행 ── */
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
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: #9e9585;
  margin-left: 13px;
}

.input-row input {
  flex: 1;
  padding: 12px 12px;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #3A2410;
  outline: none;
  font-family: inherit;
}

.input-row input::placeholder { color: #b0a090; }

/* ── 비밀번호 토글 ── */
.toggle-pw {
  background: none;
  border: none;
  padding: 0 13px;
  cursor: pointer;
  color: #9e9585;
  display: flex;
  align-items: center;
}
.toggle-pw:hover { color: #3A2410; }
.toggle-pw svg { width: 17px; height: 17px; }

/* ── 생년월일 ── */
.birth-row {
  display: flex;
  gap: 8px;
}

.birth-row .input-row { flex: 1; }
.birth-first { flex: 1.4 !important; }

.select-input {
  flex: 1;
  padding: 12px 8px 12px 4px;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #3A2410;
  outline: none;
  font-family: inherit;
  cursor: pointer;
  appearance: none;
  min-width: 0;
}

.select-input option { color: #3A2410; }

/* ── 메시지 ── */
.field-msg {
  font-size: 12px;
  color: #e53e3e;
  padding-left: 4px;
}

.field-msg.success { color: #38a169; }

/* ── 체크박스 ── */
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
  background: #fff;
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
.btn-submit {
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
.btn-submit:hover:not(:disabled) { background: #B45309; }
.btn-submit:active:not(:disabled) { transform: scale(0.99); }
.btn-submit:disabled { background: #e8c07a; cursor: not-allowed; }

.btn-login-link {
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
  transition: background 0.15s;
  margin-top: 10px;
  box-sizing: border-box;
  font-family: inherit;
}
.btn-login-link:hover { background: #FFF0D6; }

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
  .register-card {
    margin-right: 40px;
    width: 420px;
    padding: 40px 36px;
  }
}

@media (max-width: 600px) {
  .register-page {
    justify-content: center;
    padding: 40px 0;
  }
  .register-card {
    margin: 0 16px;
    width: 100%;
    max-width: 460px;
    border-radius: 20px;
    padding: 36px 28px;
  }
}
</style>
