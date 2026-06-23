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

        <!-- ── 게임 소개 ── -->
        <GameDescription :description="game.description" />

        <!-- ── 공략·스트리밍 영상 ── -->
        <GameVideos :game-id="game.id" :videos="game.videos" />

        <!-- ── 관련 커뮤니티 글 ── -->
        <GameCommunityPosts :game-id="game.id" :posts="game.posts" />
      </template>

    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import GameMediaGallery from '@/components/game-detail/GameMediaGallery.vue'
import GameInfoPanel from '@/components/game-detail/GameInfoPanel.vue'
import GameDescription from '@/components/game-detail/GameDescription.vue'
import GameVideos from '@/components/game-detail/GameVideos.vue'
import GameCommunityPosts from '@/components/game-detail/GameCommunityPosts.vue'

const route = useRoute()
const loading = ref(true)
const game = ref({})

// ── 더미 데이터 (백엔드 연결 전) ──────────────────────────
const DUMMY_GAME = {
  id: 1,
  title: '엔더릴리즈: 기사의 고요',
  platform: 'PC · Steam',
  release_status: '출시됨',
  initial_price: 19800,
  final_price: 13860,
  discount_rate: 30,
  metacritic_score: 85,
  supports_korean: true,
  required_age: 12,
  is_online: false,
  capsule_url: '',   // 실제 이미지 URL로 교체
  screenshots: [
    { id: 1, url: '', label: '대표' },
    { id: 2, url: '', label: '스크린샷 1' },
    { id: 3, url: '', label: '스크린샷 2' },
    { id: 4, url: '', label: '스크린샷 3' },
    { id: 5, url: '', label: '영상 썸네일' },
  ],
  genres: [
    { id: 1, name: '액션' },
    { id: 2, name: '메트로바니아' },
    { id: 3, name: '소울라이크' },
    { id: 4, name: '인디' },
  ],
  description: `엔더릴리즈는 아름답고 황폐한 세계를 배경으로 한 2D 액션 RPG입니다.
기사 라스트의 조력을 받아 저주받은 왕국을 탐험하세요. 강력한 보스들을 쓰러뜨리고, 숨겨진 비밀을 밝혀내세요.

섬세하게 그려진 손 그림 애니메이션과 잔잔한 피아노 선율이 어우러져 깊은 감동을 선사합니다.`,
  is_wishlisted: false,
  videos: [
    { id: 1, title: '엔더릴리즈 공략 1화', video_url: 'https://youtube.com', thumbnail_url: '', channel: '인디게임TV', views: '12.4만', uploaded_at: '2024.03.10' },
    { id: 2, title: '보스 공략 완전정복',   video_url: 'https://youtube.com', thumbnail_url: '', channel: '게임왕',    views: '8.2만',  uploaded_at: '2024.03.08' },
    { id: 3, title: '스트리머 첫 플레이',   video_url: 'https://youtube.com', thumbnail_url: '', channel: '탐험단TV',  views: '5.7만',  uploaded_at: '2024.03.05' },
  ],
  posts: [
    { id: 1, title: '엔더릴리즈 숨겨진 보스 공략 총정리', author: '탐험가123', comments: 12, likes: 24, created_at: '3일 전' },
    { id: 2, title: '처음 하는 분들을 위한 입문 가이드',  author: '인디고수',   comments: 8,  likes: 31, created_at: '3일 전' },
    { id: 3, title: '이 게임 진짜 갓겜임 후기',          author: '방구석탐험대', comments: 20, likes: 47, created_at: '3일 전' },
  ],
}
// ────────────────────────────────────────────────────────

onMounted(async () => {
  const gameId = route.params.id
  try {
    // TODO: 백엔드 연결 시 아래 주석 해제
    // const res = await fetch(`/api/games/${gameId}/`)
    // game.value = await res.json()

    // 더미 데이터 사용 (딜레이로 로딩 시뮬레이션)
    await new Promise(r => setTimeout(r, 600))
    game.value = { ...DUMMY_GAME, id: gameId }
  } catch (e) {
    console.error('게임 상세 로드 실패:', e)
  } finally {
    loading.value = false
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