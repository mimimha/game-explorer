<template>
  <aside class="info-panel">

    <!-- 플랫폼 · 출시일 -->
    <div class="badges">
      <span class="badge">{{ game.platform }}</span>
      <template v-if="releaseDateFormatted">
        <span class="dot-sep">·</span>
        <span class="badge badge--date">
          <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.5" style="vertical-align:-2px;margin-right:3px">
            <rect x="1" y="2.5" width="14" height="12" rx="2"/>
            <line x1="1" y1="6.5" x2="15" y2="6.5"/>
            <line x1="5" y1="1" x2="5" y2="4"/>
            <line x1="11" y1="1" x2="11" y2="4"/>
          </svg>
          {{ releaseDateFormatted }}
        </span>
      </template>
    </div>

    <!-- 제목 -->
    <h1 class="title">
      {{ game.title }}
      <br>
      <span v-if="game.title_ko" class="title-ko">({{ game.title_ko }})</span>
    </h1>

    <!-- 가격 -->
    <div class="price-row">
      <template v-if="game.final_price != null">
        <template v-if="game.discount_rate && game.final_price > 0">
          <span class="price-original">{{ formatPrice(game.initial_price) }}</span>
          <span class="arrow-icon">→</span>
          <span class="price-final">{{ formatPrice(game.final_price) }}</span>
          <span class="discount-badge">-{{ game.discount_rate }}% 할인</span>
        </template>
        <span v-else class="price-final">{{ formatPrice(game.final_price) }}</span>
      </template>
      <span v-else class="coming-soon">추후 업데이트 예정</span>
    </div>

    <!-- 메타크리틱 점수 + 별점 -->
    <div class="score-row">
      <template v-if="game.metacritic_score">
        <div class="stars">
          <svg v-for="i in 5" :key="i"
            viewBox="0 0 16 16" width="16" height="16"
            :fill="i <= Math.round(game.metacritic_score / 20) ? '#f59e0b' : '#e8e4d9'">
            <path d="M8 1l1.8 3.6L14 5.4l-3 2.9.7 4.1L8 10.4l-3.7 2 .7-4.1-3-2.9 4.2-.8z"/>
          </svg>
        </div>
        <span class="meta-score">평점 {{ game.metacritic_score }}점</span>
      </template>
      <span v-else class="coming-soon">추후 업데이트 예정</span>
    </div>

    <!-- 태그 칩들 -->
    <div class="tag-chips">
      <span v-if="game.supports_korean" class="chip">한국어 지원</span>
      <span v-if="game.required_age"    class="chip">{{ game.required_age }}세 이상</span>
      <span v-if="!game.is_online"      class="chip">오프라인</span>
      <!-- <span                              class="chip">{{ game.release_status }}</span> -->
    </div>

    <!-- 찜하기 버튼 -->
    <button class="wishlist-btn" :class="{ wished }" @click="toggleWish">
      <svg xmlns="http://www.w3.org/2000/svg"
        :fill="wished ? '#c0392b' : 'none'"
        viewBox="0 0 24 24" stroke-width="1.5"
        :stroke="wished ? '#c0392b' : 'currentColor'"
        width="18">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
      </svg>
      {{ wished ? '찜 해제' : '찜하기' }}
    </button>

    <!-- 스팀 페이지 버튼 -->
    <a
      v-if="game.steam_id"
      :href="`https://store.steampowered.com/app/${game.steam_id}/`"
      target="_blank"
      rel="noopener noreferrer"
      class="steam-btn"
    >
      <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
        <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.252 0-2.265-1.014-2.265-2.265z"/>
      </svg>
      Steam 페이지 보기
    </a>

    <!-- 장르 태그 -->
    <div class="genre-section">
      <h3 class="genre-label">장르 태그</h3>
      <div class="genre-tags">
        <span v-for="g in visibleGenres" :key="g.id" class="genre-chip">
          {{ g.name }}
        </span>
        <button v-if="hasMore" class="genre-more" @click="showAll = !showAll">
          {{ showAll ? '접기' : `+${game.genres.length - MAX_VISIBLE}` }}
        </button>
      </div>
    </div>

  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { wishlistAPI } from '@/api/services'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

const props = defineProps({
  game: { type: Object, required: true },
})

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const MAX_VISIBLE = 5
const showAll = ref(false)
const wished = ref(props.game.is_wishlisted || false)

const visibleGenres = computed(() =>
  showAll.value ? props.game.genres : (props.game.genres || []).slice(0, MAX_VISIBLE)
)
const hasMore = computed(() => (props.game.genres || []).length > MAX_VISIBLE)

const releaseDateFormatted = computed(() => {
  const raw = props.game.release_date
  if (!raw) return null
  const d = new Date(raw)
  if (isNaN(d)) return raw
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`
})

function formatPrice(p) {
  if (p === null || p === undefined) return '추후 업데이트'
  if (Number(p) === 0) return '무료'
  return '₩' + Number(p).toLocaleString('ko-KR')
}

async function toggleWish() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  const prev = wished.value
  wished.value = !prev
  try {
    if (!prev) {
      await wishlistAPI.add(props.game.id)
      notificationStore.refresh()
    } else {
      await wishlistAPI.remove(props.game.id)
    }
  } catch {
    wished.value = prev
  }
}
</script>

<style scoped>
.info-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 14px;
  padding: 24px;
  height: fit-content;
}

/* 배지 */
.badges {
  display: flex;
  align-items: center;
  gap: 6px;
}
.badge {
  font-size: 12px;
  font-weight: 600;
  color: #6b6256;
  background: #f0ece3;
  border-radius: 6px;
  padding: 3px 8px;
}
.badge--date {
  color: #1e3a5f;
  background: #eef3fa;
  border: 1px solid #93b4e0;
}
.dot-sep { color: #c8c2b4; font-size: 12px; }

/* 제목 */
.title {
  font-size: 24px;
  font-weight: 800;
  color: #1a1510;
  line-height: 1.3;
  letter-spacing: -0.02em;
  margin: 0;
}
.title-ko {
  font-size: 16px;
  font-weight: 600;
  color: #6b6256;
  letter-spacing: 0;
}

/* 가격 */
.price-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.price-original {
  font-size: 13px;
  color: #9e9585;
  text-decoration: line-through;
}
.arrow-icon { color: #9e9585; font-size: 13px; }
.price-final {
  font-size: 20px;
  font-weight: 800;
  color: #1e3a5f;
}
.discount-badge {
  font-size: 11px;
  font-weight: 700;
  background: #1e3a5f;
  color: white;
  padding: 3px 8px;
  border-radius: 6px;
}

/* 별점 */
.score-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.stars { display: flex; gap: 2px; }
.meta-score {
  font-size: 12px;
  font-weight: 700;
  color: #6b6256;
  background: #f0ece3;
  border-radius: 6px;
  padding: 3px 8px;
}

/* 태그 칩 */
.tag-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.chip {
  font-size: 12px;
  color: #3d3529;
  border: 1px solid #ddd8cc;
  border-radius: 999px;
  padding: 4px 10px;
}

/* 찜하기 버튼 */
.wishlist-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #fff;
  border: 1.5px solid #ddd8cc;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  color: #3d3529;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}
.wishlist-btn:hover { border-color: #c0392b; color: #c0392b; }
.wishlist-btn.wished { border-color: #c0392b; color: #c0392b; background: #fff5f5; }

/* 스팀 버튼 */
.steam-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  margin-top: -10px;
  background: #1b2838;
  border: 1.5px solid #1b2838;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  color: #c7d5e0;
  text-decoration: none;
  font-family: inherit;
  transition: all 0.15s;
}
.steam-btn:hover {
  background: #2a475e;
  border-color: #2a475e;
  color: #fff;
}

/* 장르 태그 */
.genre-section {
  border-top: 1px solid #f0ece3;
  padding-top: 16px;
}
.genre-label {
  font-size: 13px;
  font-weight: 700;
  color: #3d3529;
  margin: 0 0 10px;
}
.genre-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.genre-chip {
  font-size: 12px;
  color: #1e3a5f;
  background: #eef3fa;
  border: 1px solid #93b4e0;
  border-radius: 8px;
  padding: 4px 10px;
  font-weight: 500;
}
.genre-more {
  font-size: 12px;
  color: #6b6256;
  background: #f0ece3;
  border: 1px solid #ddd8cc;
  border-radius: 8px;
  padding: 4px 10px;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}
.genre-more:hover { border-color: #1e3a5f; color: #1e3a5f; }

/* 추후 업데이트 예정 */
.coming-soon {
  font-size: 13px;
  color: #9e9585;
  font-style: italic;
}
</style>