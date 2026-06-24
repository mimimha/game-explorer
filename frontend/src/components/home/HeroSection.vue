<template>
  <section class="hero">
    <div class="hero-inner">
      <!-- 좌: 텍스트 -->
      <div class="hero-text">
        <h1>새로운 세계로의 탐험,<br />방구석 탐험대와 함께</h1>
        <p>
          당신의 취향에 맞는 인디 게임을 추천받고<br />
          다양한 게임을 탐험해보세요.
        </p>
        <RouterLink to="/explore" class="cta">탐험 시작하기</RouterLink>
      </div>

      <!-- 우: 어드벤처 맵 -->
      <div class="hero-map">
        <div class="theme-tag" :style="{ borderColor: STEPS[step].accent, color: STEPS[step].accent }">
          <span class="dot" :style="{ background: STEPS[step].accent }"></span>
          <Transition name="swap" mode="out-in">
            <span :key="step">탐험지 · {{ STEPS[step].label }}</span>
          </Transition>
        </div>

        <svg viewBox="0 0 640 380" class="map-svg" role="img" aria-label="탐험 지도">
          <defs>
            <clipPath id="parchment">
              <path :d="MAP_SILHOUETTE" />
            </clipPath>
          </defs>

          <!-- 양피지 지도 실루엣 (구불구불한 윤곽선) -->
          <path :d="MAP_SILHOUETTE" class="parchment" />

          <!-- 지도 안쪽 장식 (실루엣으로 클립) -->
          <g clip-path="url(#parchment)">
            <!-- 등고선 느낌 물결 -->
            <path class="contour" d="M 70 300 C 200 280, 360 318, 590 296" />
            <path class="contour" d="M 80 250 C 220 232, 380 262, 580 244" />

            <!-- 위에서 본 지도 산 기호 (작게 흩뿌림) -->
            <g class="map-mtn">
              <path d="M-10,4 L-3,-8 L2,-2 L7,-10 L12,4 Z" transform="translate(110 300)" />
              <path d="M-8,4 L-2,-7 L4,4 Z" transform="translate(135 305)" />
              <path d="M-10,4 L-3,-9 L2,-2 L7,-11 L12,4 Z" transform="translate(225 130)" />
              <path d="M-8,4 L-2,-7 L4,4 Z" transform="translate(248 135)" />
              <path d="M-11,4 L-4,-10 L1,-3 L7,-12 L12,4 Z" transform="translate(400 300)" />
              <path d="M-8,4 L-2,-8 L4,4 Z" transform="translate(425 305)" />
              <path d="M-9,4 L-2,-8 L3,-2 L8,-9 L11,4 Z" transform="translate(515 150)" />
            </g>

            <!-- 지도 나무 기호 -->
            <g class="map-tree">
              <g transform="translate(180 250)"><path class="trunk" d="M0,5 v4"/><circle cy="0" r="6"/></g>
              <g transform="translate(330 110)"><path class="trunk" d="M0,5 v4"/><circle cy="0" r="6"/></g>
              <g transform="translate(470 305)"><path class="trunk" d="M0,5 v4"/><circle cy="0" r="6"/></g>
              <g transform="translate(560 290)"><path class="trunk" d="M0,5 v4"/><circle cy="0" r="6"/></g>
            </g>
          </g>

          <!-- 점선 루트 (핀이 따라 이동) -->
          <path ref="pathEl" class="trail" :d="ROUTE"
            fill="none" stroke="#9a7b54" stroke-width="2.6"
            stroke-linecap="round" stroke-dasharray="2 9" />

          <!-- 지점 (현재만 보임) -->
          <g v-for="(p, i) in POINTS" :key="'pt' + i"
             class="node-grp" :class="{ active: step === i && !moving }">
            <circle :cx="p.x" :cy="p.y" r="14" class="node" />
            <text :x="p.x" :y="p.y + 4.5" class="node-num">{{ i + 1 }}</text>
          </g>

          <!-- 장르 오브젝트 (현재 지점만 등장) -->
          <g v-for="(s, i) in STEPS" :key="'obj' + i"
             class="genre-obj" :class="{ show: step === i && !moving }"
             :transform="`translate(${POINTS[i].x} ${POINTS[i].y - 56})`">
            <template v-if="s.key === 'adventure'">
              <path d="M0,-22 L4,-7 L-4,-7 Z" fill="#d2d7db" stroke="#9aa4ad" stroke-width="1.1"/>
              <line x1="-9" y1="-6" x2="9" y2="-6" stroke="#c9a44a" stroke-width="3" stroke-linecap="round"/>
              <line x1="0" y1="-6" x2="0" y2="11" stroke="#9a7b54" stroke-width="3" stroke-linecap="round"/>
              <circle cx="0" cy="12" r="2.6" fill="#c9a44a"/>
            </template>
            <template v-else-if="s.key === 'puzzle'">
              <line x1="6" y1="6" x2="15" y2="15" stroke="#7a6b54" stroke-width="4.2" stroke-linecap="round"/>
              <circle cx="-3" cy="-3" r="11" fill="rgba(255,255,255,0.5)" stroke="#5b86b0" stroke-width="3"/>
              <line x1="-8" y1="-3" x2="2" y2="-3" stroke="#5b86b0" stroke-width="1.5" stroke-linecap="round"/>
              <line x1="-3" y1="-8" x2="-3" y2="2" stroke="#5b86b0" stroke-width="1.5" stroke-linecap="round"/>
            </template>
            <template v-else-if="s.key === 'fantasy'">
              <line x1="-6" y1="16" x2="6" y2="-8" stroke="#8a6f4e" stroke-width="3" stroke-linecap="round"/>
              <path d="M8,-20 L11,-12 L8,-4 L5,-12 Z" fill="#8c7bc0"/>
              <path d="M1,-12 L8,-9.5 L15,-12 L8,-14.5 Z" fill="#a99ad4"/>
              <circle cx="-3" cy="3" r="1.5" fill="#b3a6dd"/>
              <circle cx="14" cy="-1" r="1.1" fill="#b3a6dd"/>
            </template>
            <template v-else>
              <path d="M-3,9 Q0,19 3,9 Z" fill="#e4b95b"/>
              <path d="M0,-18 C6.5,-10 6.5,3 4,8 L-4,8 C-6.5,3 -6.5,-10 0,-18 Z" fill="#eef1f3" stroke="#9aa4ad" stroke-width="1.3"/>
              <path d="M-4,4 L-9,13 L-4,9 Z" fill="#d98a5b"/>
              <path d="M4,4 L9,13 L4,9 Z" fill="#d98a5b"/>
              <circle cx="0" cy="-5" r="3" fill="#5b86b0"/>
            </template>
          </g>

          <!-- 이동하는 핀 -->
          <g class="pin" :style="{ transform: `translate(${pinX}px, ${pinY}px)` }">
            <line x1="0" y1="0" x2="0" y2="-30" stroke="#6b5b4a" stroke-width="2.6" stroke-linecap="round" />
            <path d="M0,-30 q20,4 22,10 q-2,6 -22,10 z" :fill="STEPS[step].accent" />
            <circle cx="0" cy="0" r="3.2" fill="#6b5b4a" />
          </g>

          <!-- 나침반 -->
          <g class="compass" transform="translate(582 330)">
            <circle r="24" fill="none" stroke="#b3a884" stroke-width="1.5" />
            <circle r="18" fill="none" stroke="#cfc6a8" stroke-width="1" />
            <path d="M0,-20 L5,0 L0,20 L-5,0 Z" fill="#a9c08f" stroke="#8a9a7b" stroke-width="0.8" />
            <path d="M-20,0 L0,5 L20,0 L0,-5 Z" fill="#e4d9af" stroke="#cbbf90" stroke-width="0.8" />
            <text x="0" y="-27" class="compass-n">N</text>
          </g>
        </svg>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { RouterLink } from 'vue-router'

// 구불구불한 양피지 지도 윤곽선
const MAP_SILHOUETTE =
  'M 44 70 C 130 48, 210 80, 300 60 C 388 42, 470 76, 560 58 ' +
  'C 606 50, 616 110, 602 150 C 590 196, 612 244, 596 296 ' +
  'C 588 330, 510 320, 420 332 C 330 344, 240 320, 158 334 ' +
  'C 92 344, 42 330, 48 280 C 30 232, 52 184, 40 134 ' +
  'C 32 100, 22 84, 44 70 Z'

// 핀이 따라 이동하는 곡선 루트
const ROUTE =
  'M 150 250 C 210 200, 250 175, 300 175 ' +
  'C 360 175, 405 215, 450 250 C 510 250, 545 190, 560 140'

const POINTS = [
  { x: 150, y: 250 },
  { x: 300, y: 175 },
  { x: 450, y: 250 },
  { x: 560, y: 140 },
]

const STEPS = [
  { key: 'adventure', label: '어드벤처', accent: '#6fa06a' },
  { key: 'puzzle',    label: '퍼즐',     accent: '#5b86b0' },
  { key: 'fantasy',   label: '판타지',   accent: '#8c7bc0' },
  { key: 'scifi',     label: 'SF · 사이버', accent: '#d98a5b' },
]

const step = ref(0)
const moving = ref(false)
const pinX = ref(POINTS[0].x)
const pinY = ref(POINTS[0].y)
const pathEl = ref(null)

let ptLen = []      // 각 지점의 path 길이 위치
let curLen = 0
let raf = null
let timer = null

// path 위에서 각 지점에 가장 가까운 길이 좌표 계산
function buildLengths() {
  const el = pathEl.value
  if (!el?.getTotalLength) return
  const L = el.getTotalLength()
  ptLen = POINTS.map(p => {
    let best = 0, bestD = Infinity
    for (let l = 0; l <= L; l += 2) {
      const pt = el.getPointAtLength(l)
      const d = (pt.x - p.x) ** 2 + (pt.y - p.y) ** 2
      if (d < bestD) { bestD = d; best = l }
    }
    return best
  })
  curLen = ptLen[0]
}

// 곡선을 따라 핀을 부드럽게 이동
function tweenTo(targetLen, dur = 900) {
  cancelAnimationFrame(raf)
  const el = pathEl.value
  if (!el?.getPointAtLength) return
  const startLen = curLen
  const t0 = performance.now()
  moving.value = true
  function frame(now) {
    const t = Math.min(1, (now - t0) / dur)
    const e = t < 0.5 ? 2 * t * t : 1 - ((-2 * t + 2) ** 2) / 2   // easeInOut
    curLen = startLen + (targetLen - startLen) * e
    const pt = el.getPointAtLength(curLen)
    pinX.value = pt.x; pinY.value = pt.y
    if (t < 1) raf = requestAnimationFrame(frame)
    else moving.value = false
  }
  raf = requestAnimationFrame(frame)
}

watch(step, (s) => tweenTo(ptLen[s]))

onMounted(() => {
  buildLengths()
  timer = setInterval(() => {
    step.value = step.value >= POINTS.length - 1 ? 0 : step.value + 1
  }, 2300)
})
onBeforeUnmount(() => { clearInterval(timer); cancelAnimationFrame(raf) })
</script>

<style scoped>
.hero {
  position: relative; border-radius: 16px; overflow: hidden;
  margin: 24px 40px 0;
  background: linear-gradient(135deg, #f3f5ec 0%, #e7efdd 100%);
}
.hero-inner {
  position: relative; z-index: 1;
  display: grid; grid-template-columns: minmax(280px, 1fr) 1.3fr;
  align-items: center; gap: 24px; padding: 44px 48px;
}
.hero-text h1 {
  font-size: 34px; font-weight: 800; line-height: 1.3;
  color: #2f3d29; letter-spacing: -0.01em; margin: 0;
}
.hero-text p { margin: 16px 0 0; font-size: 15px; line-height: 1.7; color: #5d6b4f; }
.cta {
  display: inline-block; margin-top: 22px; padding: 12px 22px;
  border-radius: 10px; background: #5b7553; color: #fff;
  font-size: 14px; font-weight: 700; text-decoration: none;
  transition: background 0.15s, transform 0.15s;
}
.cta:hover { background: #4a6244; transform: translateY(-1px); }

.hero-map { position: relative; width: 100%; }
.map-svg { width: 100%; height: auto; display: block; }

.theme-tag {
  position: absolute; top: 6px; left: 6px; z-index: 2;
  display: inline-flex; align-items: center; gap: 7px;
  padding: 5px 12px; border-radius: 999px;
  background: rgba(255,255,255,0.8); border: 1.5px solid;
  font-size: 12px; font-weight: 700; backdrop-filter: blur(3px);
}
.theme-tag .dot { width: 8px; height: 8px; border-radius: 50%; }
.swap-enter-active, .swap-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.swap-enter-from { opacity: 0; transform: translateY(4px); }
.swap-leave-to { opacity: 0; transform: translateY(-4px); }

/* 양피지 지도 */
.parchment {
  fill: #f5efdd;
  stroke: #b9a77f;
  stroke-width: 2.5;
  stroke-linejoin: round;
}
.contour { fill: none; stroke: #d9cca6; stroke-width: 1.4; stroke-dasharray: 1 6; stroke-linecap: round; }

/* 지도 산·나무 기호 (위에서 본 라인아트) */
.map-mtn path { fill: #fbf7ea; stroke: #9c8c63; stroke-width: 1.5; stroke-linejoin: round; }
.map-tree circle { fill: #b6c79a; stroke: #84996a; stroke-width: 1.2; }
.map-tree .trunk { stroke: #9c8463; stroke-width: 1.6; stroke-linecap: round; }

/* 루트 */
.trail { opacity: 0.85; }

/* 지점 (현재만 보임) */
.node-grp { opacity: 0; transition: opacity 0.4s ease; }
.node-grp.active { opacity: 1; }
.node { fill: #fff; stroke: #5b7553; stroke-width: 2.5; }
.node-num { font-size: 13px; font-weight: 800; fill: #4a5d42; text-anchor: middle; }

/* 장르 오브젝트 (현재만 등장) */
.genre-obj {
  opacity: 0; transform: scale(0.4);
  transform-box: fill-box; transform-origin: center;
  transition: opacity 0.4s ease, transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.genre-obj.show { opacity: 1; transform: scale(1.15); }

/* 이동 핀 */
.pin { will-change: transform; }

/* 나침반 */
.compass { animation: sway 6s ease-in-out infinite; }
.compass-n { font-size: 9px; font-weight: 700; fill: #9a8c6a; text-anchor: middle; }
@keyframes sway {
  0%, 100% { transform: translate(582px, 330px) rotate(-3deg); }
  50%      { transform: translate(582px, 330px) rotate(3deg); }
}

@media (max-width: 900px) {
  .hero-inner { grid-template-columns: 1fr; }
  .hero-map { max-width: 480px; margin: 8px auto 0; }
}
@media (max-width: 600px) {
  .hero { margin: 16px 20px 0; }
  .hero-inner { padding: 28px 24px; }
  .hero-text h1 { font-size: 26px; }
}
</style>
