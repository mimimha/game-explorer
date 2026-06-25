# Backend

Django REST Framework 기반 API 서버

## 기술 스택

- **Django 5.2** + **Django REST Framework** — REST API
- **dj-rest-auth** + **django-allauth** — 토큰 인증·회원가입
- **drf-spectacular** — OpenAPI(Swagger) 문서 자동 생성
- **SQLite** — 개발 DB (게임 데이터는 JSON fixture로 공유)
- **GMS** (OpenAI 호환 게이트웨이) — AI 추천·표지 분석
- **외부 API** — RAWG(메타), Steam(가격·인원), YouTube(영상)

---

## 프로젝트 구조

```
backend/
├── config/             # 프로젝트 설정 (settings, urls, wsgi)
├── accounts/           # 유저·팔로우·메달·알림
├── games/              # 게임 데이터·검색·영상 (핵심 도메인)
│   ├── services/       # 외부 API 연동 (rawg, steam, youtube, videos, vision)
│   └── management/     # 데이터 적재·보강 커맨드
├── recommendations/    # AI 추천 (GMS 연동)
├── wishlists/          # 찜
├── community/          # 게시글·댓글
├── media/              # 업로드 이미지
└── manage.py
```

모든 API는 `api/v1/` 하위에 마운트된다. ([config/urls.py](config/urls.py))

---

## 앱 (apps)

| 앱 | 역할 | 핵심 모델 |
|---|---|---|
| **accounts** | 인증·프로필·팔로우·메달·알림 | `User`, `Follow`, `Medal`, `UserMedal`, `Notification` |
| **games** | 게임 메타·분류·미디어·검색 기록 | `Game`, `Genre`, `Platform`, `Mood`, `Screenshot`, `GameVideo`, `SearchLog` |
| **recommendations** | AI 자연어 추천·기록 | `RecommendationLog`, `RecommendationResult` |
| **wishlists** | 게임 찜 | `Wishlist` |
| **community** | 게시판·댓글·이미지 | `Post`, `PostImage`, `PostComment` |

> `User`는 `AbstractUser` 상속 커스텀 모델(`AUTH_USER_MODEL = accounts.User`).

---

## API 엔드포인트

### accounts/ — 유저
| 메서드 | 경로 | 설명 |
|---|---|---|
| GET/PATCH | `/accounts/me/` | 내 정보 조회·수정 |
| GET | `/accounts/me/medals/` | 내 메달 목록 |
| GET | `/accounts/mypage/` | 마이페이지 (찜·기록·게시글 종합) |
| GET | `/accounts/users/{id}/` | 유저 프로필 |
| POST | `/accounts/users/{id}/follow/` | 팔로우 토글 |
| GET | `/accounts/users/{id}/{followers\|followings}/` | 팔로워·팔로잉 목록 |
| GET | `/accounts/notifications/` | 알림 목록 |
| GET | `/accounts/notifications/count/` | 안 읽은 알림 수 |
| POST | `/accounts/notifications/read-all/` | 전체 읽음 |
| POST/DELETE | `/accounts/notifications/{id}/...` | 개별 읽음·삭제 |

### games/ — 게임
| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/games/` | 게임 목록 (필터·정렬·**서버 페이지네이션** 20개/page) |
| GET | `/games/recommended/` | 홈 취향 분석 추천 (찜·AI기록 유사도) |
| GET | `/games/on-sale/` | 할인 중 게임 |
| GET | `/games/new-releases/` | 최근 출시 게임 |
| GET | `/games/filter-options/` | 필터 옵션 (DB 실데이터 기반) |
| GET | `/games/suggest/` | 검색어 자동완성 |
| GET | `/games/{id}/` | 게임 상세 (영상 제외, 즉시 응답) |
| GET | `/games/{id}/videos/` | 영상 (없으면 YouTube **Lazy** 호출·저장) |
| GET | `/games/{id}/posts/` | 해당 게임 게시글 |
| GET | `/genres/` | 장르 목록 |

### recommendations/ — AI 추천
| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/recommend/` | 자연어 프롬프트 → AI 추천 + 기록 저장 |
| GET | `/recommend/logs/` | 내 추천 기록 |
| GET/DELETE | `/recommend/logs/{id}/...` | 기록 상세·삭제 |

### wishlists/ — 찜
| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/wishlist/` | 내 찜 목록 |
| POST/DELETE | `/games/{id}/wishlist/` | 찜 토글 |

### community/ — 커뮤니티
| 메서드 | 경로 | 설명 |
|---|---|---|
| GET/POST | `/posts/` | 게시글 목록·작성 |
| GET/PATCH/DELETE | `/posts/{id}/` | 게시글 상세·수정·삭제 |
| POST/DELETE | `/posts/{id}/images/...` | 게시글 이미지 |
| GET/POST | `/posts/{id}/comments/` | 댓글 목록·작성 |
| PATCH/DELETE | `/comments/{id}/` | 댓글 수정·삭제 |

### 인증·문서
- `/auth/`, `/auth/registration/` — dj-rest-auth (로그인·로그아웃·회원가입)
- `/api/v1/docs/` — Swagger UI / `/api/v1/schema/` — OpenAPI 스키마

---

## 생성형 AI (GMS) 활용

GMS는 OpenAI 호환 게이트웨이로, `RECOMMEND_USE_LLM=True` + 키 설정 시에만 호출된다(없으면 토큰 0 폴백). 클라이언트: [recommendations/gms.py](recommendations/gms.py)

### 1. AI 추천 검색 — [recommendations/services.py](recommendations/services.py)
자연어 프롬프트를 받아 **3단계**로 추천한다.
1. **의도 추출** (GMS) — 문장 → 구조화 JSON(`genres/moods/subjects/price_max/...`). few-shot + rapidfuzz로 DB 어휘 보정.
2. **DB 필터·점수화** (GMS 미사용) — 의도로 Game DB를 가중 점수화(무드>소재>장르>인원>키워드).
3. **이유·관련도 생성** (GMS) — 후보별 추천 이유 한 문장 + 관련도(0~100).

> LLM은 언어 이해·설명만, **무엇을 추천할지는 우리 DB에서 결정**한다(할루시네이션 방지). 실패 시 랜덤 폴백.

### 2. 홈 취향 분석 추천 — `RecommendedGamesView` ([games/views.py](games/views.py))
**GMS 미호출.** AI 추천 기록 + 찜 목록의 무드·장르를 가중 집계해 프로파일을 만들고, 안 본 게임 중 가장 닮은 것을 추천(`ai_sim` / `wish_sim` 유사도 %).

### 3. 표지 시각 소재 분석 — [games/services/vision.py](games/services/vision.py)
GMS 비전 모델로 게임 표지를 분석해 `thumbnail_subjects`(예: `['동물','풍경']`)를 채운다. → AI 추천의 소재 매칭에 사용.

> ⚠️ 한글 번역(`title_ko`/`description_ko`)은 GMS를 쓰지 않고 LLM이 직접 채운다.

---

## 데이터 파이프라인 (management commands)

`db.sqlite3`는 `.gitignore` 대상이라 게임 데이터는 **JSON fixture**(`games/fixtures/games.json`)로 공유한다.

| 커맨드 | 역할 |
|---|---|
| `load_games` | RAWG+Steam+YouTube 전체 적재 (`--no-youtube`로 쿼터 절약) |
| `backfill_meta` | playtime·플레이인원·무드 보강 (영상 미호출) |
| `backfill_videos` | 영상만 보강 (YouTube 쿼터만 사용) |
| `backfill_thumbnails` | GMS 비전으로 표지 시각 소재 채움 |
| `translate_games` | 한글 번역 적재 |
| `export_translations` / `import_translations` | 번역 내보내기·가져오기 |
| `refresh_prices` | Steam 가격 갱신 |
| `award_existing_medals` | 기존 유저 메달 일괄 부여 |

### 데이터 받기 (팀원)
```bash
git pull
python manage.py migrate          # ⚠️ 필수 — 안 하면 no such table
python manage.py loaddata games
```

### 데이터 공유 (내보내기)
```bash
PYTHONUTF8=1 python manage.py dumpdata games \
  --exclude games.SearchLog --indent 2 -o games/fixtures/games.json
```
- `PYTHONUTF8=1` 필수 (Windows cp949 한글 깨짐 방지)
- `--exclude games.SearchLog` 필수 (사용자 종속 FK라 loaddata 깨짐)



---

## 실행

```bash
# 가상환경 활성화 후
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata games   # 게임 데이터 적재, accounts에 메달 데이터 확인
python manage.py loaddata medals   # 메달 데이터(fixture) 적재
python manage.py runserver
```

### 환경 변수 (.env)
| 변수 | 설명 |
|---|---|
| `SSAFY_GMS_KEY` (또는 `GMS_API_KEY`) | GMS 인증 키 |
| `GMS_BASE_URL` | GMS 엔드포인트 (예: `https://.../v1`) |
| `GMS_MODEL` / `GMS_VISION_MODEL` | 텍스트·비전 모델 (기본 `gpt-4o-mini`) |
| `RECOMMEND_USE_LLM` | `True`일 때만 AI 추천에 GMS 호출 |
| `RAWG_API_KEY` | RAWG 메타 수집 |
| `YOUTUBE_DATA_API_KEYS` | YouTube 영상 수집 (쉼표로 다중 키, 쿼터 소진 시 자동 전환) |

---

## 주요 구현 포인트

### 영상 Lazy Loading
- 상세(`/games/{id}/`)와 영상(`/games/{id}/videos/`) 엔드포인트 분리 → 상세는 즉시 응답.
- 영상 없는 게임을 처음 열 때만 YouTube 호출 후 `GameVideo`로 저장, 이후 DB에서 즉시 제공.

### 서버 페이지네이션
- 게임 목록을 20개씩 분할 응답(`{count, results}`) → 게임 수와 무관하게 응답 일정.

### 무드 화이트리스트
- RAWG의 평면 태그 목록에서 "무드"만 골라내는 허용 목록(`services/rawg.py`의 `MOOD_TAG_MAP`). 실데이터 빈도 분석 기반으로 관리.

### 안전한 폴백
- GMS 미설정·호출 실패 시 AI 추천은 랜덤으로, 홈 추천은 무작위 '오늘의 추천'으로 폴백 → 키 없이도 동작.
