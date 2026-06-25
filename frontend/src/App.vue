<template>
  <div class="app">
    <img
      v-show="compassVisible"
      :src="compassImg"
      class="compass-follower"
      :style="{ left: compassX + 'px', top: compassY + 'px' }"
      alt=""
    />
    <nav class="nav">
      <div class="nav-left">
        <RouterLink :to="{ name: 'home' }" class="logo-wrap">
          <img src="@/assets/logo.png" alt="방구석 탐험대" class="logo" />
        </RouterLink>
        <a class="nav-link" :class="{ 'router-link-active': $route.name === 'explore' }" @click="handleExploreClick">게임 라이브러리</a>
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
            @input="suggestTrigger($event.target.value)"
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
          <RouterLink :to="{ name: 'login' }" class="btn btn-outline">로그인</RouterLink>
          <RouterLink :to="{ name: 'register' }" class="btn btn-primary">회원가입</RouterLink>
        </template>
      </div>
    </nav>

    <RouterView />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useExploreStore } from '@/stores/explore'
import { accountAPI } from '@/api/services'
import defaultAvatar from '@/assets/profile.png'
import { useGameSuggest } from '@/composables/useGameSuggest'
import GameSuggestDropdown from '@/components/common/GameSuggestDropdown.vue'
import NotificationBubble from '@/components/common/NotificationBubble.vue'
import compassImg from '@/assets/나침반.png'
import mouseImg from '@/assets/마우스.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const exploreStore = useExploreStore()

const compassX = ref(0)
const compassY = ref(0)
const compassVisible = ref(false)

function onMouseMove(e) {
  compassX.value = e.clientX + 39
  compassY.value = e.clientY + 28
  compassVisible.value = true
}

function handleExploreClick() {
  exploreStore.requestReset()
  if (route.name !== 'explore') {
    router.push({ name: 'explore' })
  }
}

const navSearchRef = ref(null)
const keyword = ref('')
const { suggestions, activeIdx, trigger: suggestTrigger, onKeydown: suggestKeydown, clear: suggestClear } = useGameSuggest()

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
  document.addEventListener('mousemove', onMouseMove)
  const cursorStyle = document.createElement('style')
  cursorStyle.id = 'custom-cursor-style'
  cursorStyle.textContent = `* { cursor: url(${mouseImg}) 0 0, auto !important; }`
  document.head.appendChild(cursorStyle)
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
  document.removeEventListener('mousemove', onMouseMove)
  document.getElementById('custom-cursor-style')?.remove()
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #FFF7E6;
  font-family: 'Pretendard', sans-serif;
}

.compass-follower {
  position: fixed;
  width: 48px;
  height: 48px;
  pointer-events: none;
  z-index: 9999;
  transform: translate(-50%, -50%);
  user-select: none;
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 80px;
  background: #FFF7E6;
  border-bottom: 1px solid #D8C4A3;
  position: sticky;
  top: 0;
  z-index: 100;
  gap: 16px;
  min-width: 0;
  font-family: 'Pretendard', sans-serif;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 40px;
  flex-shrink: 0;
}

.logo-wrap {
  display: flex;
  align-items: center;
}

.logo {
  height: 65px;
  width: auto;
  object-fit: contain;
}

.nav-link {
  text-decoration: none;
  color: #3A2410;
  font-size: 16px;
  font-weight: 700;
  white-space: nowrap;
  transition: color 0.15s;
  font-family: 'Pretendard', sans-serif;
}
.nav-link:hover,
.nav-link.router-link-active {
  color: #D97706;
}

.nav-search {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  max-width: 300px;
}

.search-icon {
  position: absolute;
  left: 14px;
  width: 16px;
  color: #6B5A45;
  pointer-events: none;
}

.nav-search input {
  width: 100%;
  min-width: 120px;
  padding: 9px 16px 9px 38px;
  border-radius: 999px;
  border: 1px solid #D8C4A3;
  background: #FFFDF7;
  font-size: 14px;
  color: #2F2418;
  outline: none;
  transition: border-color 0.15s, background 0.15s;
  font-family: 'Pretendard', sans-serif;
}
.nav-search input:focus {
  border-color: #D97706;
  background: #fff;
}
.nav-search input::placeholder {
  color: #6B5A45;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.icon-btn {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #3A2410;
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
  border: 2px solid #D8C4A3;
  transition: border-color 0.15s;
}
.profile-link:hover .nav-avatar {
  border-color: #D97706;
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
  font-family: 'Pretendard', sans-serif;
}
.btn-outline {
  border: 1px solid #D8C4A3;
  color: #3A2410;
  background: transparent;
}
.btn-outline:hover {
  border-color: #D97706;
  color: #D97706;
}
.btn-primary {
  background: #D97706;
  color: #fff;
}
.btn-primary:hover {
  background: #B45309;
}
</style>