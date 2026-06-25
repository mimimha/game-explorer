<template>
  <main class="game-detail">
    <div class="inner">

      <!-- 브레드크럼 -->
      <nav class="breadcrumb">
        <RouterLink to="/">홈</RouterLink>
        <span class="sep">›</span>
        <RouterLink :to="{ name: 'explore' }">게임 목록</RouterLink>
        <span class="sep">›</span>
        <span class="current">{{ game.title }}</span>
      </nav>

      <!-- 로딩 -->
      <div v-if="loading" class="loading-wrap">
        <div class="dots-state">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>

      <template v-else>
        <!-- ── 상단: 미디어 + 게임 정보 ── -->
        <div class="top-section">
          <GameMediaGallery :capsule-url="game.capsule_url" :screenshots="game.screenshots" />
          <GameInfoPanel :game="game" />
        </div>

        <!-- ── 게임 소개 (한글 번역 우선) ── -->
        <GameDescription :description-ko="game.description_ko" :description="game.description" />

        <!-- ── 공략·스트리밍 영상 ── -->
        <GameVideos :game-id="game.id" :videos="game.videos" :loading="videosLoading" />

        <!-- ── 관련 커뮤니티 글 ── -->
        <!-- <GameCommunityPosts :game-id="game.id" :posts="game.posts" /> -->
      </template>

    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { onBeforeRouteLeave } from 'vue-router'
import { gameAPI } from '@/api/services'
import { useExploreStore } from '@/stores/explore'
import GameMediaGallery from '@/components/game-detail/GameMediaGallery.vue'
import GameInfoPanel from '@/components/game-detail/GameInfoPanel.vue'
import GameDescription from '@/components/game-detail/GameDescription.vue'
import GameVideos from '@/components/game-detail/GameVideos.vue'
import GameCommunityPosts from '@/components/game-detail/GameCommunityPosts.vue'

const route = useRoute()
const router = useRouter()
const exploreStore = useExploreStore()
const loading = ref(true)
const videosLoading = ref(false)
const game = ref({})

onBeforeRouteLeave((to) => {
  if (to.name !== 'explore' && to.name !== 'game-detail') {
    exploreStore.clear()
  }
})

// 백엔드 상세 응답 → 화면 컴포넌트가 기대하는 형태로 변환
function mapGame(d) {
  const init = Number(d.initial_price)
  const final = Number(d.final_price)
  const discount = (init && final && init > final)
    ? Math.round((1 - final / init) * 100)
    : 0
  return {
    ...d,
    // 정보 패널용 파생 필드
    platform: (d.platforms || []).map(p => p.name).slice(0, 2).join(' · ') || '플랫폼 미상',
    discount_rate: discount,
    supports_korean: d.is_korean,
    is_online: !d.offline,
    release_status: d.release_date ? '출시됨' : '미정',
    description: d.description || '',          // 원문(EN) — 폴백용
    description_ko: d.description_ko || '',    // 한글 번역(우선 표시)
    // 갤러리용: image_url → url, 라벨 부여
    screenshots: (d.screenshots || []).map((s, i) => ({
      id: s.id,
      url: s.image_url,
      label: `스크린샷 ${i + 1}`,
    })),
    // 영상: thumbnail → thumbnail_url, published_at → uploaded_at (channel 은 그대로)
    videos: (d.videos || []).map(v => ({
      ...v,
      thumbnail_url: v.thumbnail || '',
      uploaded_at: v.published_at || '',
    })),
    posts: [],
  }
}

onMounted(async () => {
  const gameId = route.params.id
  try {
    const { data } = await gameAPI.detail(gameId)
    game.value = mapGame(data)
  } catch (e) {
    router.replace({ name: 'error' })
    return
  } finally {
    loading.value = false
  }

  // 영상은 상세와 분리해 '비동기'로 불러온다 → 상세 화면은 위에서 이미 즉시 표시됨.
  // 상세 응답에 영상이 이미 있으면(DB에 있던 게임) 추가 호출하지 않는다.
  if (!game.value.videos?.length) {
    videosLoading.value = true
    try {
      const { data } = await gameAPI.videos(gameId)   // 없으면 백엔드가 lazy로 채워 반환
      game.value.videos = (data || []).map(v => ({
        ...v,
        thumbnail_url: v.thumbnail || '',
        uploaded_at: v.published_at || '',
      }))
    } catch {
      // 실패 시 영상 없음 상태 유지(상세 페이지는 정상)
    } finally {
      videosLoading.value = false
    }
  }
})
</script>

<style scoped>
.game-detail {
  background: #fafaf8;
  min-height: 100vh;
  padding: 24px 0 80px;
}
.inner {
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 40px;
}

/* 브레드크럼 */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  margin-bottom: 24px;
}
.breadcrumb a {
  color: #6b6256;
  text-decoration: none;
  transition: color 0.15s;
}
.breadcrumb a:hover { color: #1e3a5f; }
.sep { color: #c8c2b4; }
.current { color: #1a1510; font-weight: 600; }

/* 상단 레이아웃 */
.top-section {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 32px;
  margin-bottom: 24px;
}

/* 로딩 */
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 120px 0;
}
.dots-state {
  display: flex;
  align-items: center;
  gap: 10px;
}
.dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  background: #1e3a5f;
  opacity: 0;
  animation: dot-pop 1.2s ease-in-out infinite;
}
.dot:nth-child(1) { animation-delay: 0s; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes dot-pop {
  0%, 80%, 100% { opacity: 0; transform: scale(0.6); }
  40%           { opacity: 1; transform: scale(1); }
}
</style>