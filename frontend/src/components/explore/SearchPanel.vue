<template>
  <div class="panel" :class="{ active: isActive }" @click="$emit('activate')">
    <div class="panel-header">
      <h2>
        검색으로 찾기
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
        </svg>
      </h2>
      <p class="desc">키워드와 필터를 사용해 원하는 게임을 찾아보세요.</p>
    </div>

    <div class="search-wrap">
      <input
        v-model="keyword"
        type="text"
        placeholder="게임 제목을 검색하세요"
        class="search-input"
        @focus="$emit('activate')"
        @keydown.enter="handleSubmit"
      />
      <button class="search-btn" @click.stop="handleSubmit">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" width="16">
          <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
        </svg>
      </button>
    </div>

    <div class="filter-bar">
      <div class="filter-bar-left">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="14">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75" />
        </svg>
        필터
      </div>
      <button class="reset-btn" @click.stop="reset">초기화 ↺</button>
    </div>

    <FilterChipGroup :filter-defs="filterDefs" v-model="filters" />

    <button class="detail-toggle" @click.stop="showDetail = !showDetail">
      상세 필터 {{ showDetail ? '닫기' : '열기' }}
      <svg viewBox="0 0 16 16" fill="currentColor" width="11">
        <path :d="showDetail ? 'M8 6l5 5H3l5-5z' : 'M8 10L3 5h10l-5 5z'"/>
      </svg>
    </button>

    <div v-if="showDetail" class="detail-filter">
      <div class="detail-row">
        <span class="detail-label">가격대</span>
        <label v-for="o in priceOptions" :key="o.value">
          <input type="radio" v-model="filters.priceRange" :value="o.value" /> {{ o.label }}
        </label>
      </div>
      <div class="detail-row">
        <span class="detail-label">출시 연도</span>
        <label v-for="o in yearOptions" :key="o.value">
          <input type="radio" v-model="filters.year" :value="o.value" /> {{ o.label }}
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FilterChipGroup from './FilterChipGroup.vue'

defineProps({
  isActive: { type: Boolean, default: false },
})
const emit = defineEmits(['activate', 'submit', 'reset'])

const keyword = ref('')
const showDetail = ref(false)
const filters = ref({
  genre: [], platform: [], price: [], language: [], difficulty: [],
  priceRange: 'all', year: '',
})

const filterDefs = [
  { key: 'genre',      label: '장르',   options: ['RPG', '어드벤처', '퍼즐', '액션', '시뮬레이션'] },
  { key: 'platform',   label: '플랫폼', options: ['PC', 'Mac', '모바일'] },
  { key: 'price',      label: '가격',   options: ['무료', '1만원 이하', '2만원 이하', '전체'] },
  { key: 'language',   label: '언어',   options: ['한국어', '영어', '일본어'] },
  { key: 'difficulty', label: '난이도', options: ['쉬움', '보통', '어려움'] },
]

const priceOptions = [
  { value: 'free', label: '무료' },
  { value: 'under10k', label: '1만원 이하' },
  { value: 'under20k', label: '2만원 이하' },
  { value: 'all', label: '전체' },
]
const yearOptions = [
  { value: '2024', label: '2024' },
  { value: '2023', label: '2023' },
  { value: 'older', label: '그 이전' },
]

function handleSubmit() {
  emit('submit', { keyword: keyword.value, filters: filters.value })
}

function reset() {
  keyword.value = ''
  filters.value = { genre: [], platform: [], price: [], language: [], difficulty: [], priceRange: 'all', year: '' }
  emit('reset')
}

defineExpose({ reset })
</script>

<style scoped>
.panel {
  background: #fff;
  border: 1.5px solid #e8e4d9;
  border-radius: 16px;
  padding: 28px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.panel.active {
  border-color: #1e3a5f;
  box-shadow: 0 0 0 3px rgba(30,58,95,0.07);
  cursor: default;
}
.panel-header h2 {
  font-size: 18px;
  font-weight: 800;
  color: #1a1510;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.icon { width: 16px; color: #1e3a5f; }
.desc { font-size: 13px; color: #9e9585; }

.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.search-input {
  width: 100%;
  padding: 12px 44px 12px 16px;
  border: 1px solid #e8e4d9;
  border-radius: 10px;
  font-size: 14px;
  color: #1a1510;
  background: #fafaf8;
  outline: none;
  font-family: inherit;
  transition: border-color 0.15s;
}
.search-input:focus { border-color: #1e3a5f; background: #fff; }
.search-input::placeholder { color: #c8c2b4; }
.search-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  color: #9e9585;
  display: flex;
  align-items: center;
  padding: 0;
  transition: color 0.15s;
}
.search-btn:hover { color: #1e3a5f; }

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 600;
  color: #3d3529;
}
.filter-bar-left { display: flex; align-items: center; gap: 6px; }
.reset-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: #9e9585;
  cursor: pointer;
  font-family: inherit;
}
.reset-btn:hover { color: #1e3a5f; }

.detail-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  font-size: 13px;
  color: #6b6256;
  cursor: pointer;
  padding: 0;
  font-family: inherit;
}
.detail-toggle:hover { color: #1e3a5f; }

.detail-filter {
  background: #f7f5f0;
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.detail-row {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: #3d3529;
  flex-wrap: wrap;
}
.detail-label { font-weight: 600; min-width: 60px; color: #6b6256; }
.detail-row label { display: flex; align-items: center; gap: 4px; cursor: pointer; }
.detail-row input { accent-color: #1e3a5f; }
</style>