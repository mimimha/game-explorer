<template>
  <div class="auth-wrapper">
    <div class="auth-card">

      <div class="auth-header">
        <div class="logo">🎮 방구석 탐험대</div>
        <h1>회원가입</h1>
        <p>인디게임의 세계에 오신 걸 환영해요</p>
      </div>

      <form @submit.prevent="handleRegister" class="auth-form" novalidate>

        <div class="form-group" :class="{ error: errors.username, success: touched.username && !errors.username }">
          <label for="username">이름</label>
          <input
            id="username"
            v-model="form.username"
            placeholder="성함"
            type="text"
            autocomplete="username"
            @blur="validateField('username')"
            @input="clearError('username')"
          />
          <span class="field-msg" v-if="errors.username">{{ errors.username }}</span>
        </div>

        <div class="form-group" :class="{ error: errors.nickname, success: touched.nickname && !errors.nickname }">
          <label for="nickname">닉네임</label>
          <input
            id="nickname"
            v-model="form.nickname"
            type="text"
            placeholder="게임에서 사용할 닉네임"
            autocomplete="nickname"
            @blur="validateField('nickname')"
            @input="clearError('nickname')"
          />
          <span class="field-msg" v-if="errors.nickname">{{ errors.nickname }}</span>
          <span class="field-msg success" v-else-if="touched.nickname && form.nickname">사용 가능한 닉네임이에요</span>
        </div>

        <div class="form-group" :class="{ error: errors.email, success: touched.email && !errors.email }">
          <label for="email">이메일</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="your@email.com"
            autocomplete="email"
            @blur="validateField('email')"
            @input="clearError('email')"
          />
          <span class="field-msg" v-if="errors.email">{{ errors.email }}</span>
        </div>

        <div class="form-group" :class="{ error: errors.password, success: touched.password && !errors.password }">
          <label for="password">비밀번호</label>
          <div class="input-with-toggle">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="8자 이상"
              autocomplete="new-password"
              @blur="validateField('password')"
              @input="clearError('password')"
            />
            <button type="button" class="toggle-pw" @click="showPassword = !showPassword" tabindex="-1">
              {{ showPassword ? '숨기기' : '보기' }}
            </button>
          </div>
      
          <span class="field-msg" v-if="errors.password">{{ errors.password }}</span>
        </div>

        <div class="form-group" :class="{ error: errors.passwordConfirm, success: touched.passwordConfirm && !errors.passwordConfirm }">
          <label for="passwordConfirm">비밀번호 확인</label>
          <input
            id="passwordConfirm"
            v-model="form.passwordConfirm"
            type="password"
            placeholder="비밀번호 재입력"
            autocomplete="new-password"
            @blur="validateField('passwordConfirm')"
            @input="clearError('passwordConfirm')"
          />
          <span class="field-msg" v-if="errors.passwordConfirm">{{ errors.passwordConfirm }}</span>
          <span class="field-msg success" v-else-if="touched.passwordConfirm && form.passwordConfirm && form.password === form.passwordConfirm">비밀번호가 일치해요</span>
        </div>

        <div class="form-group" :class="{ error: errors.birth_date }">
          <label for="birth_date">생년월일</label>
          <input
            id="birth_date"
            v-model="form.birth_date"
            type="date"
            :max="maxDate"
            @blur="validateField('birth_date')"
          />
          <span class="field-msg" v-if="errors.birth_date">{{ errors.birth_date }}</span>
        </div>

        <div class="form-group terms-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="form.agreed" />
            <span class="custom-check"></span>
            <span>이용약관 및 개인정보처리방침에 동의합니다</span>
          </label>
          <span class="field-msg" v-if="errors.agreed">{{ errors.agreed }}</span>
        </div>

        <div class="form-error-banner" v-if="apiError">{{ apiError }}</div>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          <span v-else>가입하기</span>
        </button>

      </form>

      <div class="auth-footer">
        이미 계정이 있으신가요?
        <router-link to="/login">로그인</router-link>
      </div>

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

const maxDate = computed(() => {
  const d = new Date()
  d.setFullYear(d.getFullYear() - 14)
  return d.toISOString().split('T')[0]
})



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

label {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

input[type="text"],
input[type="email"],
input[type="password"],
input[type="date"] {
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

.form-group.success input {
  border-color: #38a169;
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

/* ── 메시지 ── */
.field-msg {
  font-size: 12px;
  color: #e53e3e;
}

.field-msg.success {
  color: #38a169;
}

/* ── 체크박스 ── */
.terms-group { gap: 8px; }

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 13px;
  color: #444;
  font-weight: 400;
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
