# 🎮 인디 게임 추천 서비스: '방구석 탐험대' 프로젝트 정리.

> 사용자 선호 데이터를 분석해 최적의 인디 게임을 추천하는 **AI 기반 게임 추천 서비스**

| 영역 | 문서 | 기술 |
|---|---|---|
| 🖥️ **프론트엔드** | [front_README](frontend/front_README.md) | Vue 3 · Pinia · Vue Router · Axios |
| ⚙️ **백엔드** | [back_README](backend/back_README.md) | Django · DRF · GMS(AI) · SQLite |

## 빠른 실행

### 사전 요구사항

- Python 3.10 이상
- Node.js 22.18 이상 또는 24.12 이상

### 백엔드

```powershell
cd backend
Copy-Item .env.example .env
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata games
python manage.py loaddata medals
python manage.py runserver
```

### 프론트엔드

새 PowerShell 창에서 실행한다.

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

- 서비스: `http://127.0.0.1:5173`
- API 문서(Swagger): `http://127.0.0.1:8000/api/v1/docs/`
- 기본 화면·게임 목록·일반 검색은 외부 API 키 없이 fixture 데이터로 확인할 수 있다. AI 추천의 GMS 호출과 외부 데이터 수집은 해당 API 키를 설정한 경우에만 사용한다.


## 1. 프로젝트 개요
* **서비스명**: 방구석 탐험대
* **서비스 개요**: 사용자 선호 데이터를 분석하여 최적의 인디 게임을 추천해주는 AI 기반 서비스
* **주요 기능**:
    * 외부 API(Steam, RAWG 등)를 활용한 게임 데이터 수집 및 캐싱
    * AI 기반 사용자 맞춤형 게임 추천 시스템
    * 커뮤니티(자유/후기/파트너 모집) 및 사용자 간 소통 기능
    * 사용자 프로필 관리(찜 목록, 메달, 팔로우/팔로잉)

### 기술 스택

| 구분 | 사용 기술 |
|---|---|
| **프론트엔드** | Vue 3 (Composition API), Pinia, Vue Router, Axios |
| **백엔드** | Django 5.2, Django REST Framework, dj-rest-auth, drf-spectacular |
| **AI** | GMS (OpenAI 호환 게이트웨이) — 자연어 추천·표지 분석 |
| **데이터** | SQLite, 외부 API (RAWG·Steam·YouTube) |

### 아키텍처

```
┌─────────────┐      REST API       ┌──────────────┐      ┌─────────────────┐
│  Frontend   │  /api/v1/...        │   Backend    │ ───▶ │  GMS (AI)       │
│  (Vue 3 SPA)│ ◀─────────────────▶ │  (Django)    │      │  RAWG·Steam·YT  │
└─────────────┘                     └──────────────┘      └─────────────────┘
        │                                  │
   Pinia 상태관리                     SQLite + JSON fixture
```

### 핵심 설계

- **검색 상태 복원**: Pinia에 검색어·필터·정렬·페이지를 임시 저장해 게임 상세 화면에서 돌아올 때 이전 탐색 맥락을 복원한다.
- **서버 페이지네이션**: 게임 목록을 서버에서 20개 단위로 반환해 데이터가 많아져도 초기 응답 부담을 제어한다.
- **영상 Lazy Loading**: 게임 상세 정보와 YouTube 영상을 분리 요청해 상세 화면을 먼저 표시하고, 필요한 경우에만 영상을 수집·저장한다.
- **안정적인 AI 추천**: LLM은 사용자 의도 추출과 추천 이유 생성에 사용하고, 후보 선정은 서비스 DB의 필터·점수화 로직으로 처리한다.
- **키 없는 기본 시연**: 게임 fixture와 추천 폴백 로직을 제공해 외부 API 키가 없어도 주요 화면과 흐름을 확인할 수 있다.

각 영역의 상세 구조·컴포넌트·엔드포인트는 [프론트 README](frontend/front_README.md) / [백엔드 README](backend/back_README.md) 참고.

---

## 2. 프로젝트 일정
* [방구석 탐험대 노션 페이지](https://app.notion.com/p/Notion-361088fa848f804c87d3fafcf6ffc7d7)

## 3. 목표 서비스 및 실제 구현 정도
* [방구석 탐험대 노션 페이지](https://app.notion.com/p/Notion-361088fa848f804c87d3fafcf6ffc7d7)

## 4. 데이터베이스 모델링 (ERD)
* [방구석 탐험대 노션 페이지](https://app.notion.com/p/Notion-361088fa848f804c87d3fafcf6ffc7d7)

주요 도메인 모델 (자세한 내용은 [백엔드 README](backend/back_README.md#앱-apps)):

| 앱 | 핵심 모델 |
|---|---|
| accounts | `User`, `Follow`, `Medal`, `UserMedal`, `Notification` |
| games | `Game`, `Genre`, `Platform`, `Mood`, `Screenshot`, `GameVideo`, `SearchLog` |
| recommendations | `RecommendationLog`, `RecommendationResult` |
| wishlists | `Wishlist` |
| community | `Post`, `PostImage`, `PostComment` |

## 5. 페이지 설계 (화면 구성)
* [방구석 탐험대 노션 페이지](https://app.notion.com/p/Notion-361088fa848f804c87d3fafcf6ffc7d7)

주요 페이지 (자세한 내용은 [프론트 README](frontend/front_README.md#페이지-views)):

| 페이지 | 경로 | 설명 |
|---|---|---|
| 홈 | `/` | 추천·할인·신작 게임 카드 |
| 탐색 | `/explore` | AI 추천 + 필터 검색 |
| 게임 상세 | `/games/:id` | 정보·영상·스크린샷 |
| 커뮤니티 | `/community` | 게시판·댓글 |
| 프로필 | `/profile` | 찜·메달·팔로우·AI 기록 |

## 6. 컴포넌트 구조도 (Vue 컴포넌트 트리)
* [방구석 탐험대 노션 페이지](https://app.notion.com/p/Notion-361088fa848f804c87d3fafcf6ffc7d7)

컴포넌트 분류(common·home·explore·game-detail·profile·community)는 [프론트 README](frontend/front_README.md#컴포넌트-components) 참고.

## 7. URL 설계
* [방구석 탐험대 노션 페이지](https://app.notion.com/p/Notion-361088fa848f804c87d3fafcf6ffc7d7)

모든 API는 `api/v1/` 하위에 마운트된다. 앱별 엔드포인트 전체 목록은 [백엔드 README](backend/back_README.md#api-엔드포인트) 참고.

| 영역 | 대표 경로 |
|---|---|
| 인증 | `/auth/`, `/auth/registration/` |
| 게임 | `/games/`, `/games/{id}/`, `/games/recommended/` |
| AI 추천 | `/recommend/`, `/recommend/logs/` |
| 찜 | `/wishlist/`, `/games/{id}/wishlist/` |
| 커뮤니티 | `/posts/`, `/posts/{id}/comments/` |
| 유저 | `/accounts/me/`, `/accounts/users/{id}/follow/` |
| API 문서 | `/api/v1/docs/` (Swagger) |

---

## 8. 생성형 AI(GMS) 활용

이 서비스의 핵심은 생성형 AI 기반 추천이다. (상세: [백엔드 README](backend/back_README.md#생성형-ai-gms-활용))

1. **AI 추천 검색** — 자연어 프롬프트를 3단계로 처리: ①의도 추출(GMS) → ②DB 필터·점수화 → ③추천 이유·관련도 생성(GMS). *LLM은 언어 이해·설명만, 무엇을 추천할지는 DB에서 결정해 할루시네이션 방지.*
2. **홈 취향 분석 추천** — AI 추천 기록 + 찜 목록의 무드·장르를 가중 집계해 닮은 게임 추천(GMS 미호출).
3. **표지 시각 소재 분석** — GMS 비전으로 게임 표지를 분석해 추천 소재 매칭에 활용.

---

## 9. 실행 방법

### 백엔드
```bash
cd backend
python -m venv venv
# Windows PowerShell: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata games   # 게임 데이터(fixture) 적재
python manage.py loaddata medals   # 메달 데이터(fixture) 적재
python manage.py runserver
```

### 프론트엔드
```bash
cd frontend
npm install (또는 npm i)
npm run dev
```

> ⚠️ 팀원은 `git pull` 후 **반드시 `python manage.py migrate`** 를 실행한다. 데이터 파이프라인·환경 변수 등 자세한 내용은 [백엔드 README](backend/back_README.md) 참고.
