<template>
  <div class="app">
    <nav class="nav">
      <div class="nav-left">
        <RouterLink :to="{ name: 'home' }" class="logo-wrap">
          <img src="@/assets/logo.png" alt="방구석 탐험대" class="logo" />
        </RouterLink>
        <RouterLink :to="{ name: 'explore' }" class="nav-link">게임 라이브러리</RouterLink>
        <RouterLink :to="{ name: 'home' }" class="nav-link">커뮤니티</RouterLink>
      </div>

      

      <div class="nav-right">
        <form class="nav-search" @submit.prevent="onSearch">
        <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none"
          viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
        </svg>
        <input v-model="keyword" type="text" placeholder="게임 검색" />
      </form>
        <button class="icon-btn" @click="openNotifications">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
          </svg>
          <span v-if="notifCount" class="notif-badge">{{ notifCount }}</span>
        </button>

        <template v-if="authStore.isLoggedIn">
          <RouterLink to="/profile" class="nav-link profile-link">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
              stroke-width="1.5" stroke="currentColor" width="20" height="20">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
            </svg>
            프로필
          </RouterLink>
          <button class="btn btn-outline" @click="authStore.logout">로그아웃</button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="nav-link">프로필</RouterLink>
          <RouterLink to="/login" class="btn btn-outline">로그인</RouterLink>
          <RouterLink to="/signup" class="btn btn-primary">회원가입</RouterLink>
        </template>
      </div>
    </nav>

    <RouterView />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const keyword = ref('')
const notifCount = ref('')

function onSearch() {
  if (keyword.value.trim()) {
    router.push({ name: 'search', query: { q: keyword.value } })
  }
}

function openNotifications() {
  // TODO: 알림 패널 열기
}
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
}

.logo-wrap {
  display: flex;
  align-items: center;
}

.logo {
  width: 52px;
  height: 52px;
  object-fit: contain;
  border-radius: 50%;
}

.nav-link {
  text-decoration: none;
  color: #3d3529;
  font-size: 14px;
  font-weight: 500;
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
  gap: 4px;
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