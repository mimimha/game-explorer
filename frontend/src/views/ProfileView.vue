<template>
  <div class="page-wrap">
    <!-- Breadcrumb -->
    <nav class="breadcrumb">
      <RouterLink to="/">홈</RouterLink>
      <span class="sep">&rsaquo;</span>
      <span>{{ isOwner ? '마이페이지' : '프로필' }}</span>
    </nav>

    <header class="page-header">
      <h1 class="page-title">{{ isOwner ? '마이페이지' : '프로필' }}</h1>
      <p v-if="isOwner" class="page-sub">당신의 활동과 취향을 한눈에 확인하세요.</p>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner" />
      <p>프로필을 불러오는 중...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchAll">다시 시도</button>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Birthday Banner -->
      <div v-if="isBirthday" class="birthday-banner">
        🎂 오늘은 <strong>{{ user.nickname }}</strong>님의 생일이에요! 생일을 진심으로 축하합니다! 🎉
      </div>

      <ProfileHeader
        :user="user"
        :counts="mypage.counts"
        :is-owner="isOwner"
        :is-following="isFollowing"
        @edit-profile="openEditModal"
        @avatar-changed="handleAvatarChange"
        @show-followers="showFollowers"
        @show-following="showFollowing"
        @follow-toggle="handleFollowToggle"
      />

      <ProfileStats :counts="mypage.counts" />

      <MedalSection :medals="mypage.medals" />

      <MyPostsSection :posts="mypage.recent_posts" />

      <WishlistSection :games="mypage.recent_wishlist" />

      <AiHistorySection :logs="recentLogs" />
    </template>

    <!-- Confetti Canvas -->
    <Teleport to="body">
      <canvas v-if="showConfetti" ref="confettiCanvas" class="confetti-canvas" />
    </Teleport>

    <!-- Follow List Modal -->
    <Teleport to="body">
      <div v-if="followModalOpen" class="modal-overlay" @click.self="closeFollowModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ followModalTitle }}</h2>
            <button class="modal-close" @click="closeFollowModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div v-if="followListLoading" class="follow-loading">불러오는 중...</div>
          <ul v-else-if="followList.length" class="follow-list">
            <li v-for="u in followList" :key="u.id" class="follow-item" @click="goToProfile(u.id)">
              <img :src="u.profile_img || defaultFollowAvatar" class="follow-avatar" alt="" />
              <span class="follow-nickname">{{ u.nickname }}</span>
              <svg class="follow-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
              </svg>
            </li>
          </ul>
          <p v-else class="follow-empty">아직 {{ followModalTitle }}가 없어요.</p>
        </div>
      </div>
    </Teleport>

    <!-- Edit Profile Modal (본인만) -->
    <Teleport to="body">
      <div v-if="editModalOpen" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal">
          <div class="modal-header">
            <h2>프로필 수정</h2>
            <button class="modal-close" @click="closeEditModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <form class="modal-form" @submit.prevent="submitEdit">
            <div class="form-field">
              <label>닉네임</label>
              <input v-model="editForm.nickname" type="text" placeholder="닉네임" maxlength="50" />
            </div>
            <div class="form-field">
              <label>생년월일</label>
              <input v-model="editForm.birth_date" type="date" :max="new Date().toISOString().slice(0, 10)" />
            </div>
            <div class="modal-actions">
              <button type="button" class="btn-cancel" @click="closeEditModal">취소</button>
              <button type="submit" class="btn-save" :disabled="saving">
                {{ saving ? '저장 중...' : '저장' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { accountAPI, recommendAPI } from '@/api/services'
import { useAuthStore } from '@/stores/auth'
import defaultFollowAvatar from '@/assets/profile.png'

import ProfileHeader from '@/components/profile/ProfileHeader.vue'
import ProfileStats from '@/components/profile/ProfileStats.vue'
import MedalSection from '@/components/profile/MedalSection.vue'
import MyPostsSection from '@/components/profile/MyPostsSection.vue'
import WishlistSection from '@/components/profile/WishlistSection.vue'
import AiHistorySection from '@/components/profile/AiHistorySection.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// /profile = 본인, /users/:userId 이지만 자기 자신 ID인 경우도 본인으로 처리
const isOwner = computed(() => {
  if (!route.params.userId) return true
  return String(route.params.userId) === String(authStore.user?.id)
})

const loading = ref(true)
const error = ref(null)
const saving = ref(false)
const editModalOpen = ref(false)
const isFollowing = ref(false)

const followModalOpen = ref(false)
const followModalTitle = ref('')
const followList = ref([])
const followListLoading = ref(false)

const user = ref({})
const mypage = reactive({
  counts: { wishlist: 0, posts: 0, comments: 0, medals: 0 },
  medals: [],
  recent_posts: [],
  recent_wishlist: [],
})
const recentLogs = ref([])

const editForm = reactive({ nickname: '', birth_date: '' })

// ── Birthday & Confetti ──────────────────────────────────────────────────────
const CONFETTI_COLORS = [
  '#ff6b6b', '#ffa94d', '#ffd43b', '#69db7c',
  '#74c0fc', '#9775fa', '#f783ac', '#a9e34b',
]

const confettiCanvas = ref(null)
const showConfetti = ref(false)
let animFrame = null

const isBirthday = computed(() => {
  const bd = user.value?.birth_date
  if (!bd) return false
  const [, m, d] = bd.split('-').map(Number)
  const now = new Date()
  return now.getMonth() + 1 === m && now.getDate() === d
})

function makeParticle(w, h) {
  return {
    x: Math.random() * w,
    y: -(Math.random() * h * 0.6),
    size: Math.random() * 10 + 5,
    vx: (Math.random() - 0.5) * 3,
    vy: Math.random() * 2.5 + 1.5,
    rot: Math.random() * 360,
    rotV: (Math.random() - 0.5) * 8,
    color: CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)],
    circle: Math.random() < 0.35,
  }
}

function startConfetti() {
  if (showConfetti.value) return
  showConfetti.value = true
  nextTick(() => {
    const canvas = confettiCanvas.value
    if (!canvas) return
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    const ctx = canvas.getContext('2d')
    const particles = Array.from({ length: 160 }, () => makeParticle(canvas.width, canvas.height))
    const start = Date.now()
    const TOTAL = 7000

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const elapsed = Date.now() - start
      if (elapsed >= TOTAL) { showConfetti.value = false; return }
      const alpha = elapsed > TOTAL * 0.65
        ? 1 - (elapsed - TOTAL * 0.65) / (TOTAL * 0.35)
        : 1

      for (const p of particles) {
        p.x += p.vx
        p.y += p.vy
        p.rot += p.rotV
        if (p.y > canvas.height && elapsed < TOTAL * 0.55) {
          p.y = -p.size
          p.x = Math.random() * canvas.width
        }
        ctx.save()
        ctx.globalAlpha = alpha
        ctx.translate(p.x, p.y)
        ctx.rotate(p.rot * Math.PI / 180)
        ctx.fillStyle = p.color
        if (p.circle) {
          ctx.beginPath()
          ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2)
          ctx.fill()
        } else {
          ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2)
        }
        ctx.restore()
      }
      animFrame = requestAnimationFrame(draw)
    }
    draw()
  })
}

onBeforeUnmount(() => {
  if (animFrame) cancelAnimationFrame(animFrame)
})

watch(loading, (v) => {
  if (!v && isBirthday.value) nextTick(startConfetti)
})

async function fetchAll() {
  loading.value = true
  error.value = null

  try {
    if (isOwner.value) {
      if (!authStore.isLoggedIn) { router.push('/login'); return }
      const [meRes, mypageRes, logsRes] = await Promise.all([
        accountAPI.getMe(),
        accountAPI.getMypage(),
        recommendAPI.logs(),
      ])
      user.value = meRes.data
      Object.assign(mypage, mypageRes.data)
      recentLogs.value = (logsRes.data?.results ?? logsRes.data ?? []).slice(0, 3)
    } else {
      // 타인 공개 프로필 — 백엔드가 counts·posts·wishlist·logs 모두 반환
      const res = await accountAPI.getUserProfile(route.params.userId)
      const d = res.data
      user.value = {
        id: d.id,
        nickname: d.nickname,
        profile_img: d.profile_img,
        birth_date: d.birth_date ?? null,
        follower_count: d.follower_count,
        following_count: d.following_count,
      }
      isFollowing.value = d.is_following ?? false
      mypage.medals = d.medals ?? []
      mypage.counts = d.counts ?? { wishlist: 0, posts: 0, comments: 0, medals: 0 }
      mypage.recent_posts = d.recent_posts ?? []
      mypage.recent_wishlist = d.recent_wishlist ?? []
      recentLogs.value = d.recent_logs ?? []
    }
  } catch (e) {
    if (e.response?.status === 401) {
      router.push('/login')
    } else if (e.response?.status === 404) {
      error.value = '존재하지 않는 사용자예요.'
    } else {
      error.value = '데이터를 불러오는 데 실패했어요. 잠시 후 다시 시도해주세요.'
    }
  } finally {
    loading.value = false
  }
}

// 라우트 파라미터 변경 시 재조회
watch(() => route.params.userId, fetchAll)

async function handleFollowToggle() {
  if (!authStore.isLoggedIn) { router.push('/login'); return }
  try {
    if (isFollowing.value) {
      const res = await accountAPI.unfollow(user.value.id)
      isFollowing.value = res.data.is_following
      user.value = { ...user.value, follower_count: res.data.follower_count }
    } else {
      const res = await accountAPI.follow(user.value.id)
      isFollowing.value = res.data.is_following
      user.value = { ...user.value, follower_count: res.data.follower_count }
    }
  } catch {
    alert('팔로우 처리 중 오류가 발생했어요.')
  }
}

function openEditModal() {
  editForm.nickname = user.value.nickname || ''
  editForm.birth_date = user.value.birth_date || ''
  editModalOpen.value = true
}
function closeEditModal() { editModalOpen.value = false }

async function submitEdit() {
  saving.value = true
  try {
    const res = await accountAPI.updateMe({
      nickname: editForm.nickname,
      birth_date: editForm.birth_date || null,
    })
    user.value = res.data
    authStore.setProfile(res.data)
    const medalsRes = await accountAPI.getMyMedals()
    mypage.medals = medalsRes.data?.results ?? medalsRes.data ?? []
    closeEditModal()
  } catch {
    alert('프로필 수정에 실패했어요.')
  } finally {
    saving.value = false
  }
}

async function handleAvatarChange(file) {
  const formData = new FormData()
  formData.append('profile_img', file)
  try {
    const res = await accountAPI.updateMe(formData)
    user.value = res.data
    authStore.setProfile(res.data)
  } catch {
    alert('프로필 사진 변경에 실패했어요.')
  }
}

async function openFollowModal(type) {
  const targetId = isOwner.value ? authStore.user?.id : route.params.userId
  followModalTitle.value = type === 'followers' ? '팔로워' : '팔로잉'
  followModalOpen.value = true
  followListLoading.value = true
  followList.value = []
  try {
    const res = type === 'followers'
      ? await accountAPI.getFollowers(targetId)
      : await accountAPI.getFollowing(targetId)
    followList.value = res.data
  } catch {
    followList.value = []
  } finally {
    followListLoading.value = false
  }
}
function closeFollowModal() { followModalOpen.value = false }
function goToProfile(userId) {
  closeFollowModal()
  router.push(`/users/${userId}`)
}

function showFollowers() { openFollowModal('followers') }
function showFollowing() { openFollowModal('following') }

onMounted(fetchAll)
</script>

<style scoped>
.page-wrap {
  max-width: 860px;
  margin: 0 auto;
  padding: 32px 24px 64px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #9e9585;
}
.breadcrumb a { color: #9e9585; text-decoration: none; }
.breadcrumb a:hover { color: #1e3a5f; }
.sep { font-size: 12px; }

.page-header { margin-bottom: 4px; }
.page-title {
  font-size: 26px;
  font-weight: 800;
  color: #1a1510;
  margin: 0 0 6px;
}
.page-sub { font-size: 14px; color: #9e9585; margin: 0; }

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 16px;
  color: #9e9585;
  font-size: 14px;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e8e4d9;
  border-top-color: #1e3a5f;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.error-state button {
  padding: 8px 20px;
  background: #1e3a5f;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(26,21,16,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.modal {
  background: #fff;
  border-radius: 16px;
  padding: 28px 32px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.modal-header h2 { font-size: 18px; font-weight: 700; color: #1a1510; margin: 0; }
.modal-close { background: none; border: none; cursor: pointer; color: #9e9585; padding: 4px; }
.modal-close svg { width: 20px; height: 20px; }
.modal-form { display: flex; flex-direction: column; gap: 18px; }
.form-field { display: flex; flex-direction: column; gap: 6px; }
.form-field label { font-size: 13px; font-weight: 600; color: #6b6256; }
.form-field input {
  border: 1px solid #e8e4d9;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  color: #1a1510;
  outline: none;
  transition: border-color 0.15s;
}
.form-field input:focus { border-color: #1e3a5f; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 8px; }
.btn-cancel {
  padding: 9px 20px;
  border: 1px solid #e8e4d9;
  border-radius: 8px;
  background: #fff;
  color: #6b6256;
  font-size: 14px;
  cursor: pointer;
}
.btn-save {
  padding: 9px 20px;
  border: none;
  border-radius: 8px;
  background: #1e3a5f;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

.follow-loading {
  text-align: center;
  padding: 32px 0;
  color: #9e9585;
  font-size: 14px;
}
.follow-list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 360px;
  overflow-y: auto;
}
.follow-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 4px;
  border-bottom: 1px solid #f0ece3;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.12s;
}
.follow-item:last-child { border-bottom: none; }
.follow-item:hover { background: #f5f3ef; }
.follow-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e8e4d9;
  flex-shrink: 0;
}
.follow-nickname { flex: 1; font-size: 14px; font-weight: 600; color: #1a1510; }
.follow-arrow { width: 16px; height: 16px; color: #c8c2b4; flex-shrink: 0; }
.follow-empty {
  text-align: center;
  padding: 32px 0;
  color: #9e9585;
  font-size: 14px;
}

.birthday-banner {
  background: linear-gradient(135deg, #fff9db, #fff0f6);
  border: 1.5px solid #fcc2d7;
  border-radius: 12px;
  padding: 14px 20px;
  text-align: center;
  font-size: 15px;
  color: #c92a2a;
  animation: birthday-pulse 2s ease-in-out infinite;
}
@keyframes birthday-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(252, 194, 215, 0.5); }
  50%       { box-shadow: 0 0 0 8px rgba(252, 194, 215, 0); }
}

.confetti-canvas {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
}
</style>
