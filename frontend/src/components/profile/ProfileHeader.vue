<template>
  <section class="profile-card">
    <div class="profile-main">
      <!-- Avatar -->
      <div class="avatar-wrap">
        <div class="avatar">
          <img :src="user.profile_img || defaultAvatar" alt="프로필 이미지" />
        </div>
        <!-- 본인만 카메라 아이콘 표시 -->
        <label v-if="isOwner" class="avatar-edit-btn" title="프로필 사진 변경">
          <input type="file" accept="image/*" class="hidden-input" @change="onAvatarChange" />
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/>
            <path fill-rule="evenodd" d="M9.344 3.071a49.52 49.52 0 0 1 5.312 0c.967.052 1.83.585 2.332 1.39l.821 1.317c.24.383.645.643 1.11.71.386.054.77.113 1.152.177 1.432.239 2.429 1.493 2.429 2.909V18a3 3 0 0 1-3 3h-15a3 3 0 0 1-3-3V9.574c0-1.416.997-2.67 2.429-2.909.382-.064.766-.123 1.151-.178a1.56 1.56 0 0 0 1.11-.71l.822-1.315a2.942 2.942 0 0 1 2.332-1.39ZM6.75 12.75a5.25 5.25 0 1 1 10.5 0 5.25 5.25 0 0 1-10.5 0Zm12-1.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" clip-rule="evenodd"/>
          </svg>
        </label>
      </div>

      <!-- Info -->
      <div class="profile-info">
        <div class="name-row">
          <h2 class="nickname">{{ user.nickname || user.username }}</h2>
          <span class="rank-badge" :class="rankBadge.cls">{{ rankBadge.icon }} {{ rankBadge.label }}</span>
        </div>

        <!-- 이메일은 본인만 표시 -->
        <p v-if="isOwner" class="email">
          <svg viewBox="0 0 20 20" fill="currentColor" class="email-icon">
            <path d="M3 4a2 2 0 0 0-2 2v1.161l8.441 4.221a1.25 1.25 0 0 0 1.118 0L19 7.162V6a2 2 0 0 0-2-2H3Z"/>
            <path d="m19 8.839-7.77 3.885a2.75 2.75 0 0 1-2.46 0L1 8.839V14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V8.839Z"/>
          </svg>
          {{ user.email }}
        </p>

        <div class="action-row">
          <!-- 본인: 프로필 수정 -->
          <button v-if="isOwner" class="btn-edit" @click="$emit('editProfile')">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path fill-rule="evenodd" d="M7.5 6a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM3.751 20.105a8.25 8.25 0 0 1 16.498 0 .75.75 0 0 1-.437.695A18.683 18.683 0 0 1 12 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 0 1-.437-.695Z" clip-rule="evenodd" />
            </svg>
            프로필 수정
          </button>

          <!-- 타인: 팔로우/언팔로우 -->
          <button v-else class="btn-follow" :class="{ following: isFollowing }" @click="$emit('followToggle')">
            {{ isFollowing ? '언팔로우' : '팔로우' }}
          </button>

          <button class="btn-follow-stat" @click="$emit('showFollowers')">
            <div class="stat-left">
              <span class="stat-count">{{ user.follower_count ?? 0 }}</span>
              <span class="stat-label">팔로워</span>
            </div>
            <svg class="stat-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M4.5 6.375a4.125 4.125 0 1 1 8.25 0 4.125 4.125 0 0 1-8.25 0ZM14.25 8.625a3.375 3.375 0 1 1 6.75 0 3.375 3.375 0 0 1-6.75 0ZM1.5 19.125a7.125 7.125 0 0 1 14.25 0v.003l-.001.119a.75.75 0 0 1-.363.63 13.067 13.067 0 0 1-6.761 1.873c-2.472 0-4.786-.684-6.76-1.873a.75.75 0 0 1-.364-.63l-.001-.122ZM17.25 19.128l-.001.144a2.25 2.25 0 0 1-.233.96 10.088 10.088 0 0 0 5.06-1.01.75.75 0 0 0 .42-.643 4.875 4.875 0 0 0-6.957-4.611 8.586 8.586 0 0 1 1.71 5.157v.003Z" />
            </svg>
          </button>
          <button class="btn-follow-stat" @click="$emit('showFollowing')">
            <div class="stat-left">
              <span class="stat-count">{{ user.following_count ?? 0 }}</span>
              <span class="stat-label">팔로잉</span>
            </div>
            <svg class="stat-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path fill-rule="evenodd" d="M7.5 6a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM3.751 20.105a8.25 8.25 0 0 1 16.498 0 .75.75 0 0 1-.437.695A18.683 18.683 0 0 1 12 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 0 1-.437-.695Z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import defaultAvatar from '@/assets/profile.png'

const props = defineProps({
  user: { type: Object, default: () => ({}) },
  counts: { type: Object, default: () => ({ wishlist: 0, posts: 0, comments: 0, medals: 0 }) },
  isOwner: { type: Boolean, default: true },
  isFollowing: { type: Boolean, default: false },
})

const emit = defineEmits(['editProfile', 'showFollowers', 'showFollowing', 'avatarChanged', 'followToggle'])

const isBirthday = computed(() => {
  if (!props.user.birth_date) return false
  const today = new Date()
  const bd = new Date(props.user.birth_date)
  return today.getMonth() === bd.getMonth() && today.getDate() === bd.getDate()
})

const rankBadge = computed(() => {
  const medals = props.counts?.medals ?? 0
  if (medals >= 7) return { icon: '👑', label: '탐험 마스터', cls: 'rank-master' }
  if (medals >= 3) return { icon: '🧭', label: '숙련 탐험가', cls: 'rank-skilled' }
  return { icon: '🌱', label: '초보 탐험가', cls: 'rank-beginner' }
})

function onAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  emit('avatarChanged', file)
}
</script>

<style scoped>
.profile-card {
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 16px;
  padding: 28px 32px;
}
.profile-main {
  display: flex;
  align-items: flex-start;
  gap: 24px;
}

/* Avatar */
.avatar-wrap { position: relative; flex-shrink: 0; }
.avatar {
  width: 130px;
  height: 130px;
  border-radius: 50%;
  overflow: hidden;
  background: #f0ece3;
  border: 2px solid #e8e4d9;
}
.avatar img { width: 100%; height: 100%; object-fit: cover; }

.avatar-edit-btn {
  position: absolute;
  bottom: 5px;
  right: 2px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #1e3a5f;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 2px solid #fff;
}
.avatar-edit-btn svg { width: 16px; height: 16px; }
.hidden-input { display: none; }

/* Profile info */
.profile-info { flex: 1; min-width: 0; }
.name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.nickname { font-size: 20px; font-weight: 700; color: #1a1510; margin: 0; margin-left: 8px;}

.email {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b6256;
  margin: 0 0 6px;
  margin-left: 8px;
}
.email-icon { width: 14px; height: 14px; flex-shrink: 0; }

.action-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 40px;
  margin-left: 8px;
  flex-wrap: wrap;
}

.btn-edit {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #1a1510;
  background: #fff;
  border: 1px solid #c8c2b4;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-edit svg { width: 15px; height: 15px; flex-shrink: 0; color: #6b6256; }
.btn-edit:hover { background: #f0ece3; }

.btn-follow {
  font-size: 13px;
  font-weight: 600;
  padding: 6px 18px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid #1e3a5f;
  background: #1e3a5f;
  color: #fff;
}
.btn-follow.following {
  background: #fff;
  color: #1e3a5f;
}
.btn-follow:hover { opacity: 0.85; }

.btn-follow-stat {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: #f5f3ef;
  border: 1px solid #e8e4d9;
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.15s;
  min-width: 100px;
}
.btn-follow-stat:hover { background: #ede9e0; }
.btn-follow-stat .stat-left { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; }
.btn-follow-stat .stat-count { font-size: 18px; font-weight: 700; color: #3a6b4a; line-height: 1; }
.btn-follow-stat .stat-label { font-size: 11px; color: #6b6256; }
.btn-follow-stat .stat-icon { width: 22px; height: 22px; color: #c8c2b4; flex-shrink: 0; }

/* Rank badge */
.rank-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
}
.rank-beginner { background: #e8f5e9; color: #2e7d32; }
.rank-skilled  { background: #e3f0ff; color: #1e4e8c; }
.rank-master   { background: #fff8e1; color: #b8860b; }

/* Birthday card */
.birthday-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #f0f5ff;
  border: 1px solid #c7d8f5;
  border-radius: 12px;
  padding: 16px 20px;
  min-width: 220px;
  flex-shrink: 0;
}
.birthday-icon-wrap { width: 36px; height: 36px; flex-shrink: 0; }
.birthday-icon-wrap svg { width: 100%; height: 100%; }
.birthday-title { font-size: 14px; font-weight: 700; color: #1e3a5f; margin: 0 0 2px; }
.birthday-sub { font-size: 12px; color: #5a7ab5; margin: 0; }
</style>
