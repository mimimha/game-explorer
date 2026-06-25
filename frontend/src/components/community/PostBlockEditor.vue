<template>
  <div class="block-editor">
    <template v-for="(block, i) in blocks" :key="block.id">

      <!-- 텍스트 블록 -->
      <textarea
        v-if="block.type === 'text'"
        v-model="block.value"
        class="block-textarea"
        :placeholder="i === 0 ? '내용을 입력하세요' : '계속 작성하세요...'"
        @input="e => autoResize(e.target)"
        @focus="e => autoResize(e.target)"
      />

      <!-- 이미지 블록 -->
      <div v-else class="image-block">
        <img :src="block.preview || block.url" class="block-img" />
        <button type="button" class="remove-img-btn" @click="removeImage(i)" title="이미지 삭제">×</button>
      </div>

    </template>

    <!-- 사진 추가 버튼: 항상 하단에 하나만 -->
    <button
      v-if="imageCount < MAX_IMAGES"
      type="button"
      class="add-photo-btn"
      @click="fileRef?.click()"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <path stroke-linecap="round" stroke-linejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z"/>
      </svg>
      사진 추가
    </button>

    <input ref="fileRef" type="file" accept="image/*" style="display:none" @change="onFileChosen" />
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const MAX_IMAGES = 5

// 항상 텍스트로 시작하고 텍스트로 끝나는 구조 유지
// [text] or [text, img, text] or [text, img, text, img, text] ...
const blocks = ref([{ id: uid(), type: 'text', value: '' }])
const fileRef = ref(null)

const imageCount = computed(() => blocks.value.filter(b => b.type === 'image').length)

function uid() {
  return Math.random().toString(36).slice(2)
}

function autoResize(el) {
  if (!el) return
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

// 파일 선택 시: 마지막 텍스트 블록 뒤에 이미지 + 새 텍스트 블록 추가
function onFileChosen(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return

  const preview = URL.createObjectURL(file)
  const imgBlock  = { id: uid(), type: 'image', file, preview, existingId: null, url: null }
  const textBlock = { id: uid(), type: 'text', value: '' }

  // 마지막 블록이 텍스트임을 보장 (항상 그래야 함)
  blocks.value.push(imgBlock, textBlock)

  nextTick(() => {
    // 새 텍스트 블록으로 포커스
    const textareas = document.querySelectorAll('.block-textarea')
    textareas[textareas.length - 1]?.focus()
  })
}

// 이미지 제거 → 앞뒤 텍스트 병합
function removeImage(imgIdx) {
  const block = blocks.value[imgIdx]
  if (block.preview) URL.revokeObjectURL(block.preview)

  const before = blocks.value[imgIdx - 1]
  const after  = blocks.value[imgIdx + 1]
  const merged = [before?.value, after?.value].filter(v => v).join('\n')

  // [text_before, image, text_after] → [text_merged]
  blocks.value.splice(imgIdx - 1, 3, { id: uid(), type: 'text', value: merged })

  nextTick(() => {
    document.querySelectorAll('.block-textarea').forEach(autoResize)
  })
}

// ── 공개 API ─────────────────────────────────────────────────

// 수정 모드 초기화: 기존 content + images 로 블록 복원
function init(content, images = []) {
  const imageMap = Object.fromEntries((images ?? []).map(img => [img.id, img.url]))
  const lines = (content ?? '').split('\n')
  const result = []
  let textBuf = []

  for (const line of lines) {
    const m = line.match(/^\[IMAGE:(\d+)\]$/)
    if (m) {
      result.push({ id: uid(), type: 'text', value: textBuf.join('\n') })
      textBuf = []
      const url = imageMap[parseInt(m[1])]
      if (url) result.push({ id: uid(), type: 'image', file: null, preview: null, existingId: parseInt(m[1]), url })
    } else {
      textBuf.push(line)
    }
  }
  result.push({ id: uid(), type: 'text', value: textBuf.join('\n') })

  // 마지막이 텍스트가 아니면 추가
  if (result[result.length - 1]?.type !== 'text') {
    result.push({ id: uid(), type: 'text', value: '' })
  }

  blocks.value = result.length ? result : [{ id: uid(), type: 'text', value: '' }]

  nextTick(() => document.querySelectorAll('.block-textarea').forEach(autoResize))
}

function getBlocks() { return blocks.value }

function cleanup() {
  blocks.value.forEach(b => { if (b.preview) URL.revokeObjectURL(b.preview) })
}

function reset() {
  cleanup()
  blocks.value = [{ id: uid(), type: 'text', value: '' }]
}

defineExpose({ init, getBlocks, cleanup, reset })
</script>

<style scoped>
.block-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.block-textarea {
  width: 100%;
  min-height: 80px;
  border: 1px solid #D8C4A3;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 14px;
  color: #3A2410;
  font-family: inherit;
  line-height: 1.7;
  resize: none;
  outline: none;
  background: #fff;
  box-sizing: border-box;
  transition: border-color 0.15s;
  overflow: hidden;
}
.block-textarea:focus { border-color: #D97706; }

/* 이미지 블록 */
.image-block {
  position: relative;
  align-self: flex-start;
  max-width: 100%;
}
.block-img {
  display: block;
  max-width: 100%;
  max-height: 320px;
  border-radius: 10px;
  border: 1px solid #D8C4A3;
  object-fit: contain;
}
.remove-img-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(58, 36, 16, 0.65);
  color: #fff;
  border: none;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(2px);
  transition: background 0.15s;
}
.remove-img-btn:hover { background: rgba(155, 48, 48, 0.85); }

/* 사진 추가 버튼 */
.add-photo-btn {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 1.5px dashed #D8C4A3;
  border-radius: 8px;
  background: #FFF7E6;
  color: #6B5A45;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
  margin-top: 2px;
}
.add-photo-btn:hover {
  border-color: #D97706;
  color: #D97706;
  background: #FFF0D6;
}
.add-photo-btn svg { width: 16px; height: 16px; flex-shrink: 0; }
</style>
