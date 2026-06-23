<template>
  <aside class="info-panel">

    <!-- 플랫폼 · 출시상태 -->
    <div class="badges">
      <span class="badge">{{ game.platform }}</span>
    </div>

    <!-- 제목 -->
    <h1 class="title">{{ game.title }}</h1>

    <!-- 가격 -->
    <div class="price-row">
      <template v-if="game.discount_rate">
        <span class="price-original">₩{{ formatPrice(game.initial_price) }}</span>
        <span class="arrow-icon">→</span>
        <span class="price-final">₩{{ formatPrice(game.final_price) }}</span>
        <span class="discount-badge">-{{ game.discount_rate }}% 할인</span>
      </template>
      <span v-else class="price-final">₩{{ formatPrice(game.final_price) }}</span>
    </div>

    <!-- 메타크리틱 점수 + 별점 -->
    <div class="score-row">
      <div class="stars">
        <svg v-for="i in 5" :key="i"
          viewBox="0 0 16 16" width="16" height="16"
          :fill="i <= Math.round((game.metacritic_score || 0) / 20) ? '#f59e0b' : '#e8e4d9'">
          <path d="M8 1l1.8 3.6L14 5.4l-3 2.9.7 4.1L8 10.4l-3.7 2 .7-4.1-3-2.9 4.2-.8z"/>
        </svg>
      </div>
      <span v-if="game.metacritic_score" class="meta-score">
        Metacritic {{ game.metacritic_score }}
      </span>
    </div>

    <!-- 태그 칩들 -->
    <div class="tag-chips">
      <span v-if="game.supports_korean" class="chip">한국어 지원</span>
      <span v-if="game.required_age"    class="chip">{{ game.required_age }}세 이상</span>
      <span v-if="!game.is_online"      class="chip">오프라인</span>
      <span                              class="chip">{{ game.release_status }}</span>
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
      {{ wished ? '찜 완료' : '찜하기 WISHLIST' }}
    </button>

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

const props = defineProps({
  game: { type: Object, required: true },
})

const MAX_VISIBLE = 5
const showAll = ref(false)
const wished = ref(props.game.is_wishlisted || false)

const visibleGenres = computed(() =>
  showAll.value ? props.game.genres : (props.game.genres || []).slice(0, MAX_VISIBLE)
)
const hasMore = computed(() => (props.game.genres || []).length > MAX_VISIBLE)

function formatPrice(p) {
  return Number(p || 0).toLocaleString('ko-KR')
}

function toggleWish() {
  wished.value = !wished.value
  // TODO: POST /api/wishlist/{game.id}/toggle/
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
</style>