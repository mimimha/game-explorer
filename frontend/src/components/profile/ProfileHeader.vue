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
          <button v-if="isOwner" class="btn-edit" @click="$emit('editProfile')">프로필 수정</button>

          <!-- 타인: 팔로우/언팔로우 -->
          <button v-else class="btn-follow" :class="{ following: isFollowing }" @click="$emit('followToggle')">
            {{ isFollowing ? '언팔로우' : '팔로우' }}
          </button>

          <button class="btn-follow-stat" @click="$emit('showFollowers')">
            팔로워 <strong>{{ user.follower_count ?? 0 }}</strong>
          </button>
          <button class="btn-follow-stat" @click="$emit('showFollowing')">
            팔로잉 <strong>{{ user.following_count ?? 0 }}</strong>
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
  width: 88px;
  height: 88px;
  border-radius: 50%;
  overflow: hidden;
  background: #f0ece3;
  border: 2px solid #e8e4d9;
}
.avatar img { width: 100%; height: 100%; object-fit: cover; }

.avatar-edit-btn {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #1e3a5f;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 2px solid #fff;
}
.avatar-edit-btn svg { width: 13px; height: 13px; }
.hidden-input { display: none; }

/* Profile info */
.profile-info { flex: 1; min-width: 0; }
.name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.nickname { font-size: 20px; font-weight: 700; color: #1a1510; margin: 0; }
.level-badge {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: #1e3a5f;
  border-radius: 999px;
  padding: 2px 10px;
}

.email {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b6256;
  margin: 0 0 6px;
}
.email-icon { width: 14px; height: 14px; flex-shrink: 0; }

.action-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.btn-edit {
  font-size: 13px;
  font-weight: 600;
  color: #1a1510;
  background: #fff;
  border: 1px solid #c8c2b4;
  border-radius: 8px;
  padding: 6px 14px;
  cursor: pointer;
  transition: background 0.15s;
}
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
  font-size: 13px;
  color: #6b6256;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}
.btn-follow-stat strong { color: #1a1510; font-weight: 700; margin-left: 3px; }

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
