<template>
  <RouterLink :to="`/games/${game.id}`" class="card">
    <div class="thumbnail">
      <img v-if="game.capsule_url" :src="game.capsule_url" :alt="game.title" />
      <div v-else class="thumbnail-placeholder">
        <svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
          <rect width="80" height="80" fill="#e8e2d5"/>
          <line x1="0" y1="0" x2="80" y2="80" stroke="#c8c2b4" stroke-width="1"/>
          <line x1="80" y1="0" x2="0" y2="80" stroke="#c8c2b4" stroke-width="1"/>
        </svg>
      </div>

      <!-- 할인 배지 -->
      <span v-if="discountRate" class="badge-discount">-{{ discountRate }}%</span>

      <!-- 위시리스트 버튼 (취향 분석 섹션에서만) -->
      <button v-if="showWishlist" class="wishlist-btn" @click.prevent="toggleWishlist">
        <svg xmlns="http://www.w3.org/2000/svg"
          :fill="isWishlisted ? '#c0392b' : 'none'"
          viewBox="0 0 24 24" stroke-width="1.5"
          :stroke="isWishlisted ? '#c0392b' : 'currentColor'">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
        </svg>
      </button>
    </div>

    <div class="card-body">
      <h3 class="card-title">{{ game.title || '게임 제목' }}</h3>

      <div v-if="showPrice" class="price-row">
        <span v-if="discountRate" class="price-original">
          {{ formatPrice(game.initial_price) }}
        </span>
        <span class="price-final">
          {{ formatPrice(game.final_price) }}
        </span>
      </div>

      <div class="tags">
        <span v-for="name in genreNames.slice(0, 2)" :key="name" class="tag">
          {{ name }}
        </span>
        <span v-if="genreNames.length === 0">
          <span class="tag">태그</span>
        </span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { wishlistAPI } from '@/api/services'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  game: {
    type: Object,
    default: () => ({})
  },
  showPrice: {
    type: Boolean,
    default: false
  },
  showWishlist: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()
const authStore = useAuthStore()
const isWishlisted = ref(props.game.is_wishlisted || false)

const discountRate = computed(() => {
  const init = props.game.initial_price
  const final = props.game.final_price
  if (init && final && Number(init) > Number(final)) {
    return Math.round((1 - Number(final) / Number(init)) * 100)
  }
  return null
})

const genreNames = computed(() => (props.game.genres || []).map(g => g.name))

async function toggleWishlist() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  const prev = isWishlisted.value
  isWishlisted.value = !prev
  try {
    if (!prev) {
      await wishlistAPI.add(props.game.id)
    } else {
      await wishlistAPI.remove(props.game.id)
    }
  } catch {
    isWishlisted.value = prev
  }
}

function formatPrice(price) {
  if (price === null || price === undefined) return '무료'
  return '₩' + Number(price).toLocaleString('ko-KR')
}
</script>

<style scoped>
.card {
  display: block;
  width: 100%;
  text-decoration: none;
  color: inherit;
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.15s, box-shadow 0.15s;
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(30, 58, 95, 0.1);
}

.thumbnail {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
  background: #f0ece3;
}
.thumbnail img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.thumbnail-placeholder svg {
  width: 100%;
  height: 100%;
}

.badge-discount {
  position: absolute;
  top: 8px;
  left: 8px;
  background: #1a1510;
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
}

.wishlist-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255,255,255,0.9);
  border: none;
  border-radius: 8px;
  padding: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.wishlist-btn:hover {
  background: white;
}
.wishlist-btn svg {
  width: 18px;
  height: 18px;
  color: #6b6256;
}

.card-body {
  padding: 12px 14px 14px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1510;
  margin: 0 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.price-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.price-original {
  font-size: 12px;
  color: #9e9585;
  text-decoration: line-through;
}
.price-final {
  font-size: 14px;
  font-weight: 700;
  color: #1e3a5f;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}
.tag {
  font-size: 11px;
  color: #6b6256;
  background: #f0ece3;
  border-radius: 999px;
  padding: 2px 8px;
}
</style>