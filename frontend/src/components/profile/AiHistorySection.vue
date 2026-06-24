<template>
  <section class="section-card">
    <div class="section-header">
      <h3 class="section-title">AI 추천 기록</h3>

    </div>

    <div v-if="logs.length === 0" class="empty">
      아직 AI 추천 기록이 없어요.
    </div>

    <ul v-else class="log-list">
      <li v-for="log in logs" :key="log.log_id" class="log-item">
        <RouterLink :to="`/explore?log=${log.log_id}`" class="log-link">
          <div class="log-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" stroke="#6b6256" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="log-prompt">{{ log.prompt_input }}</span>
          <span class="log-date">{{ formatDate(log.created_at) }}</span>
        </RouterLink>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  logs: { type: Array, default: () => [] },
})

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

.log-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}
.log-item + .log-item {
  border-top: 1px solid #f0ece3;
}
.log-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  text-decoration: none;
  color: inherit;
}
.log-link:hover .log-prompt {
  color: #1e3a5f;
}

.log-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #f0ece3;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.log-icon svg {
  width: 18px;
  height: 18px;
}

.log-prompt {
  flex: 1;
  font-size: 14px;
  color: #1a1510;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}
.log-date {
  font-size: 12px;
  color: #9e9585;
  flex-shrink: 0;
}
</style>
