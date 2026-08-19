# Frontend

방구석 탐험대의 Vue 3 기반 SPA(Single Page Application)입니다. 자연어 AI 추천, 조건 필터링, 게임 상세 탐색, 커뮤니티와 사용자 활동 흐름을 담당합니다.

![AI 추천 및 검색](../docs/screenshots/추천%20및%20검색%20기능.jpg)

## 기술 스택

- **Vue 3** (Composition API)
- **Pinia** — 전역 상태 관리
- **Vue Router** — SPA 라우팅
- **Axios** — HTTP 통신

---

## 실행

백엔드 서버를 먼저 `http://127.0.0.1:8000`에서 실행한 뒤, 아래 명령을 실행한다.

```powershell
Copy-Item .env.example .env
npm install
npm run dev
```

`frontend/.env`에는 백엔드 API 주소를 설정한다.

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

개발 서버는 기본적으로 `http://127.0.0.1:5173`에서 열린다.

### 빌드

```powershell
npm run build
npm run preview
```

프로덕션 빌드 결과는 `dist/`에 생성됩니다.

---

## 프로젝트 구조

```
src/
├── views/          # 페이지 단위 컴포넌트
├── components/     # 재사용 UI 컴포넌트
├── stores/         # Pinia 전역 상태
├── api/            # Axios 기반 서비스 레이어
└── router/         # Vue Router
```

---

## 페이지 (views/)

| 페이지 | 경로 | 설명 |
|---|---|---|
| HomeView | `/` | 메인 홈 (추천·할인·신작 게임 카드) |
| ExploreView | `/explore` | 게임 탐색 (AI 추천 + 필터 검색) |
| GamedetailView | `/games/:id` | 게임 상세 (정보·영상·스크린샷, 파일명은 현재 구현 기준) |
| CommunityView | `/community` | 커뮤니티 게시판 목록 |
| PostDetailView | `/community/:postId` | 게시글 상세 및 댓글 |
| ProfileView | `/profile`, `/users/:userId` | 마이페이지 및 유저 프로필 |
| WishlistView | `/wishlist` | 찜 목록 (로그인 필요) |
| LoginView | `/login` | 로그인 |
| RegisterView | `/register` | 회원가입 |
| ErrorView | `/*` | 404 에러 |

---

## 컴포넌트 (components/)

### common/ — 공통
| 컴포넌트 | 설명 |
|---|---|
| GameSuggestDropdown | 검색어 자동완성 드롭다운 |
| NotificationBubble | 상단 알림 배지 |
| Pagination | 페이지 이동 버튼 |
| ToastAlert | 알림 토스트 메시지 |

### home/ — 홈
| 컴포넌트 | 설명 |
|---|---|
| HeroSection | 메인 배너 영역 |
| GameCard | 게임 카드 (썸네일·가격·평점) |
| GameCardList | 게임 카드 그리드 목록 |
| GameCardRow | 게임 카드 가로 스크롤 행 |
| SectionHeader | 섹션 제목 |
| FooterSection | 푸터 |

### explore/ — 탐색
| 컴포넌트 | 설명 |
|---|---|
| AiRecommendPanel | AI 자연어 추천 입력 패널 |
| SearchPanel | 키워드 + 필터 검색 패널 |
| GameResultGrid | 검색 결과 게임 그리드 |
| RecentHistory | 최근 AI 추천 기록 태그 |
| EmptyState | 결과 없음 안내 |
| FilterChipGroup | 필터 칩 그룹 UI |

### game-detail/ — 게임 상세
| 컴포넌트 | 설명 |
|---|---|
| GameInfoPanel | 게임 메타 정보 (장르·플랫폼·가격 등) |
| GameDescription | 게임 설명 (한국어 우선) |
| GameMediaGallery | 스크린샷 갤러리 |
| GameVideos | YouTube 영상 목록 (Lazy Loading) |

### profile/ — 프로필
| 컴포넌트 | 설명 |
|---|---|
| ProfileHeader | 프로필 상단 (아바타·닉네임·팔로우) |
| ProfileStats | 팔로워·팔로잉 수치 |
| MedalSection | 획득 메달 목록 |
| MedalBadge | 메달 배지 단위 |
| WishlistSection | 찜한 게임 목록 |
| AiHistorySection | AI 추천 기록 |
| MyPostsSection | 내가 쓴 게시글 목록 |

### community/ — 커뮤니티
| 컴포넌트 | 설명 |
|---|---|
| PostBlockEditor | 게시글 작성 에디터 |

---

## 상태 관리 (stores/)

| 스토어 | 역할 |
|---|---|
| **auth** | 로그인 상태·토큰 관리. `localStorage`에 토큰 저장해 새로고침 후에도 유지 |
| **explore** | 탐색 페이지 검색 상태(키워드·필터·페이지) 임시 저장. 상세 페이지 뒤로가기 시 복원에 사용 |
| **notifications** | 알림 갱신 신호 관리. 새 알림 발생 시 어느 컴포넌트에서든 배지 즉시 업데이트 |

### 탐색 상태 복원 흐름

```text
ExploreView에서 검색
  → 검색어·필터·정렬·페이지를 explore store에 저장
  → 게임 상세 페이지 이동
  → 뒤로가기
  → 저장된 조건으로 서버 재조회
  → 이전 탐색 맥락 복원
```

검색 결과 전체를 전역에 장기 보관하지 않고 재조회에 필요한 조건만 저장해 상태 복잡도를 줄였습니다.

---

## API 레이어 (api/)

### client.js
- Axios 인스턴스 생성 및 공통 설정
- 요청 인터셉터: 매 요청마다 토큰 자동 첨부
- 응답 인터셉터: 401 수신 시 자동 로그아웃 처리

### endpoints.js
- 백엔드 API 경로를 한 곳에서 관리
- 동적 경로는 함수로 정의 (예: `detail: (gameId) => /games/${gameId}/`)

### services.js
- endpoints + axios를 묶은 호출 함수 모음
- 컴포넌트에서 `gameAPI.list()`, `recommendAPI.create()` 형태로 사용

| 서비스 | 담당 |
|---|---|
| authAPI | 로그인·로그아웃·회원가입 |
| accountAPI | 프로필 조회·수정·팔로우 |
| gameAPI | 게임 목록·상세·영상·필터 옵션·자동완성 |
| wishlistAPI | 찜 추가·해제·목록 |
| communityAPI | 게시글·댓글·이미지 CRUD |
| recommendAPI | AI 추천 요청·기록 |
| notificationAPI | 알림 조회·읽음·삭제 |

API 경로, HTTP 클라이언트, 도메인 호출 함수를 분리해 컴포넌트에서 URL 문자열과 인증 처리 코드를 제거했습니다. 엔드포인트가 바뀌어도 수정 범위를 API 계층으로 제한할 수 있습니다.

### 인증 처리

- 로그인 토큰과 사용자 정보를 Pinia `auth` store에서 관리
- 토큰을 `localStorage`에 저장해 새로고침 후 인증 상태 복원
- Axios 요청 인터셉터에서 인증 토큰 자동 첨부
- 401 응답 시 저장된 인증 정보를 제거하고 로그인 상태 초기화
- 프로필과 찜 경로에 `requiresAuth` 메타데이터 지정

현재 라우터 전역 가드는 연결되어 있지 않아, 최종 권한 검사는 백엔드 API가 담당합니다. 클라이언트 전역 가드 추가는 개선 과제로 남아 있습니다.

---

## 주요 구현 포인트

### 필터 검색
- 필터 칩 클릭 즉시 `watch`로 자동 검색 실행 (검색 버튼 불필요)
- 장르·분위기·플랫폼은 다중 선택 AND 교집합
- 필터 옵션은 DB 실데이터 기반으로 동적 구성

### 서버 페이지네이션
- 게임 목록을 20개씩 서버에서 분할 응답
- 전체 게임 수가 늘어나도 한 번에 전달하는 응답 데이터 크기를 제한

### 온디맨드 영상 조회 및 캐싱
- 게임 상세 정보와 YouTube 영상 요청을 분리된 엔드포인트로 처리
- DB에 영상이 없는 경우에만 YouTube API를 실시간 호출 후 저장
- 이후 재방문 시 DB에서 즉시 제공

### 탐색 상태 복원
- 상세 페이지 이동 전 `onBeforeRouteLeave`에서 검색 상태를 Pinia에 저장
- 뒤로가기 시 저장된 조건으로 서버 재조회하여 이전 페이지 위치 복원

### 검색 UX

- 상단 검색창과 탐색 화면에서 게임명 자동 완성 제공
- 키보드 방향키·Enter로 자동 완성 결과 선택
- 필터 칩 변경을 감지해 별도 검색 버튼 없이 결과 갱신
- 로딩, 결과 없음, API 오류를 화면 상태별로 구분
- ToastAlert로 작업 성공·실패 피드백 제공

### UI와 반응형 처리

- 서비스 색상과 카드 레이아웃을 Vue SFC의 scoped CSS로 구성
- 홈·탐색·상세·프로필 화면에 화면 폭별 미디어 쿼리 적용
- 게임 카드 그리드와 가로 스크롤 행을 화면 목적에 맞게 분리
- 탐험 콘셉트의 커서와 나침반 인터랙션, 활동 메달 이미지 제공

반응형 레이아웃은 주요 화면에 적용했지만 다양한 모바일 기기와 키보드 탐색에 대한 정식 접근성 검증은 아직 진행하지 않았습니다.

---

## 프론트엔드 설계 포인트

### 화면과 데이터 호출의 역할 분리

`views`는 라우트 단위 흐름을 조율하고, 재사용 UI는 도메인별 `components`에 배치했습니다. 외부 통신은 `api` 계층에 두어 화면 컴포넌트가 렌더링과 사용자 상호작용에 집중하도록 했습니다.

### 서버 상태를 불필요하게 복제하지 않기

Pinia에는 인증 정보와 화면 복원에 필요한 검색 조건처럼 여러 화면이 공유하는 상태만 저장합니다. 게임 목록과 상세 응답은 각 화면에서 API로 가져와 전역 상태의 수명과 동기화 범위를 줄였습니다.

### 실패 상황 피드백

외부 API와 인증 상태에 따라 요청이 실패할 수 있으므로 빈 결과 컴포넌트, 토스트, 401 공통 처리로 사용자에게 현재 상태를 알리도록 구성했습니다.

---

## 현재 한계와 개선 계획

- Vitest 기반 store·composable 단위 테스트 추가
- ESLint·Prettier와 CI 빌드 검사 도입
- 라우터 전역 인증 가드 및 로그인 후 원래 경로 복귀 구현
- 이미지 WebP 변환, 중복 에셋 정리와 지연 로딩 적용
- 키보드 탐색, 포커스 표시, 명도 대비 등 접근성 점검
- 모바일 해상도별 회귀 테스트와 E2E 테스트 추가
