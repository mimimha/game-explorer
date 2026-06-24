<template>
  <div class="page-wrap">

    <!-- Breadcrumb -->
    <nav class="breadcrumb">
      <RouterLink to="/">홈</RouterLink>
      <span class="sep">&rsaquo;</span>
      <span>커뮤니티</span>
    </nav>

    <header class="page-header">
      <div>
        <h1 class="page-title">커뮤니티</h1>
        <p class="page-sub">인디게임에 대한 자유로운 이야기, 공략, 파티원 모집에 대한 이야기를 나눠보세요!</p>
      </div>
    </header>

    <!-- Controls: 탭 + 검색 + 글쓰기 -->
    <div class="controls">
      <div class="tabs">
        <button
          v-for="tab in TABS"
          :key="tab.value"
          class="tab"
          :class="{ active: activeCategory === tab.value }"
          @click="selectCategory(tab.value)"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="controls-right">
        <button v-if="authStore.isLoggedIn" class="btn-write" @click="openWriteModal">
          <svg viewBox="0 0 20 20" fill="currentColor" class="btn-write-icon">
            <path d="M2.695 14.763l-1.262 3.154a.5.5 0 0 0 .65.65l3.155-1.262a4 4 0 0 0 1.343-.885L17.5 5.5a2.121 2.121 0 0 0-3-3L3.58 13.42a4 4 0 0 0-.885 1.343Z"/>
          </svg>
          글쓰기
        </button>
        <RouterLink v-else to="/login" class="btn-write">글쓰기</RouterLink>
      </div>
    </div>

    <!-- Table -->
    <div class="table-wrap">
      <div v-if="loading" class="state-box">
        <div class="spinner" />
        <p>게시글을 불러오는 중...</p>
      </div>

      <div v-else-if="posts.length === 0" class="state-box">
        <p class="empty-icon">💬</p>
        <p>아직 게시글이 없어요. 첫 번째 글을 작성해보세요!</p>
      </div>

      <template v-else>
        <table class="post-table">
          <thead>
            <tr>
              <th class="col-num">번호</th>
              <th class="col-title">제목</th>
              <th class="col-author">작성자</th>
              <th class="col-date">작성일</th>
              <th class="col-count">댓글 수</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="post in posts"
              :key="post.id"
              class="post-row"
              @click="goToPost(post.id)"
            >
              <td class="col-num">{{ post.id }}</td>
              <td class="col-title">
                <div class="title-cell">
                  <span class="cat-badge" :class="`cat-${post.category}`">{{ post.category }}</span>
                  <span class="post-title">{{ post.title }}</span>
                  <span v-if="post.game" class="game-tag">
                    <svg viewBox="0 0 16 16" fill="currentColor" class="game-icon"><path d="M11.5 2A1.5 1.5 0 0 0 10 3.5v9A1.5 1.5 0 0 0 11.5 14h1A1.5 1.5 0 0 0 14 12.5v-9A1.5 1.5 0 0 0 12.5 2h-1Zm-6.723 3.24c-.184-.39-.629-.56-1.019-.374L2.49 5.52A1.5 1.5 0 0 0 1.75 6.87v4.258A1.5 1.5 0 0 0 2.49 12.48l1.267.654c.39.185.835.015 1.02-.374L7.648 7H5.5L4.777 5.24ZM8 7l1.552 5.04a1 1 0 0 1-.634 1.246l-.708.219A1 1 0 0 1 6.964 12.5L5 7h3Z"/></svg>
                    {{ post.game.title }}
                  </span>
                </div>
              </td>
              <td class="col-author" @click.stop="goToProfile(post.author.id)">
                <div class="author-cell author-link">
                  <img :src="post.author.profile_img || defaultAvatar" class="author-avatar" alt="" />
                  <span>{{ post.author.nickname }}</span>
                </div>
              </td>
              <td class="col-date">{{ formatDate(post.created_at) }}</td>
              <td class="col-count">
                <span v-if="post.comment_count > 0" class="comment-count">{{ post.comment_count }}</span>
                <span v-else class="comment-none">0</span>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <button class="page-btn" :disabled="currentPage === 1" @click="goPage(1)">«</button>
          <button class="page-btn" :disabled="currentPage === 1" @click="goPage(currentPage - 1)">‹</button>

          <button
            v-for="p in visiblePages"
            :key="p"
            class="page-btn"
            :class="{ active: p === currentPage }"
            @click="goPage(p)"
          >{{ p }}</button>

          <button class="page-btn" :disabled="currentPage === totalPages" @click="goPage(currentPage + 1)">›</button>
          <button class="page-btn" :disabled="currentPage === totalPages" @click="goPage(totalPages)">»</button>
        </div>
      </template>
    </div>

    <!-- Search Bar -->
    <div class="search-center">
      <form class="search-form" @submit.prevent="doSearch">
        <select v-model="searchType" class="search-type-select">
          <option value="title">제목</option>
          <option value="author">작성자</option>
        </select>
        <input v-model="searchKeyword" type="text" :placeholder="searchType === 'author' ? '닉네임 검색' : '제목 검색'" class="search-input" />
        <button type="submit" class="search-btn" aria-label="검색">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"/>
          </svg>
        </button>
      </form>
    </div>

    <!-- Write/Edit Modal -->
    <Teleport to="body">
      <div v-if="modalOpen" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ editPostId ? '글 수정' : '글쓰기' }}</h2>
            <button class="modal-close" @click="closeModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <form class="modal-form" @submit.prevent="submitPost">
            <div class="form-row">
              <div class="form-field form-field--category">
                <label>카테고리</label>
                <select v-model="postForm.category">
                  <option value="자유">자유</option>
                  <option value="공략">공략</option>
                  <option value="파티원모집">파티원 모집</option>
                </select>
              </div>
              <div class="form-field form-field--title">
                <label>제목</label>
                <input v-model="postForm.title" type="text" placeholder="제목을 입력하세요" maxlength="200" required />
              </div>
            </div>

            <div class="form-field">
              <label>내용</label>
              <textarea v-model="postForm.content" placeholder="내용을 입력하세요" rows="10" required></textarea>
            </div>

            <div v-if="submitError" class="form-error">{{ submitError }}</div>

            <div class="modal-actions">
              <button type="button" class="btn-cancel" @click="closeModal">취소</button>
              <button type="submit" class="btn-save" :disabled="submitting">
                {{ submitting ? '저장 중...' : (editPostId ? '수정' : '등록') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { communityAPI } from '@/api/services'
import { useAuthStore } from '@/stores/auth'
import defaultAvatar from '@/assets/profile.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const TABS = [
  { label: '전체', value: '' },
  { label: '자유', value: '자유' },
  { label: '공략', value: '공략' },
  { label: '파티원 모집', value: '파티원모집' },
]

const PAGE_SIZE = 20

const posts = ref([])
const loading = ref(false)
const totalCount = ref(0)
const currentPage = ref(1)
const activeCategory = ref('')
const searchKeyword = ref('')
const appliedKeyword = ref('')
const searchType = ref('title')
const appliedSearchType = ref('title')

const totalPages = computed(() => Math.ceil(totalCount.value / PAGE_SIZE))

const visiblePages = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  const delta = 2
  const pages = []
  for (let p = Math.max(1, cur - delta); p <= Math.min(total, cur + delta); p++) {
    pages.push(p)
  }
  return pages
})

async function fetchPosts() {
  loading.value = true
  try {
    const params = { page: currentPage.value }
    if (activeCategory.value) params.category = activeCategory.value
    if (appliedKeyword.value) {
      params.q = appliedKeyword.value
      params.search_type = appliedSearchType.value
    }
    const { data } = await communityAPI.getPosts(params)
    posts.value = data.results ?? data
    totalCount.value = data.count ?? posts.value.length
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
}

function selectCategory(val) {
  activeCategory.value = val
  currentPage.value = 1
}

function doSearch() {
  appliedKeyword.value = searchKeyword.value.trim()
  appliedSearchType.value = searchType.value
  currentPage.value = 1
}

function goPage(p) {
  currentPage.value = p
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToPost(postId) {
  router.push({ name: 'post-detail', params: { postId } })
}

function goToProfile(userId) {
  router.push({ name: 'user-profile', params: { userId } })
}

function formatDate(iso) {
  const d = new Date(iso)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

// Write modal
const modalOpen = ref(false)
const editPostId = ref(null)
const submitting = ref(false)
const submitError = ref('')
const postForm = ref({ title: '', content: '', category: '자유' })

function openWriteModal() {
  editPostId.value = null
  postForm.value = { title: '', content: '', category: activeCategory.value || '자유' }
  submitError.value = ''
  modalOpen.value = true
}

function closeModal() {
  modalOpen.value = false
}

async function submitPost() {
  submitError.value = ''
  if (!postForm.value.title.trim() || !postForm.value.content.trim()) {
    submitError.value = '제목과 내용을 모두 입력해주세요.'
    return
  }
  submitting.value = true
  try {
    const payload = {
      title: postForm.value.title.trim(),
      content: postForm.value.content.trim(),
      category: postForm.value.category,
    }
    if (editPostId.value) {
      await communityAPI.updatePost(editPostId.value, payload)
    } else {
      const { data } = await communityAPI.createPost(payload)
      closeModal()
      router.push({ name: 'post-detail', params: { postId: data.id } })
      return
    }
    closeModal()
    fetchPosts()
  } catch (e) {
    const data = e?.response?.data
    const first = data && Object.values(data)[0]
    submitError.value = Array.isArray(first) ? first[0] : '저장에 실패했어요.'
  } finally {
    submitting.value = false
  }
}

watch([activeCategory, currentPage, appliedKeyword, appliedSearchType], fetchPosts)

onMounted(fetchPosts)
</script>

<style scoped>
.page-wrap {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 24px 64px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #9e9585;
}
.breadcrumb a { color: #9e9585; text-decoration: none; }
.breadcrumb a:hover { color: #1e3a5f; }
.sep { font-size: 12px; }

.page-header { margin-bottom: 4px; }
.page-title { font-size: 26px; font-weight: 800; color: #1a1510; margin: 0 0 6px; }
.page-sub { font-size: 14px; color: #9e9585; margin: 0; }

/* Controls */
.controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.tabs { display: flex; gap: 4px; }
.tab {
  padding: 8px 18px;
  border: 1px solid transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #6b6256;
  background: none;
  cursor: pointer;
  transition: all 0.15s;
}
.tab:hover { background: #f0ece3; color: #1a1510; }
.tab.active {
  background: #1e3a5f;
  color: #fff;
  border-color: #1e3a5f;
}

.controls-right { display: flex; align-items: center; gap: 10px; }

.search-center {
  display: flex;
  justify-content: center;
}

.search-form {
  display: flex;
  align-items: center;
  height: 36px;
  border: 1px solid #ddd8cc;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.15s;
  background: #f7f5f0;
}
.search-form:focus-within { border-color: #1e3a5f; }

.search-type-select {
  height: 100%;
  padding: 0 15px 0 10px;
  border: none;
  border-right: 1px solid #ddd8cc;
  border-radius: 0;
  font-size: 13px;
  color: #3d3529;
  background: #f7f5f0;
  outline: none;
  cursor: pointer;
  flex-shrink: 0;
}

.search-input {
  width: 260px;
  height: 100%;
  padding: 0 10px;
  border: none;
  background: #f7f5f0;
  font-size: 13px;
  color: #1a1510;
  outline: none;
  transition: background 0.15s;
}
.search-form:focus-within .search-input { background: #fff; }

.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 0 12px;
  border: none;
  border-left: 1px solid #ddd8cc;
  background: #1e3a5f;
  color: #fff;
  cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}
.search-btn:hover { background: #162d4a; }
.search-btn svg { width: 15px; height: 15px; }

.btn-write {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: #1e3a5f;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s;
  white-space: nowrap;
}
.btn-write:hover { background: #162d4a; }
.btn-write-icon { width: 14px; height: 14px; }

/* Table */
.table-wrap {
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 12px;
  overflow: hidden;
}

.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 0;
  gap: 12px;
  color: #9e9585;
  font-size: 14px;
}
.empty-icon { font-size: 36px; margin: 0; }
.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e8e4d9;
  border-top-color: #1e3a5f;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.post-table {
  width: 100%;
  border-collapse: collapse;
}

.post-table thead tr {
  background: #fafaf8;
  border-bottom: 1px solid #e8e4d9;
}
.post-table th {
  padding: 13px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #9e9585;
  text-align: left;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.col-num { width: 72px; text-align: center; }
.col-title { }
.col-author { width: 140px; }
.col-date { width: 110px; }
.col-count { width: 80px; text-align: center; }

.post-row {
  border-bottom: 1px solid #f0ece3;
  cursor: pointer;
  transition: background 0.12s;
}
.post-row:last-child { border-bottom: none; }
.post-row:hover { background: #f9f7f3; }

.post-table td {
  padding: 14px 16px;
  font-size: 14px;
  color: #3d3529;
}
.post-table td.col-num {
  text-align: center;
  font-size: 13px;
  color: #9e9585;
}
.post-table td.col-date {
  font-size: 13px;
  color: #9e9585;
  white-space: nowrap;
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.post-title {
  font-weight: 500;
  color: #1a1510;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.post-title:hover { color: #1e3a5f; }

.cat-badge {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
}
.cat-자유 { background: #e8f0fb; color: #1e3a5f; }
.cat-공략 { background: #fef3c7; color: #92400e; }
.cat-파티원모집 { background: #ede9fe; color: #6d28d9; }

.game-tag {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
  font-size: 11px;
  color: #6b6256;
  background: #f0ece3;
  border-radius: 6px;
  padding: 2px 7px;
}
.game-icon { width: 11px; height: 11px; }

.author-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.author-link {
  cursor: pointer;
  border-radius: 6px;
  transition: color 0.12s;
}
.author-link:hover { color: #1e3a5f; }
.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e8e4d9;
  flex-shrink: 0;
}

.comment-count {
  font-size: 13px;
  font-weight: 600;
  color: #1e3a5f;
}
.comment-none { color: #c8c2b4; font-size: 13px; }

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 20px;
  border-top: 1px solid #e8e4d9;
}
.page-btn {
  min-width: 34px;
  height: 34px;
  padding: 0 6px;
  border: 1px solid #e8e4d9;
  border-radius: 8px;
  background: #fff;
  color: #3d3529;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.12s;
}
.page-btn:hover:not(:disabled) { border-color: #1e3a5f; color: #1e3a5f; }
.page-btn.active { background: #1e3a5f; border-color: #1e3a5f; color: #fff; font-weight: 700; }
.page-btn:disabled { color: #c8c2b4; cursor: default; border-color: #e8e4d9; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(26,21,16,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 24px;
}
.modal {
  background: #fff;
  border-radius: 16px;
  padding: 28px 32px;
  width: 100%;
  max-width: 640px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  max-height: 90vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.modal-header h2 { font-size: 18px; font-weight: 700; color: #1a1510; margin: 0; }
.modal-close { background: none; border: none; cursor: pointer; color: #9e9585; padding: 4px; }
.modal-close svg { width: 20px; height: 20px; }

.modal-form { display: flex; flex-direction: column; gap: 16px; }
.form-row { display: flex; gap: 12px; }
.form-field { display: flex; flex-direction: column; gap: 6px; }
.form-field--category { width: 140px; flex-shrink: 0; }
.form-field--title { flex: 1; }
.form-field label { font-size: 13px; font-weight: 600; color: #6b6256; }

.form-field input,
.form-field select,
.form-field textarea {
  border: 1px solid #e8e4d9;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  color: #1a1510;
  outline: none;
  background: #fff;
  font-family: inherit;
  transition: border-color 0.15s;
}
.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus { border-color: #1e3a5f; }
.form-field textarea { resize: vertical; line-height: 1.6; min-height: 200px; }

.form-error {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  color: #c53030;
  font-size: 13px;
  padding: 10px 12px;
  border-radius: 8px;
}

.modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 8px; }
.btn-cancel {
  padding: 9px 20px;
  border: 1px solid #e8e4d9;
  border-radius: 8px;
  background: #fff;
  color: #6b6256;
  font-size: 14px;
  cursor: pointer;
}
.btn-save {
  padding: 9px 24px;
  border: none;
  border-radius: 8px;
  background: #1e3a5f;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-save:hover:not(:disabled) { background: #162d4a; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
