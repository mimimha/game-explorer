# Frontend

Vue 3 기반 SPA(Single Page Application)

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
| GamedetailView | `/games/:id` | 게임 상세 (정보·영상·스크린샷) |
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
| NotificationBubble | 상단 알림 뱃지 |
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
| MedalBadge | 메달 뱃지 단위 |
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
| **notifications** | 알림 갱신 신호 관리. 새 알림 발생 시 어느 컴포넌트에서든 뱃지 즉시 업데이트 |

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

---

## 주요 구현 포인트

### 필터 검색
- 필터 칩 클릭 즉시 `watch`로 자동 검색 실행 (검색 버튼 불필요)
- 장르·분위기·플랫폼은 다중 선택 AND 교집합
- 필터 옵션은 DB 실데이터 기반으로 동적 구성

### 서버 페이지네이션
- 게임 목록을 20개씩 서버에서 분할 응답
- 게임 수와 무관하게 응답 속도 일정 유지

### 영상 Lazy Loading
- 게임 상세 정보와 YouTube 영상 요청을 분리된 엔드포인트로 처리
- DB에 영상이 없는 경우에만 YouTube API를 실시간 호출 후 저장
- 이후 재방문 시 DB에서 즉시 제공

### 탐색 상태 복원
- 상세 페이지 이동 전 `onBeforeRouteLeave`에서 검색 상태를 Pinia에 저장
- 뒤로가기 시 저장된 조건으로 서버 재조회하여 이전 페이지 위치 복원
