<template>
  <div class="app">
    <nav class="nav">
      <div class="nav-left">
        <RouterLink :to="{ name: 'home' }" class="logo-wrap">
          <img src="@/assets/logo.png" alt="방구석 탐험대" class="logo" />
        </RouterLink>
        <RouterLink :to="{ name: 'explore' }" class="nav-link">게임 라이브러리</RouterLink>
        <RouterLink :to="{ name: 'community' }" class="nav-link">커뮤니티</RouterLink>
      </div>

      

      <div class="nav-right">
        <form ref="navSearchRef" class="nav-search" @submit.prevent="onSearch" role="search">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none"
            viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
          <input
            v-model="keyword"
            type="text"
            placeholder="게임 검색"
            autocomplete="off"
            @keydown="(e) => suggestKeydown(e, onSelectSuggestion, onSearch)"
          />
          <GameSuggestDropdown
            :suggestions="suggestions"
            :active-idx="activeIdx"
            @select="onSelectSuggestion"
            @hover="onNavSuggestHover"
          />
        </form>
        <NotificationBubble v-if="authStore.isLoggedIn" />

        <template v-if="authStore.isLoggedIn">
          <RouterLink to="/profile" class="nav-link profile-link">
            <img
              :src="authStore.user?.profile_img || defaultAvatar"
              class="nav-avatar"
              alt="프로필"
            />
          </RouterLink>
          <button class="btn btn-outline" @click="handleLogout">로그아웃</button>
        </template>
        <template v-else>
          <RouterLink :to="{ name: 'Login' }" class="btn btn-outline">로그인</RouterLink>
          <RouterLink :to="{ name: 'Register' }" class="btn btn-primary">회원가입</RouterLink>
        </template>
      </div>
    </nav>

    <RouterView />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { accountAPI } from '@/api/services'
import defaultAvatar from '@/assets/profile.png'
import { useGameSuggest } from '@/composables/useGameSuggest'
import GameSuggestDropdown from '@/components/common/GameSuggestDropdown.vue'
import NotificationBubble from '@/components/common/NotificationBubble.vue'

const router = useRouter()
const authStore = useAuthStore()

const navSearchRef = ref(null)
const keyword = ref('')
const { suggestions, activeIdx, onKeydown: suggestKeydown, clear: suggestClear } = useGameSuggest(keyword)

function onNavSuggestHover(i) { activeIdx.value = i }

function onNavDocumentClick(e) {
  if (navSearchRef.value && !navSearchRef.value.contains(e.target)) {
    suggestClear()
  }
}

function handleLogout() {
  authStore.logout()
  router.push({ name: 'home' })
}

function onSelectSuggestion(s) {
  keyword.value = ''
  suggestClear()
  router.push({ name: 'explore', query: { q: s.title_ko || s.title } })
}

function onSearch() {
  const q = keyword.value.trim()
  suggestClear()
  if (!q) return
  keyword.value = ''
  router.push({ name: 'explore', query: { q } })
}

// 새로고침 후 profile_img 복원
onMounted(async () => {
  document.addEventListener('mousedown', onNavDocumentClick)
  if (authStore.isLoggedIn && !authStore.user?.profile_img) {
    try {
      const { data } = await accountAPI.getMe()
      authStore.setProfile(data)
    } catch {
      // 인증 만료 등은 인터셉터가 처리
    }
  }
})

onUnmounted(() => {
  document.removeEventListener('mousedown', onNavDocumentClick)
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #fafaf8;
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 64px;
  background: #ffffff;
  border-bottom: 1px solid #e8e4d9;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 28px;
  margin-bottom: 10px;
}

.logo-wrap {
  display: flex;
  align-items: center;
}

.logo {
  width: 110px;
  height: 110%;
  object-fit: contain;
  border-radius: 50%;
}

.nav-link {
  text-decoration: none;
  color: #3d3529;
  font-size: 19px;
  font-weight: 700;
  transition: color 0.15s;
}
.nav-link:hover,
.nav-link.router-link-active {
  color: #1e3a5f;
}

.nav-search {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 14px;
  width: 16px;
  color: #9e9585;
  pointer-events: none;
}

.nav-search input {
  width: 300px;
  padding: 9px 16px 9px 38px;
  border-radius: 999px;
  border: 1px solid #ddd8cc;
  background: #f7f5f0;
  font-size: 14px;
  color: #3d3529;
  outline: none;
  transition: border-color 0.15s, background 0.15s;
}
.nav-search input:focus {
  border-color: #1e3a5f;
  background: #fff;
}
.nav-search input::placeholder {
  color: #9e9585;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-btn {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #3d3529;
  display: flex;
  align-items: center;
}
.icon-btn svg {
  width: 22px;
}

.notif-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #c0392b;
  color: white;
  font-size: 10px;
  font-weight: 700;
  border-radius: 999px;
  min-width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.profile-link {
  display: flex;
  align-items: center;
}

.nav-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e8e4d9;
  transition: border-color 0.15s;
}
.profile-link:hover .nav-avatar {
  border-color: #1e3a5f;
}

.btn {
  padding: 8px 18px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
}
.btn-outline {
  border: 1px solid #c8c2b4;
  color: #3d3529;
  background: transparent;
}
.btn-outline:hover {
  border-color: #1e3a5f;
  color: #1e3a5f;
}
.btn-primary {
  background: #1e3a5f;
  color: white;
}
.btn-primary:hover {
  background: #162d4a;
}
</style>