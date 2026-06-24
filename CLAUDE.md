# CLAUDE.md

이 저장소에서 작업할 때 참고할 프로젝트 지침.

## 게임 데이터 파이프라인 (backend/games)

게임 데이터는 외부 API에서 수집한다. **`db.sqlite3`는 `.gitignore` 대상이라 git으로 공유되지 않으며**, 공유는 JSON fixture(`backend/games/fixtures/games.json`)로 한다.

- **수집**: `python manage.py load_games` — RAWG(메타) + Steam(가격·인원) + YouTube(영상). 외부 API라 느리고 YouTube는 일일 쿼터(10,000 units = 100 검색)가 있다.
- **기존 데이터 보강**: `python manage.py backfill_meta` — playtime/플레이인원/무드만 채움(영상·스크린샷 미호출 → YouTube 쿼터 보호). `--moods-only`는 무드만 갱신.
- **공유**: `PYTHONUTF8=1 python manage.py dumpdata games --indent 2 -o games/fixtures/games.json` 로 내보내 커밋. **`PYTHONUTF8=1` 필수** — 없으면 Windows cp949로 한글이 깨진다.
- **받기**: `python manage.py migrate` → `python manage.py loaddata games`

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

## 임시 스크립트 (커밋 금지)

`backend/try_walkthrough.py`, `backend/verify_one_game.py`, `backend/analyze_tags.py`는 튜닝·분석용 임시 파일이다. **`git add .`로 묶지 말 것.** (`backfill_meta.py`는 정식 management command라 커밋 대상)
