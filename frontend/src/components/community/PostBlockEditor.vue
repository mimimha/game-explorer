<template>
  <div class="block-editor">
    <div
      ref="editorEl"
      class="editor-content"
      contenteditable="true"
      data-placeholder="내용을 입력하세요"
      @paste.prevent="onPaste"
      @blur="saveRange"
    />

    <button
      v-if="imgCount < MAX_IMAGES"
      type="button"
      class="add-photo-btn"
      @mousedown.prevent
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
import { ref } from 'vue'

const MAX_IMAGES = 5
const editorEl = ref(null)
const fileRef  = ref(null)
const imgCount = ref(0)
const pendingFiles = ref([])

let lastRange = null

function uid() { return Math.random().toString(36).slice(2) }

// ── 커서 저장 ─────────────────────────────────────────────────

function saveRange() {
  const sel = window.getSelection()
  if (sel && sel.rangeCount > 0 && editorEl.value?.contains(sel.anchorNode)) {
    lastRange = sel.getRangeAt(0).cloneRange()
  }
}

// ── 파일 선택 ─────────────────────────────────────────────────

function onFileChosen(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file || imgCount.value >= MAX_IMAGES) return

  const fid = uid()
  const preview = URL.createObjectURL(file)
  pendingFiles.value.push({ id: fid, file, preview })

  const wrapper = makeImgEl(null, preview, fid, 100)
  insertIntoEditor(wrapper)
  imgCount.value++
}

function insertIntoEditor(node) {
  const editor = editorEl.value
  const sel = window.getSelection()
  const br = document.createElement('br')

  const hasEditorCursor = sel && sel.rangeCount > 0 && editor.contains(sel.anchorNode)
  const range = hasEditorCursor
    ? sel.getRangeAt(0)
    : (lastRange && editor.contains(lastRange.startContainer) ? lastRange : null)

  const frag = document.createDocumentFragment()
  frag.appendChild(node)
  frag.appendChild(br)

  if (range) {
    range.collapse(false)
    range.insertNode(frag)
    const r = document.createRange()
    r.setStartAfter(br)
    r.collapse(true)
    sel.removeAllRanges()
    sel.addRange(r)
  } else {
    editor.appendChild(node)
    editor.appendChild(br)
    const r = document.createRange()
    r.setStartAfter(br)
    r.collapse(true)
    sel?.removeAllRanges()
    sel?.addRange(r)
  }

  editor.focus()
  lastRange = null
}

// ── 이미지 DOM 생성 ───────────────────────────────────────────

function makeImgEl(existingId, src, newFileId, widthPct = 100) {
  const div = document.createElement('div')
  div.className = 'pbe-img-block'
  div.contentEditable = 'false'
  div.style.width = widthPct + '%'
  div.dataset.widthPct = String(widthPct)
  if (existingId != null) div.dataset.existingId = String(existingId)
  if (newFileId) div.dataset.newFileId = newFileId

  const img = document.createElement('img')
  img.src = src
  img.className = 'pbe-block-img'

  // × 삭제 버튼
  const delBtn = document.createElement('button')
  delBtn.type = 'button'
  delBtn.className = 'pbe-remove-btn'
  delBtn.textContent = '×'
  delBtn.addEventListener('click', () => {
    if (newFileId) {
      const idx = pendingFiles.value.findIndex(f => f.id === newFileId)
      if (idx !== -1) {
        URL.revokeObjectURL(pendingFiles.value[idx].preview)
        pendingFiles.value.splice(idx, 1)
      }
    }
    div.remove()
    imgCount.value = Math.max(0, imgCount.value - 1)
  })

  // 리사이즈 핸들 (오른쪽 하단)
  const handle = document.createElement('div')
  handle.className = 'pbe-resize-handle'
  handle.innerHTML = `<svg viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.5">
    <path d="M2 8 L8 2 M5 8 L8 5"/>
  </svg>`

  handle.addEventListener('mousedown', (e) => {
    e.preventDefault()
    e.stopPropagation()
    const startX  = e.clientX
    const startW  = div.offsetWidth

    function onMove(ev) {
      const editorContentW = (editorEl.value?.clientWidth ?? 600) - 28 // 패딩 14+14
      const dx   = ev.clientX - startX
      const newW = Math.max(80, Math.min(editorContentW, startW + dx))
      const pct  = Math.round((newW / editorContentW) * 100)
      div.style.width = pct + '%'
      div.dataset.widthPct = String(pct)
    }
    function onUp() {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
    }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
  })

  div.appendChild(img)
  div.appendChild(delBtn)
  div.appendChild(handle)
  return div
}

// ── 직렬화 ────────────────────────────────────────────────────

function getBlocks() {
  const editor = editorEl.value
  if (!editor) return [{ type: 'text', value: '' }]

  const blocks = []
  let buf = []

  function flush() {
    const val = buf.join('').replace(/^\n+|\n+$/g, '')
    blocks.push({ type: 'text', value: val })
    buf = []
  }

  function walk(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      buf.push(node.textContent)
      return
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return

    const tag = node.nodeName

    if (node.classList?.contains('pbe-img-block')) {
      flush()
      const existingId = node.dataset.existingId ? parseInt(node.dataset.existingId) : null
      const newFileId  = node.dataset.newFileId  || null
      const widthPct   = node.dataset.widthPct   ? parseInt(node.dataset.widthPct)   : 100
      const file = newFileId ? (pendingFiles.value.find(f => f.id === newFileId)?.file ?? null) : null
      blocks.push({ type: 'image', existingId, file, widthPct, preview: null, url: null })
      return
    }

    if (tag === 'BR') {
      if (node.previousSibling?.classList?.contains('pbe-img-block')) return
      const parent = node.parentNode
      const isOnlyChild = parent !== editor && parent.childNodes.length === 1
      if (!isOnlyChild) buf.push('\n')
      return
    }

    if (tag === 'DIV' || tag === 'P') {
      if (buf.length > 0 || blocks.length > 0) buf.push('\n')
      for (const c of node.childNodes) walk(c)
      return
    }

    for (const c of node.childNodes) walk(c)
  }

  for (const c of editor.childNodes) walk(c)
  flush()

  return blocks
}

// ── 수정 모드 초기화 ──────────────────────────────────────────
// content 형식: [IMAGE:id] 또는 [IMAGE:id:widthPct]

function init(content, images = []) {
  cleanup()
  const editor = editorEl.value
  if (!editor) return
  editor.innerHTML = ''
  imgCount.value = 0

  const imageMap = Object.fromEntries((images ?? []).map(img => [img.id, img.url]))
  const lines = (content ?? '').split('\n')

  lines.forEach((line, i) => {
    const m = line.match(/^\[IMAGE:(\d+)(?::(\d+))?\]$/)
    if (m) {
      const imgId    = parseInt(m[1])
      const widthPct = m[2] ? parseInt(m[2]) : 100
      const url      = imageMap[imgId]
      if (url) {
        editor.appendChild(makeImgEl(imgId, url, null, widthPct))
        editor.appendChild(document.createElement('br'))
        imgCount.value++
      }
    } else {
      editor.appendChild(document.createTextNode(line))
      if (i < lines.length - 1) editor.appendChild(document.createElement('br'))
    }
  })
}

function cleanup() {
  pendingFiles.value.forEach(f => URL.revokeObjectURL(f.preview))
  pendingFiles.value = []
}

function reset() {
  cleanup()
  const editor = editorEl.value
  if (editor) editor.innerHTML = ''
  imgCount.value = 0
  lastRange = null
}

function onPaste(e) {
  const text = e.clipboardData?.getData('text/plain') ?? ''
  const sel = window.getSelection()
  if (!sel?.rangeCount) return
  const range = sel.getRangeAt(0)
  range.deleteContents()
  const textNode = document.createTextNode(text)
  range.insertNode(textNode)
  range.setStartAfter(textNode)
  range.collapse(true)
  sel.removeAllRanges()
  sel.addRange(range)
}

defineExpose({ init, getBlocks, cleanup, reset })
</script>

<!-- 스코프 스타일: Vue 템플릿 요소 -->
<style scoped>
.block-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.editor-content {
  min-height: 180px;
  border: 1px solid #D8C4A3;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 14px;
  color: #3A2410;
  font-family: inherit;
  line-height: 1.7;
  outline: none;
  background: #fff;
  word-break: break-word;
  overflow: hidden;
  transition: border-color 0.15s;
  cursor: text;
  box-sizing: border-box;
}
.editor-content:focus { border-color: #D97706; }
.editor-content:empty::before {
  content: attr(data-placeholder);
  color: #c8c2b4;
  pointer-events: none;
}

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
}
.add-photo-btn:hover {
  border-color: #D97706;
  color: #D97706;
  background: #FFF0D6;
}
.add-photo-btn svg { width: 16px; height: 16px; flex-shrink: 0; }
</style>

<!-- 전역 스타일: JS로 생성되는 동적 요소 -->
<style>
.pbe-img-block {
  display: block;
  position: relative;
  max-width: 100%;
  box-sizing: border-box;
  margin: 8px 0;
  user-select: none;
  -webkit-user-select: none;
}

.pbe-block-img {
  display: block;
  width: 100%;
  height: auto;
  max-width: 100%;
  border-radius: 8px;
  box-sizing: border-box;
  pointer-events: none;
}

/* × 삭제 버튼 */
.pbe-remove-btn {
  position: absolute;
  top: 8px;
  right: 36px;
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
  opacity: 0;
}
.pbe-img-block:hover .pbe-remove-btn { opacity: 1; }
.pbe-remove-btn:hover { background: rgba(155, 48, 48, 0.85); }

/* 리사이즈 핸들 */
.pbe-resize-handle {
  position: absolute;
  bottom: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  border-radius: 5px;
  background: rgba(58, 36, 16, 0.6);
  color: #fff;
  cursor: se-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.15s, background 0.15s;
}
.pbe-img-block:hover .pbe-resize-handle { opacity: 1; }
.pbe-resize-handle:hover { background: rgba(217, 119, 6, 0.85); }
.pbe-resize-handle svg { width: 12px; height: 12px; stroke: #fff; }
</style>
