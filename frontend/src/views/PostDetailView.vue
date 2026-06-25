<template>
  <div class="page-wrap">

    <!-- Breadcrumb -->
    <nav class="breadcrumb">
      <RouterLink to="/">홈</RouterLink>
      <span class="sep">&rsaquo;</span>
      <RouterLink to="/community">커뮤니티</RouterLink>
      <span class="sep">&rsaquo;</span>
      <span class="breadcrumb-title">{{ post?.title || '...' }}</span>
    </nav>

    <!-- Loading -->
    <div v-if="loading" class="state-box">
      <div class="spinner" />
      <p>게시글을 불러오는 중...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-box">
      <p>{{ error }}</p>
      <RouterLink to="/community" class="btn-back">목록으로</RouterLink>
    </div>

    <!-- Content -->
    <template v-else-if="post">

      <!-- Post Card -->
      <article class="post-card">
        <!-- Post Header -->
        <div class="post-header">
          <div class="post-meta-top">
            <span class="cat-badge" :class="`cat-${post.category}`">{{ post.category }}</span>
            <span v-if="post.game" class="game-link">
              <svg viewBox="0 0 16 16" fill="currentColor" class="game-icon"><path d="M11.5 2A1.5 1.5 0 0 0 10 3.5v9A1.5 1.5 0 0 0 11.5 14h1A1.5 1.5 0 0 0 14 12.5v-9A1.5 1.5 0 0 0 12.5 2h-1Zm-6.723 3.24c-.184-.39-.629-.56-1.019-.374L2.49 5.52A1.5 1.5 0 0 0 1.75 6.87v4.258A1.5 1.5 0 0 0 2.49 12.48l1.267.654c.39.185.835.015 1.02-.374L7.648 7H5.5L4.777 5.24ZM8 7l1.552 5.04a1 1 0 0 1-.634 1.246l-.708.219A1 1 0 0 1 6.964 12.5L5 7h3Z"/></svg>
              {{ post.game.title }}
            </span>
          </div>

          <h1 class="post-title">{{ post.title }}</h1>

          <div class="post-meta">
            <RouterLink :to="`/users/${post.author.id}`" class="author-link">
              <img :src="post.author.profile_img || defaultAvatar" class="author-avatar" alt="" />
              <span class="author-name">{{ post.author.nickname }}</span>
            </RouterLink>
            <span class="dot">·</span>
            <span class="post-date">{{ formatDate(post.created_at) }}</span>
            <span v-if="post.updated_at !== post.created_at" class="edited">(수정됨)</span>
            <span class="dot">·</span>
            <span class="comment-meta">댓글 {{ comments.length }}개</span>
          </div>

          <!-- Author actions -->
          <div v-if="post.is_author" class="post-actions">
            <button class="action-btn" @click="openEditModal">수정</button>
            <button class="action-btn action-btn--danger" @click="confirmDelete">삭제</button>
          </div>
        </div>

        <!-- Post Body -->
        <div class="post-body">
          <template v-for="(block, i) in groupedContent" :key="i">
            <template v-if="block.type === 'text'">
              <p v-for="(line, j) in block.value.split('\n')" :key="j" class="content-line">
                <template v-if="line">{{ line }}</template>
                <br v-else />
              </p>
            </template>
            <!-- 연속 이미지들: flex로 가로 배치 -->
            <div v-else class="image-row">
              <div
                v-for="(img, k) in block.images"
                :key="k"
                class="image-wrap"
                :style="{ width: img.widthPct + '%' }"
              >
                <img :src="img.url" class="post-image" @click="openLightbox(img.url)" />
              </div>
            </div>
          </template>
        </div>
      </article>

      <!-- 이미지 라이트박스 -->
      <Teleport to="body">
        <div v-if="lightboxSrc" class="lightbox" @click="lightboxSrc = null">
          <img :src="lightboxSrc" class="lightbox-img" />
        </div>
      </Teleport>

      <!-- Comment Section -->
      <section class="comments-section">
        <h2 class="comments-title">댓글 <span class="comments-count">{{ comments.length }}</span></h2>

        <!-- Comment List -->
        <div v-if="comments.length === 0" class="comments-empty">
          첫 번째 댓글을 남겨보세요!
        </div>

        <ul v-else class="comment-list">
          <li
            v-for="comment in comments"
            :key="comment.id"
            class="comment-item"
          >
            <div class="comment-author-row">
              <RouterLink :to="`/users/${comment.author.id}`" class="comment-author-link">
                <img :src="comment.author.profile_img || defaultAvatar" class="comment-avatar" alt="" />
                <span class="comment-author-name">{{ comment.author.nickname }}</span>
              </RouterLink>
              <span class="comment-date">{{ formatDate(comment.created_at) }}</span>

              <div v-if="comment.is_author" class="comment-actions">
                <button class="comment-action-btn" @click="startEditComment(comment)">수정</button>
                <button class="comment-action-btn comment-action-btn--danger" @click="deleteComment(comment.id)">삭제</button>
              </div>
            </div>

            <!-- Inline edit -->
            <div v-if="editingCommentId === comment.id" class="comment-edit-box">
              <textarea
                v-model="editCommentContent"
                class="comment-textarea"
                rows="3"
                @keydown.ctrl.enter.prevent="submitEditComment(comment.id)"
              ></textarea>
              <div class="comment-edit-actions">
                <button class="btn-cancel-sm" @click="cancelEditComment">취소</button>
                <button class="btn-save-sm" :disabled="submittingComment" @click="submitEditComment(comment.id)">저장</button>
              </div>
            </div>

            <p v-else class="comment-content">{{ comment.content }}</p>
          </li>
        </ul>

        <!-- Comment Input -->
        <div class="comment-input-wrap">
          <template v-if="authStore.isLoggedIn">
            <div class="comment-input-row">
              <img :src="authStore.user?.profile_img || defaultAvatar" class="my-avatar" alt="" />
              <div class="comment-input-box">
                <textarea
                  v-model="newComment"
                  class="comment-textarea"
                  placeholder="댓글을 입력하세요 (Ctrl+Enter로 등록)"
                  rows="3"
                  @keydown.ctrl.enter.prevent="submitComment"
                ></textarea>
                <div class="comment-submit-row">
                  <button class="btn-comment" :disabled="submittingComment || !newComment.trim()" @click="submitComment">
                    {{ submittingComment ? '등록 중...' : '댓글 등록' }}
                  </button>
                </div>
              </div>
            </div>
          </template>
          <div v-else class="comment-login-prompt">
            <RouterLink to="/login">로그인</RouterLink> 후 댓글을 남길 수 있어요.
          </div>
        </div>
      </section>

    </template>

    <!-- Edit Post Modal -->
    <Teleport to="body">
      <div v-if="editModalOpen" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal">
          <div class="modal-header">
            <h2>글 수정</h2>
            <button class="modal-close" @click="closeEditModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <form class="modal-form" @submit.prevent="submitEdit">
            <div class="form-row">
              <div class="form-field form-field--category">
                <label>카테고리</label>
                <select v-model="editForm.category">
                  <option value="자유">자유</option>
                  <option value="공략">공략</option>
                  <option value="파티원모집">파티원모집</option>
                </select>
              </div>
              <div class="form-field form-field--title">
                <label>제목</label>
                <input v-model="editForm.title" type="text" maxlength="200" required />
              </div>
            </div>
            <div class="form-field">
              <label>내용</label>
              <PostBlockEditor ref="editEditorRef" />
            </div>
            <div v-if="editError" class="form-error">{{ editError }}</div>
            <div class="modal-actions">
              <button type="button" class="btn-cancel" @click="closeEditModal">취소</button>
              <button type="submit" class="btn-save" :disabled="editSaving">
                {{ editSaving ? '저장 중...' : '수정' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { communityAPI } from '@/api/services'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import defaultAvatar from '@/assets/profile.png'
import PostBlockEditor from '@/components/community/PostBlockEditor.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const postId = computed(() => Number(route.params.postId))

const post = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref(null)

async function fetchPost() {
  loading.value = true
  error.value = null
  try {
    const [postRes, commentRes] = await Promise.all([
      communityAPI.getPost(postId.value),
      communityAPI.getComments(postId.value),
    ])
    post.value = postRes.data
    comments.value = commentRes.data?.results ?? commentRes.data ?? []
  } catch (e) {
    if (e.response?.status === 404) {
      error.value = '존재하지 않는 게시글이에요.'
    } else {
      error.value = '게시글을 불러오는 데 실패했어요.'
    }
  } finally {
    loading.value = false
  }
}

// content + images → 텍스트/이미지 블록 배열로 변환 (표시용)
// 이미지 형식: [IMAGE:id] 또는 [IMAGE:id:widthPct]
const renderedContent = computed(() => {
  if (!post.value) return []
  const imageMap = Object.fromEntries((post.value.images ?? []).map(img => [img.id, img.url]))
  const lines = (post.value.content ?? '').split('\n')
  const result = []
  let textBuffer = []
  for (const line of lines) {
    const match = line.match(/^\[IMAGE:(\d+)(?::(\d+))?\]$/)
    if (match) {
      if (textBuffer.length) { result.push({ type: 'text', value: textBuffer.join('\n') }); textBuffer = [] }
      const url = imageMap[parseInt(match[1])]
      const widthPct = match[2] ? parseInt(match[2]) : 100
      if (url) result.push({ type: 'image', url, widthPct })
    } else {
      textBuffer.push(line)
    }
  }
  if (textBuffer.length) result.push({ type: 'text', value: textBuffer.join('\n') })
  return result
})

// 연속된 이미지 블록을 하나의 row로 묶어 가로 배치 지원
const groupedContent = computed(() => {
  const out = []
  let imgs = []
  for (const block of renderedContent.value) {
    if (block.type === 'image') {
      imgs.push(block)
    } else {
      if (imgs.length) { out.push({ type: 'image-row', images: [...imgs] }); imgs = [] }
      out.push(block)
    }
  }
  if (imgs.length) out.push({ type: 'image-row', images: imgs })
  return out
})

// 라이트박스
const lightboxSrc = ref(null)
function openLightbox(url) { lightboxSrc.value = url }

function formatDate(iso) {
  const d = new Date(iso)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

// Delete post
async function confirmDelete() {
  if (!confirm('게시글을 삭제할까요?')) return
  try {
    await communityAPI.deletePost(postId.value)
    router.push('/community')
  } catch {
    alert('삭제에 실패했어요.')
  }
}

// Edit post modal
const editModalOpen = ref(false)
const editEditorRef = ref(null)
const editForm = ref({ title: '', category: '자유' })
const editError = ref('')
const editSaving = ref(false)

function openEditModal() {
  editForm.value = { title: post.value.title, category: post.value.category }
  editError.value = ''
  editModalOpen.value = true
  nextTick(() => {
    editEditorRef.value?.init(post.value.content, post.value.images)
  })
}

function closeEditModal() {
  editEditorRef.value?.cleanup()
  editModalOpen.value = false
}

async function submitEdit() {
  editError.value = ''
  editSaving.value = true
  try {
    const blocks = editEditorRef.value?.getBlocks() ?? []

    // 원본 이미지 ID 목록 vs 현재 에디터 이미지 ID 목록 비교 → 삭제 목록 도출
    const originalIds = new Set((post.value.images ?? []).map(img => img.id))
    const keptIds = new Set(blocks.filter(b => b.type === 'image' && b.existingId).map(b => b.existingId))
    const deleteIds = [...originalIds].filter(id => !keptIds.has(id))

    // 삭제 먼저
    await Promise.all(deleteIds.map(id => communityAPI.deleteImage(postId.value, id)))

    // 새 이미지 업로드 + content 빌드 (빈 텍스트 블록 스킵)
    const parts = []
    for (const block of blocks) {
      if (block.type === 'text') {
        if (block.value.trim()) parts.push(block.value)
      } else {
        let imgId = block.existingId ?? null
        if (block.file) {
          const { data } = await communityAPI.uploadImages(postId.value, [block.file])
          imgId = data[0].id
        }
        if (imgId) {
          const wp = block.widthPct ?? 100
          parts.push(wp < 100 ? `[IMAGE:${imgId}:${wp}]` : `[IMAGE:${imgId}]`)
        }
      }
    }

    const content = parts.join('\n') || ' ' // blank=False 통과를 위해 빈 경우 공백

    await communityAPI.updatePost(postId.value, {
      title: editForm.value.title.trim(),
      content,
      category: editForm.value.category,
    })

    const refreshed = await communityAPI.getPost(postId.value)
    post.value = refreshed.data
    closeEditModal()
  } catch (e) {
    const d = e?.response?.data
    const first = d && Object.values(d)[0]
    editError.value = Array.isArray(first) ? first[0] : '수정에 실패했어요.'
  } finally {
    editSaving.value = false
  }
}

// Comments
const newComment = ref('')
const submittingComment = ref(false)

async function submitComment() {
  if (!newComment.value.trim()) return
  submittingComment.value = true
  try {
    const { data } = await communityAPI.createComment(postId.value, { content: newComment.value.trim() })
    comments.value.push(data)
    newComment.value = ''
    notificationStore.refresh()
  } catch {
    alert('댓글 등록에 실패했어요.')
  } finally {
    submittingComment.value = false
  }
}

// Edit comment
const editingCommentId = ref(null)
const editCommentContent = ref('')

function startEditComment(comment) {
  editingCommentId.value = comment.id
  editCommentContent.value = comment.content
}
function cancelEditComment() {
  editingCommentId.value = null
  editCommentContent.value = ''
}
async function submitEditComment(commentId) {
  if (!editCommentContent.value.trim()) return
  submittingComment.value = true
  try {
    const { data } = await communityAPI.updateComment(commentId, { content: editCommentContent.value.trim() })
    const idx = comments.value.findIndex(c => c.id === commentId)
    if (idx !== -1) comments.value[idx] = data
    cancelEditComment()
  } catch {
    alert('댓글 수정에 실패했어요.')
  } finally {
    submittingComment.value = false
  }
}

async function deleteComment(commentId) {
  if (!confirm('댓글을 삭제할까요?')) return
  try {
    await communityAPI.deleteComment(commentId)
    comments.value = comments.value.filter(c => c.id !== commentId)
  } catch {
    alert('댓글 삭제에 실패했어요.')
  }
}

onMounted(fetchPost)
</script>

<style scoped>
.page-wrap {
  max-width: 840px;
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
  color: #6B5A45;
}
.breadcrumb a { color: #6B5A45; text-decoration: none; }
.breadcrumb a:hover { color: #D97706; }
.breadcrumb-title {
  color: #6B5A45;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}
.sep { font-size: 12px; }

/* State */
.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 16px;
  color: #6B5A45;
  font-size: 14px;
}
.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #D8C4A3;
  border-top-color: #D97706;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.btn-back {
  padding: 8px 20px;
  background: #D97706;
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
}

/* Post Card */
.post-card {
  background: #FFFDF7;
  border: 1px solid #D8C4A3;
  border-radius: 16px;
  overflow: hidden;
}

.post-header {
  padding: 28px 32px 20px;
  border-bottom: 1px solid #FFF0D6;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-meta-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cat-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
}
.cat-자유 { background: #FFF0D6; color: #D97706; }
.cat-공략 { background: #e6f0d8; color: #3d6018; }
.cat-파티원모집 { background: #fce8e4; color: #9b3030; }

.game-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6B5A45;
  background: #FFF0D6;
  border-radius: 6px;
  padding: 3px 8px;
}
.game-icon { width: 12px; height: 12px; }

.post-title {
  font-size: 22px;
  font-weight: 800;
  color: #3A2410;
  margin: 0;
  line-height: 1.4;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.author-link {
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
}
.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #D8C4A3;
}
.author-name {
  font-size: 13px;
  font-weight: 600;
  color: #3A2410;
}
.author-link:hover .author-name { color: #D97706; }
.dot { color: #c8c2b4; font-size: 12px; }
.post-date, .comment-meta { font-size: 13px; color: #6B5A45; }
.edited { font-size: 12px; color: #6B5A45; }

.post-actions {
  display: flex;
  gap: 8px;
}
.action-btn {
  padding: 5px 14px;
  border: 1px solid #D8C4A3;
  border-radius: 7px;
  background: #FFFDF7;
  font-size: 13px;
  color: #6B5A45;
  cursor: pointer;
  transition: all 0.15s;
}
.action-btn:hover { border-color: #D97706; color: #3A2410; }
.action-btn--danger { color: #c53030; }
.action-btn--danger:hover { border-color: #fc8181; background: #fff5f5; }

/* Post Body */
.post-body {
  padding: 28px 32px;
  min-height: 160px;
}
.content-line {
  font-size: 15px;
  line-height: 1.8;
  color: #3A2410;
  margin: 0 0 4px;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Comments Section */
.comments-section {
  background: #FFFDF7;
  border: 1px solid #D8C4A3;
  border-radius: 16px;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comments-title {
  font-size: 16px;
  font-weight: 700;
  color: #3A2410;
  margin: 0;
}
.comments-count {
  color: #D97706;
  margin-left: 4px;
}

.comments-empty {
  text-align: center;
  font-size: 14px;
  color: #6B5A45;
  padding: 24px 0;
}

.comment-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.comment-item {
  padding: 16px 0;
  border-bottom: 1px solid #FFF0D6;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.comment-item:last-child { border-bottom: none; }

.comment-author-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.comment-author-link {
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
}
.comment-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #D8C4A3;
}
.comment-author-name {
  font-size: 13px;
  font-weight: 600;
  color: #3A2410;
}
.comment-author-link:hover .comment-author-name { color: #D97706; }
.comment-date { font-size: 12px; color: #6B5A45; margin-left: 4px; }

.comment-actions {
  display: flex;
  gap: 6px;
  margin-left: auto;
}
.comment-action-btn {
  padding: 3px 10px;
  border: 1px solid #D8C4A3;
  border-radius: 6px;
  background: #FFFDF7;
  font-size: 12px;
  color: #6B5A45;
  cursor: pointer;
  transition: all 0.15s;
}
.comment-action-btn:hover { border-color: #D97706; }
.comment-action-btn--danger { color: #c53030; }
.comment-action-btn--danger:hover { border-color: #fc8181; background: #fff5f5; }

.comment-content {
  font-size: 14px;
  color: #3A2410;
  line-height: 1.7;
  margin: 0;
  padding-left: 34px;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Comment Input */
.comment-input-wrap { padding-top: 8px; }

.comment-input-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.my-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #D8C4A3;
  flex-shrink: 0;
  margin-top: 2px;
}
.comment-input-box { flex: 1; display: flex; flex-direction: column; gap: 8px; }

.comment-textarea {
  width: 100%;
  border: 1px solid #D8C4A3;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  color: #3A2410;
  font-family: inherit;
  line-height: 1.6;
  resize: none;
  outline: none;
  background: #FFF7E6;
  box-sizing: border-box;
  transition: border-color 0.15s, background 0.15s;
}
.comment-textarea:focus { border-color: #D97706; background: #fff; }

.comment-edit-box { padding-left: 34px; display: flex; flex-direction: column; gap: 8px; }
.comment-edit-actions { display: flex; gap: 6px; justify-content: flex-end; }

.btn-cancel-sm, .btn-save-sm {
  padding: 5px 14px;
  border-radius: 7px;
  font-size: 13px;
  cursor: pointer;
}
.btn-cancel-sm {
  border: 1px solid #D8C4A3;
  background: #FFFDF7;
  color: #6B5A45;
}
.btn-save-sm {
  border: none;
  background: #D97706;
  color: #fff;
  font-weight: 600;
}
.btn-save-sm:disabled { opacity: 0.6; cursor: not-allowed; }

.comment-submit-row { display: flex; justify-content: flex-end; }
.btn-comment {
  padding: 8px 20px;
  background: #D97706;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-comment:hover:not(:disabled) { background: #B45309; }
.btn-comment:disabled { opacity: 0.5; cursor: not-allowed; }

.comment-login-prompt {
  text-align: center;
  font-size: 14px;
  color: #6B5A45;
  padding: 20px 0;
  border: 1px dashed #D8C4A3;
  border-radius: 10px;
}
.comment-login-prompt a { color: #D97706; font-weight: 600; text-decoration: none; }
.comment-login-prompt a:hover { text-decoration: underline; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(58,36,16,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 24px;
}
.modal {
  background: #FFFDF7;
  border-radius: 16px;
  padding: 28px 32px;
  width: 100%;
  max-width: 640px;
  box-shadow: 0 20px 60px rgba(58,36,16,0.2);
  max-height: 90vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.modal-header h2 { font-size: 18px; font-weight: 700; color: #3A2410; margin: 0; }
.modal-close { background: none; border: none; cursor: pointer; color: #6B5A45; padding: 4px; }
.modal-close svg { width: 20px; height: 20px; }

.modal-form { display: flex; flex-direction: column; gap: 16px; }
.form-row { display: flex; gap: 12px; }
.form-field { display: flex; flex-direction: column; gap: 6px; }
.form-field--category { width: 140px; flex-shrink: 0; }
.form-field--title { flex: 1; }
.form-field label { font-size: 13px; font-weight: 600; color: #6B5A45; }
.form-field input,
.form-field select,
.form-field textarea {
  border: 1px solid #D8C4A3;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  color: #3A2410;
  outline: none;
  background: #fff;
  font-family: inherit;
  transition: border-color 0.15s;
}
.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus { border-color: #D97706; }
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
  border: 1px solid #D8C4A3;
  border-radius: 8px;
  background: #FFFDF7;
  color: #6B5A45;
  font-size: 14px;
  cursor: pointer;
}
.btn-save {
  padding: 9px 24px;
  border: none;
  border-radius: 8px;
  background: #D97706;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

/* 이미지 행 (연속 이미지 가로 배치) */
.image-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0;
  align-items: flex-start;
}
.image-wrap {
  flex-shrink: 0;
  box-sizing: border-box;
  min-width: 60px;
}
.post-image {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 8px;
  cursor: zoom-in;
}

/* 라이트박스 */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: zoom-out;
  padding: 24px;
}
.lightbox-img {
  max-width: 100%;
  max-height: 90vh;
  border-radius: 8px;
  object-fit: contain;
}

</style>
