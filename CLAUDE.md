# CLAUDE.md

이 저장소에서 작업할 때 참고할 프로젝트 지침.

## 게임 데이터 파이프라인 (backend/games)

게임 데이터는 외부 API에서 수집한다. **`db.sqlite3`를 git으로 직접 공유한다** — 로그인 정보·게임 데이터·한글 번역이 모두 DB에 들어있어 파일째 공유한다. (기존엔 `games.json` fixture로 공유했으나, 로그인 등 공유 필요로 DB 파일 자체를 추적 대상으로 전환함.)

- **수집**: `python manage.py load_games` — RAWG(메타) + Steam(가격·인원) + YouTube(영상). 외부 API라 느리고 YouTube는 일일 쿼터(10,000 units = 100 검색)가 있다. 장르/태그 한정: `--genres indie`, `--tags horror,pixel-graphics`, `--no-youtube`(영상 생략·쿼터 절약).
- **기존 데이터 보강**: `python manage.py backfill_meta` — playtime/플레이인원/무드만 채움(영상·스크린샷 미호출 → YouTube 쿼터 보호). `--moods-only`는 무드만 갱신.
- **한글 번역**: `title_ko`/`description_ko`는 **Claude가 직접 번역**해 채운다(GMS 토큰 미사용). 결과는 db.sqlite3에 저장. `games.json` 백업이 필요하면 `PYTHONUTF8=1 python manage.py dumpdata games --indent 2 -o games/fixtures/games.json`(**`PYTHONUTF8=1` 필수** — 없으면 cp949로 한글 깨짐).

### ⚠️ db.sqlite3 팀 공유 규칙 (중요)

- **DB 담당자 1명만** db.sqlite3를 갱신·커밋한다. SQLite는 바이너리라 git 병합이 안 돼서, 두 명이 각자 바꿔 커밋하면 한쪽이 통째로 덮어쓴다.
- 팀원은 받은 db.sqlite3를 **그대로 사용**하고 `migrate`를 돌리지 않는다(이미 세팅됨). 이 저장소는 마이그레이션 드리프트가 있어, 빈 DB에서 새로 migrate하면 `mood`/`game_video.video_type` 등이 누락될 수 있다 → 그래서 DB 파일 공유로 우회한다.
- `db.sqlite3-journal`은 계속 `.gitignore` 대상(임시 파일).

### 필드별 소스 우선순위 (없으면 null/빈칸)

| 항목 | 1순위 | 폴백 | 비고 |
|---|---|---|---|
| playtime | RAWG `playtime` | 없음 | 0/없음 → null |
| 플레이인원(single/multi/coop) | RAWG tags | Steam categories(영문) | 둘 다 없으면 null |
| 분위기/무드 | RAWG tags 화이트리스트 | **없음** | Steam은 무드 미제공 |

## 무드 태그 화이트리스트 (중요한 설계 결정)

RAWG의 `tags` 배열은 무드·장르·기술·시점을 한데 섞은 **평면 목록**이고(전체 ~310종), **RAWG에는 "이 태그는 무드"라는 구분 필드가 없다.** 따라서 어떤 태그를 "분위기/무드"로 볼지는 **사람(LLM)의 판단**이 필요하다.

- **화이트리스트 = `backend/games/services/rawg.py`의 `MOOD_TAG_MAP`** — "이 영문 태그들만 무드로 인정한다"는 허용 목록이자 영문→한국어 라벨 변환표. 목록에 없는 태그는 `extract_mood_names()`에서 자동 폐기된다.
- **추가/검증 방법론**: 추측이 아니라 **실데이터 기반**으로 한다. `python analyze_tags.py`(임시 분석 스크립트)로 보유 게임 전체의 RAWG 태그를 빈도 집계 → 화이트리스트에 빠진 무드 후보를 빈도순으로 검토 → `MOOD_TAG_MAP`에 추가 → `backfill_meta --moods-only`로 재적재. 장르/기술/시점 태그(RPG, Full controller support, First-Person 등)는 무드가 아니므로 제외한다.
- 무드를 늘리고 싶으면 위 순서를 따른다. (예: 1개 샘플로 18종 시작 → 전수 집계로 7종 추가 → 25종)

## 마이그레이션 규칙

**이미 적용된 마이그레이션 파일을 직접 수정하지 말 것.** 모델 변경은 `makemigrations`로 새 파일을 만들어 커밋한다. db.sqlite3는 각자 로컬이라, 적용 완료된 마이그레이션을 고치면 이미 적용한 사람의 DB엔 반영되지 않아 `no such table` 류 오류가 난다.

## YouTube 영상 수집 (토큰 사용처)

YouTube Data API를 **실제로 호출하는 유일한 모듈은 `backend/games/services/youtube.py`** 다. 다중 키를 지원해 한 키가 일일 쿼터(10,000 units = 100 검색/키)를 소진하면(403 quotaExceeded / 429) 자동으로 다음 키로 넘어간다. 키는 `.env`의 `YOUTUBE_DATA_API_KEYS=키1,키2`(먼저 쓸 키부터) 또는 `YOUTUBE_DATA_API_KEY` + `YOUTUBE_DATA_API_KEY_2`로 설정.

이 서비스를 부르는 정식 수집 커맨드는 `load_games`(전체 적재 시 영상 포함)와 `backfill_videos`(영상만, RAWG/스팀/스크린샷 미호출 → YouTube 쿼터만 사용). 게임당 검색 2회(트레일러 1 + 공략 2). 한 번 수집하면 `GameVideo` → fixture(`games.json`)에 저장되어, 조회·재생·`loaddata`는 토큰을 쓰지 않는다(토큰은 '새 수집' 때만).

## 임시 스크립트 (커밋 금지)

`backend/try_walkthrough.py`, `backend/verify_one_game.py`, `backend/analyze_tags.py`는 튜닝·분석용 임시 파일이다. **`git add .`로 묶지 말 것.** (`backfill_meta.py`·`backfill_videos.py`·`export_translations.py`·`import_translations.py`는 정식 management command라 커밋 대상)

⚠️ **`try_walkthrough.py`는 `youtube.py`를 거치지 않고 YouTube API를 자체적으로 직접 호출한다**(단일 키, 키 자동 전환 없음). 돌리면 그 시점 단일 키의 쿼터를 그대로 소비하므로 주의. 나머지 정식 수집 흐름(`load_games`/`backfill_videos`)은 `youtube.py`를 거쳐 키 전환 혜택을 받는다.
