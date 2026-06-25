<template>
  <section class="posts-section">
    <div class="section-header">
      <div class="header-left">
        <h2 class="section-title">관련 커뮤니티 글</h2>
        <span class="game-id-label">POST (game_id 연동)</span>
      </div>
    </div>
    <p class="section-sub">이 게임을 다룬 게시글 목록</p>

    <div class="post-list">
      <RouterLink
        v-for="post in posts"
        :key="post.id"
        :to="`/community/posts/${post.id}`"
        class="post-item"
      >
        <!-- 썸네일 자리 -->
        <div class="post-thumb">
          <svg viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg">
            <rect width="56" height="56" fill="#e8e2d5"/>
            <line x1="0" y1="0" x2="56" y2="56" stroke="#c8c2b4" stroke-width="1"/>
            <line x1="56" y1="0" x2="0" y2="56" stroke="#c8c2b4" stroke-width="1"/>
          </svg>
        </div>

        <div class="post-body">
          <p class="post-title">{{ post.title }}</p>
          <p class="post-meta">
            {{ post.author }}
            <span class="sep">·</span> 댓글 {{ post.comments }}
            <span class="sep">·</span> 추천 {{ post.likes }}
            <span class="sep">·</span> {{ post.created_at }}
          </p>
        </div>

        <svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" width="14" class="chevron">
          <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>
        </svg>
      </RouterLink>

      <!-- 더미 (데이터 없을 때) -->
      <template v-if="!posts.length">
        <div v-for="i in 3" :key="i" class="post-item skeleton">
          <div class="post-thumb sk-thumb"></div>
          <div class="post-body">
            <div class="sk-line w70"></div>
            <div class="sk-line w40"></div>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  gameId: { type: [String, Number], default: null },
  posts:  { type: Array, default: () => [] },
})
</script>

<style scoped>
.posts-section {
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 14px;
  padding: 28px 32px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 4px;
}
.header-left { display: flex; align-items: baseline; gap: 10px; }
.section-title { font-size: 18px; font-weight: 800; color: #1a1510; margin: 0; }
.game-id-label {
  font-size: 11px;
  font-weight: 600;
  color: #9e9585;
  background: #f0ece3;
  border-radius: 4px;
  padding: 2px 6px;
}
.section-sub { font-size: 13px; color: #9e9585; margin: 0 0 20px; }

/* 게시글 목록 */
.post-list { display: flex; flex-direction: column; gap: 8px; }

.post-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border: 1px solid #e8e4d9;
  border-radius: 10px;
  text-decoration: none;
  color: inherit;
  background: #fff;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.post-item:hover {
  border-color: #1e3a5f;
  box-shadow: 0 2px 8px rgba(30,58,95,0.07);
}

.post-thumb {
  width: 52px; height: 52px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: #e8e2d5;
}
.post-thumb svg { width: 100%; height: 100%; display: block; }

.post-body { flex: 1; min-width: 0; }
.post-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1510;
  margin: 0 0 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.post-meta {
  font-size: 12px;
  color: #9e9585;
  margin: 0;
}
.sep { margin: 0 4px; }

.chevron { color: #c8c2b4; flex-shrink: 0; }

/* 스켈레톤 */
.sk-thumb {
  background: linear-gradient(90deg, #f0ece3 25%, #e8e2d5 50%, #f0ece3 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
.sk-line {
  height: 12px;
  background: linear-gradient(90deg, #f0ece3 25%, #e8e2d5 50%, #f0ece3 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: 999px;
  margin-bottom: 8px;
}
.w70 { width: 70%; }
.w40 { width: 40%; }
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>