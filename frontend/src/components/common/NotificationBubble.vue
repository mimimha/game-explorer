<template>
  <div class="notif-wrap" ref="wrapRef">
    <!-- 종 버튼 -->
    <button class="icon-btn" :class="{ active: isOpen }" @click="toggle" aria-label="알림">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
        stroke-width="1.5" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
      </svg>
      <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
    </button>

    <!-- 말풍선 -->
    <Transition name="bubble">
      <div v-if="isOpen" class="bubble">
        <div class="bubble-arrow" />

        <!-- 헤더 -->
        <div class="bubble-header">
          <span class="bubble-title">알림</span>
          <button v-if="unreadCount > 0" class="mark-all-btn" @click="markAllRead">
            모두 읽음
          </button>
        </div>

        <!-- 목록 -->
        <div class="bubble-body">
          <div v-if="loading" class="bubble-state">불러오는 중…</div>
          <div v-else-if="pagedItems.length === 0" class="bubble-state">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
              stroke-width="1.5" stroke="currentColor" class="empty-icon">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
            </svg>
            <p>알림이 없어요</p>
          </div>
          <template v-else>
            <div
              v-for="n in pagedItems"
              :key="n.id"
              class="notif-item"
              :class="{ unread: !n.is_read }"
              @click="onNotifClick(n)"
            >
              <span class="notif-type-icon">{{ typeIcon(n.notif_type) }}</span>
              <div class="notif-content">
                <p class="notif-msg">{{ n.message }}</p>
                <span class="notif-time">{{ timeAgo(n.created_at) }}</span>
              </div>
            </div>
          </template>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="totalPages > 1" class="bubble-pagination">
          <button class="page-arrow" :disabled="page === 1" @click="page--">‹</button>
          <span class="page-label">{{ page }} / {{ totalPages }}</span>
          <button class="page-arrow" :disabled="page === totalPages" @click="page++">›</button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { notificationAPI } from '@/api/services'

const router = useRouter()

const PER_PAGE = 5

const wrapRef = ref(null)
const isOpen = ref(false)
const loading = ref(false)
const items = ref([])
const page = ref(1)

const unreadCount = computed(() => items.value.filter(n => !n.is_read).length)

const totalPages = computed(() => Math.ceil(items.value.length / PER_PAGE) || 1)

const pagedItems = computed(() => {
  const start = (page.value - 1) * PER_PAGE
  return items.value.slice(start, start + PER_PAGE)
})

watch(isOpen, (val) => {
  if (val) fetchNotifications()
})

watch(totalPages, (tp) => {
  if (page.value > tp) page.value = tp
})

async function fetchNotifications() {
  loading.value = true
  try {
    const { data } = await notificationAPI.list()
    items.value = Array.isArray(data) ? data : (data.results ?? [])
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

async function onNotifClick(n) {
  // 읽음 처리
  if (!n.is_read) {
    try {
      await notificationAPI.read(n.id)
      n.is_read = true
    } catch { /* ignore */ }
  }
  // 타입별 라우팅
  const route = resolveRoute(n)
  if (route) {
    isOpen.value = false
    router.push(route)
  }
}

function resolveRoute(n) {
  switch (n.notif_type) {
    case 'follow':
      return n.actor_id ? { name: 'user-profile', params: { userId: n.actor_id } } : null
    case 'new_post':
      return n.target_id ? { name: 'post-detail', params: { postId: n.target_id } } : null
    case 'new_wishlist':
      return n.target_id ? { name: 'game-detail', params: { id: n.target_id } } : null
    case 'medal':
      return { name: 'profile' }
    default:
      return null
  }
}

async function markAllRead() {
  try {
    await notificationAPI.readAll()
    items.value.forEach(n => { n.is_read = true })
  } catch { /* ignore */ }
}

function toggle() {
  isOpen.value = !isOpen.value
  page.value = 1
}

function onDocClick(e) {
  if (wrapRef.value && !wrapRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

function typeIcon(type) {
  const map = {
    follow: '👤',
    new_post: '📝',
    new_wishlist: '🎮',
    medal: '🏅',
  }
  return map[type] ?? '🔔'
}

function timeAgo(isoStr) {
  const diff = Date.now() - new Date(isoStr).getTime()
  const min = Math.floor(diff / 60000)
  if (min < 1) return '방금 전'
  if (min < 60) return `${min}분 전`
  const hr = Math.floor(min / 60)
  if (hr < 24) return `${hr}시간 전`
  const day = Math.floor(hr / 24)
  if (day < 7) return `${day}일 전`
  return new Date(isoStr).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
}

// 앱 마운트 시 unread 수 미리 파악
async function initCount() {
  try {
    const { data } = await notificationAPI.list()
    items.value = Array.isArray(data) ? data : (data.results ?? [])
  } catch { /* ignore */ }
}

defineExpose({ initCount })

onMounted(() => {
  document.addEventListener('mousedown', onDocClick)
  initCount()
})
onUnmounted(() => {
  document.removeEventListener('mousedown', onDocClick)
})
</script>

<style scoped>
.notif-wrap {
  position: relative;
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
  transition: color 0.15s;
}
.icon-btn svg { width: 25px; }
.icon-btn:hover { color: #D97706; }
.icon-btn.active { color: #D97706; }

.notif-badge {
  position: absolute;
  bottom: 0px;
  right: 0px;
  background: #c0392b;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  border-radius: 50%;
  width: 15px;
  height: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1;
}

/* 말풍선 */
.bubble {
  position: absolute;
  top: calc(100% + 14px);
  right: -8px;
  width: 320px;
  background: #FFFDF7;
  border: 1px solid #D8C4A3;
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(58,36,16,0.13);
  z-index: 300;
  overflow: hidden;
}

/* 말풍선 꼬리 (위쪽 화살표) */
.bubble-arrow {
  position: absolute;
  top: -8px;
  right: 16px;
  width: 14px;
  height: 14px;
  background: #FFFDF7;
  border-left: 1px solid #D8C4A3;
  border-top: 1px solid #D8C4A3;
  transform: rotate(45deg);
  border-radius: 2px 0 0 0;
}

.bubble-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 10px;
  border-bottom: 1px solid #FFF0D6;
}
.bubble-title {
  font-size: 14px;
  font-weight: 700;
  color: #3A2410;
}
.mark-all-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: #D97706;
  cursor: pointer;
  font-family: inherit;
  font-weight: 600;
}
.mark-all-btn:hover { text-decoration: underline; }

.bubble-body {
  min-height: 60px;
  max-height: 300px;
  overflow-y: auto;
}

.bubble-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px 16px;
  color: #6B5A45;
  font-size: 13px;
}
.empty-icon { width: 28px; color: #D8C4A3; }

.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 11px 16px;
  border-bottom: 1px solid #FFF0D6;
  cursor: pointer;
  transition: background 0.12s;
}
.notif-item:last-child { border-bottom: none; }
.notif-item:hover { background: #FFF7E6; }
.notif-item.unread { background: #FFF0D6; }
.notif-item.unread:hover { background: #ffe4b0; }

.notif-type-icon {
  font-size: 18px;
  flex-shrink: 0;
  line-height: 1;
  margin-top: 1px;
}

.notif-content { flex: 1; min-width: 0; }
.notif-msg {
  font-size: 13px;
  color: #3A2410;
  line-height: 1.45;
  margin: 0 0 3px;
  word-break: keep-all;
}
.notif-time {
  font-size: 11px;
  color: #6B5A45;
}

/* 페이지네이션 */
.bubble-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 10px 16px;
  border-top: 1px solid #FFF0D6;
}
.page-arrow {
  background: none;
  border: 1px solid #D8C4A3;
  border-radius: 6px;
  width: 28px;
  height: 28px;
  font-size: 16px;
  cursor: pointer;
  color: #3A2410;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.12s;
}
.page-arrow:hover:not(:disabled) { border-color: #D97706; color: #D97706; }
.page-arrow:disabled { color: #c8c2b4; cursor: default; }
.page-label { font-size: 12px; color: #6B5A45; font-weight: 600; }

/* 말풍선 등장 애니메이션 */
.bubble-enter-active { transition: opacity 0.15s, transform 0.15s; }
.bubble-leave-active { transition: opacity 0.1s, transform 0.1s; }
.bubble-enter-from { opacity: 0; transform: translateY(-6px); }
.bubble-leave-to   { opacity: 0; transform: translateY(-4px); }
</style>
