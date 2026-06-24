<template>
  <section class="section-card">
    <div class="section-header">
      <h3 class="section-title">작성한 글</h3>
      <RouterLink to="/community?my=1" class="view-all">커뮤니티 가기 &rsaquo;</RouterLink>
    </div>

    <div v-if="posts.length === 0" class="empty">
      아직 작성한 글이 없어요.
    </div>

    <ul v-else class="post-list">
      <li v-for="post in posts" :key="post.id" class="post-item">
        <RouterLink :to="`/community/${post.id}`" class="post-link">
          <span class="category-badge" :class="categoryClass(post.category)">
            {{ post.category }}
          </span>
          <span class="post-title">{{ post.title }}</span>
          <span class="post-meta">
            <span class="post-date">{{ formatDate(post.created_at) }}</span>
            <span class="post-comments">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 2c-2.236 0-4.43.18-6.57.524C1.993 2.755 1 4.014 1 5.426v5.148c0 1.413.993 2.67 2.43 2.902.848.137 1.705.248 2.57.331v3.443a.75.75 0 0 0 1.28.53l3.58-3.579a.78.78 0 0 1 .527-.224 41.202 41.202 0 0 0 5.183-.5c1.437-.232 2.43-1.49 2.43-2.903V5.426c0-1.413-.993-2.67-2.43-2.902A41.289 41.289 0 0 0 10 2Zm0 7a1 1 0 1 0 0-2 1 1 0 0 0 0 2ZM8 9a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm5 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clip-rule="evenodd"/>
              </svg>
              {{ post.comment_count }}
            </span>
          </span>
        </RouterLink>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  posts: { type: Array, default: () => [] },
})

const CATEGORY_CLASS = {
  '공략': 'badge-guide',
  '자유': 'badge-free',
  '파티원모집': 'badge-party',
}

function categoryClass(cat) {
  return CATEGORY_CLASS[cat] ?? 'badge-free'
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\. /g, '.').replace(/\.$/, '')
}
</script>

<style scoped>
.section-card {
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 16px;
  padding: 24px 28px;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1510;
  margin: 0;
}
.view-all {
  font-size: 13px;
  color: #6b6256;
  text-decoration: none;
}
.view-all:hover { color: #1e3a5f; }

.empty {
  font-size: 14px;
  color: #9e9585;
  text-align: center;
  padding: 24px 0;
}

.post-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}
.post-item + .post-item {
  border-top: 1px solid #f0ece3;
}
.post-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 0;
  text-decoration: none;
  color: inherit;
  transition: background 0.1s;
}
.post-link:hover .post-title {
  color: #1e3a5f;
}

.category-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
  white-space: nowrap;
  flex-shrink: 0;
}
.badge-guide  { background: #e8f0fe; color: #1e3a5f; }
.badge-free   { background: #f0ece3; color: #6b6256; }
.badge-party  { background: #fef3e2; color: #92400e; }

.post-title {
  flex: 1;
  font-size: 14px;
  color: #1a1510;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}
.post-date {
  font-size: 12px;
  color: #9e9585;
  white-space: nowrap;
}
.post-comments {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #9e9585;
}
.post-comments svg {
  width: 14px;
  height: 14px;
}
</style>
