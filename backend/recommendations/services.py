"""
추천 계산 로직 (2층 구조).

  ① LLM(GMS)으로  prompt → 구조화된 의도(JSON) 추출
  ② 그 의도로 우리 Game DB 를 필터·점수화 (후보 선정)   ← "프롬프트 단어 ↔ 적재 게임" 연결 지점
  ③ LLM 으로 후보별 추천 이유(reason) + 관련도(match 0~100) 생성

settings.RECOMMEND_USE_LLM 이 False 거나 LLM 호출이 실패하면
기존 랜덤 placeholder 로 안전하게 폴백한다. (키 없이도 동작/시연 가능)

[정확도 개선]
  - ① 프롬프트에 few-shot 예시(완전한 입력→출력 JSON)를 추가해 포맷·엣지케이스를 동시 학습.
  - ① 반환 직전 LLM이 뱉은 genres/moods 를 DB 실제 어휘에 rapidfuzz 로 보정.
    임계치 미달은 폐기 → ②번에서 표기 흔들림이 '조용한 0건 매칭'으로 죽는 걸 방지.
  - ③ 화면 관련도(match)는 ②의 합산점수(만점에서 잘려 다 100%로 뭉치는 문제)가 아니라,
    LLM 이 후보별로 직접 매긴 0~100 차등값을 쓴다. (실패 시 ②점수로 폴백)
"""
import json
import logging

from django.conf import settings
from rapidfuzz import process, fuzz

from games.models import Game, Genre, Mood
from . import gms

logger = logging.getLogger(__name__)

# LLM 출력 → DB 실제 어휘 보정 임계치 (이 점수 미만이면 오매칭 위험으로 폐기)
_VOCAB_CUTOFF = 85


def generate_recommendations(prompt: str, user=None, limit: int = 10):
    """
    prompt(취향 문장) → [{'game_id': int, 'reason': str, 'match_score': int}, ...]
    LLM 경로 실패 시 어떤 예외든 잡아 랜덤으로 폴백한다.
    """
    if settings.RECOMMEND_USE_LLM:
        try:
            return _llm_recommendations(prompt, limit=limit)
        except Exception as e:  # 네트워크/파싱/키 등 모든 실패 → 폴백
            logger.warning('LLM 추천 실패, 랜덤 폴백: %s', e)

    return _random_recommendations(prompt, limit=limit)


# ── LLM 경로 (①+②+③) ────────────────────────────────────────────
def _llm_recommendations(prompt, limit=5):
    intent = _extract_intent(prompt)                  # ① 의도 추출
    candidates = _filter_games(intent, limit=limit)   # ② DB 필터·점수
    # 정확도 우선: 매칭이 없으면 무작위로 채우지 않고 빈 결과를 반환한다.
    # (관련 없는 게임을 끼워 넣기보다, 적게/없게 보여주는 쪽)
    rs = _generate_reasons(prompt, candidates)        # ③ 이유 + 관련도(LLM 차등)

    results = []
    for rank, (game, content_score) in enumerate(candidates):
        reason, llm_match = rs.get(game.game_id, ('', None))
        # 화면 관련도: LLM 이 매긴 차등값 우선, 없으면 ②의 합산점수로 폴백
        match = llm_match if isinstance(llm_match, (int, float)) else content_score
        results.append({
            'game_id': game.game_id,
            'reason': reason or _fallback_reason(prompt),
            'match_score': max(1, min(100, int(match))),
        })
    # LLM 관련도 기준으로 재정렬(차등 반영)
    results.sort(key=lambda r: r['match_score'], reverse=True)
    return results


# few-shot: 규칙을 '말'로 설명하는 대신 완전한 입력→출력 JSON 으로 보여준다.
# 모델이 (a) 출력 포맷 (b) 과잉추론 금지 (c) 배제어 처리 를 동시에 학습한다.
_EXTRACT_EXAMPLES = (
    '예시:\n'
    '입력: "공포 말고 아기자기한 동물 게임, 2만원 이하"\n'
    '출력: {"genres":[],"moods":["귀여운"],"exclude_moods":["공포"],'
    '"player_modes":[],"subjects":["동물"],"subject_terms":[],'
    '"price_max":20000,"is_korean":null,"platforms":[],"keywords":[]}\n\n'
    '입력: "토끼 나오는 힐링 게임 하고 싶어"\n'
    '출력: {"genres":[],"moods":["편안한"],"exclude_moods":[],'
    '"player_modes":[],"subjects":["동물"],"subject_terms":["토끼","rabbit","bunny"],'
    '"price_max":null,"is_korean":null,"platforms":[],"keywords":[]}\n\n'
    '입력: "친구랑 같이 할 협동 좀비 게임"\n'   # 좀비만, 공포·액션·생존 추가 금지
    '출력: {"genres":[],"moods":["좀비"],"exclude_moods":[],'
    '"player_modes":["coop"],"subjects":[],"subject_terms":[],'
    '"price_max":null,"is_korean":null,"platforms":[],"keywords":[]}\n\n'
    '입력: "마인크래프트 같은 한국어 지원 게임"\n'  # 프랜차이즈만 keywords 로
    '출력: {"genres":[],"moods":[],"exclude_moods":[],'
    '"player_modes":[],"subjects":[],"subject_terms":[],'
    '"price_max":null,"is_korean":true,"platforms":[],"keywords":["minecraft"]}'
)


def _extract_intent(prompt):
    """① 자유 문장 → {genres, moods, ..., keywords}. 반환 전 DB 어휘로 보정."""
    from games.services.vision import SUBJECT_VOCAB
    genre_names = list(Genre.objects.values_list('genre_name', flat=True))
    mood_names = list(Mood.objects.values_list('mood_name', flat=True))
    system = (
        '너는 게임 추천 시스템의 의도 분석기다. 사용자 문장에서 선호를 추출해 '
        'JSON 으로만 답한다. 규칙: '
        '(1) 사용자가 표현한 선호를 아래 목록의 **가장 가까운 항목으로 매핑**한다. '
        '동의어·유사 표현도 매핑한다 (예: "아기자기한"→"귀여운", "무서운"→"공포", '
        '"잔잔한"→"편안한"). '
        '(2) 단, 사용자가 말하지 않은 **별개의 속성을 추론해 추가하지 마라** '
        '(예: "좀비 게임"→moods=["좀비"]만, 공포·액션·생존 추가 금지). '
        '(3) "말고/빼고/제외/싫어/없는" 으로 **배제**한 것은 exclude_moods 에 넣는다 '
        '(예: "공포 말고 아기자기한"→moods=["귀여운"], exclude_moods=["공포"]). '
        '(4) 불명확하면 비운다. '
        '(5) 답하기 전 짧게 분석하고 싶으면 "_thought" 키에 한 문장 적어도 된다(무시됨). '
        '키: '
        '_thought(선택, 짧은 분석 — 무시됨), '
        'genres(배열, 반드시 아래 장르 목록 중에서만), '
        'moods(배열, 반드시 아래 무드 목록 중에서만 — 분위기·테마·감정), '
        'exclude_moods(배열, 배제할 무드 — 반드시 아래 무드 목록 중에서만), '
        "player_modes(배열, 'single'/'multi'/'coop' 중에서만 — 싱글/멀티/협동), "
        'subjects(배열, 표지에 보이길 원하는 시각 소재 — 반드시 아래 소재 목록 중에서만, '
        '예: "동물 나오는 게임"→["동물"]), '
        'subject_terms(배열, 사용자가 구체적으로 콕 집어 말한 등장 요소를 한국어+영어 둘 다 — '
        '예: "토끼"→["토끼","rabbit","bunny"], "고양이"→["고양이","cat"], "용"→["용","dragon"]. '
        '사전에 없어도 됨. 일반/추상 단어(예: 재미, 게임)는 제외), '
        'price_max(정수 KRW 또는 null), '
        'is_korean(불리언 또는 null), '
        'platforms(배열), '
        'keywords(배열, 사용자가 **명시적으로 언급한 시리즈/프랜차이즈/고유명사의 영어 표기만** — '
        '예: "마인크래프트 같은"→["minecraft"]. 일반 형용사·동사·추상명사는 절대 넣지 마라). '
        f'사용 가능한 장르: {", ".join(genre_names) or "(없음)"}. '
        f'사용 가능한 무드: {", ".join(mood_names) or "(없음)"}. '
        f'사용 가능한 소재: {", ".join(SUBJECT_VOCAB)}\n\n'
        + _EXTRACT_EXAMPLES
    )
    data = gms.chat_json(
        [{'role': 'system', 'content': system},
         {'role': 'user', 'content': prompt}],
        temperature=0.2,
    )

    # LLM 이 뱉은 장르/무드를 DB 실제 어휘로 보정(표기 흔들림 → 정규값 치환, 오매칭은 폐기).
    genres = _coerce_to_vocab(data.get('genres') or [], genre_names)
    moods = _coerce_to_vocab(data.get('moods') or [], mood_names)
    exclude_moods = _coerce_to_vocab(data.get('exclude_moods') or [], mood_names)

    return {
        'genres': genres,
        'moods': moods,
        'exclude_moods': exclude_moods,
        'player_modes': data.get('player_modes') or [],
        'subjects': data.get('subjects') or [],
        'subject_terms': data.get('subject_terms') or [],
        'price_max': data.get('price_max'),
        'is_korean': data.get('is_korean'),
        'platforms': data.get('platforms') or [],
        'keywords': data.get('keywords') or [],
    }


def _coerce_to_vocab(values, vocab, cutoff=_VOCAB_CUTOFF):
    """
    LLM 이 반환한 값을 DB 에 실재하는 어휘로 보정한다.
    - cutoff 이상으로 가까운 정규 어휘가 있으면 그 값으로 치환(예: '로그라이크'→'로그라이트').
    - 못 맞추면 버린다(엉뚱한 값으로 0건 매칭/오매칭을 내느니 제외).
    - 중복은 순서를 유지하며 제거한다.
    """
    if not vocab:
        return list(values)
    fixed = []
    for v in values:
        if not v:
            continue
        match = process.extractOne(str(v), vocab, scorer=fuzz.ratio)
        if match and match[1] >= cutoff and match[0] not in fixed:
            fixed.append(match[0])   # DB에 실재하는 정규 값으로 치환
    return fixed


# 상호 배타 무드: 한쪽을 원하면 반대쪽은 자동 제외한다.
# 단, 사용자가 양쪽을 모두 명시하면(예: "아기자기한 공포게임") 자동 제외하지 않는다.
_COZY_MOODS = {'귀여운', '편안한', '아늑한', '가족친화'}
_GRIM_MOODS = {'공포', '잔혹한', '폭력적인', '생존 공포', '심리 공포'}


def _implied_excludes(want_moods):
    """원하는 무드로부터 자동으로 배제할 무드 집합을 도출."""
    w = set(want_moods)
    cozy, grim = w & _COZY_MOODS, w & _GRIM_MOODS
    if cozy and grim:          # 양쪽 모두 명시 → 자동 제외 안 함
        return set()
    if cozy:
        return _GRIM_MOODS - w
    if grim:
        return _COZY_MOODS - w
    return set()


def _filter_games(intent, limit=5):
    """
    ② intent 로 Game 필터 + 장르/키워드 겹침으로 점수화.
    반환: [(game, match_score 0~100), ...]  (점수 내림차순, 상위 limit)
    """
    qs = Game.objects.prefetch_related('genres', 'moods').all()

    # 하드 필터 (조건이 명시됐을 때만)
    if intent.get('price_max') is not None:
        qs = qs.filter(final_price__isnull=False,
                       final_price__lte=intent['price_max'])
    if intent.get('is_korean') is True:
        qs = qs.filter(is_korean=True)

    want_genres = {g.lower() for g in intent.get('genres', [])}
    want_moods = {m.lower() for m in intent.get('moods', [])}
    # 명시적 배제("말고") + 상호배타 자동 배제(귀여운↔공포 등)
    exclude_moods = {m.lower() for m in intent.get('exclude_moods', [])}
    exclude_moods |= {m.lower() for m in _implied_excludes(intent.get('moods', []))}
    want_modes = {m.lower() for m in intent.get('player_modes', [])}
    want_subjects = set(intent.get('subjects', []))   # 표지 시각 소재(큰 분류)
    subject_terms = [t.lower() for t in intent.get('subject_terms', []) if t]  # 구체 소재(토끼 등)
    keywords = [k.lower() for k in intent.get('keywords', []) if k]

    scored = []
    for game in qs:
        gnames = {gn.lower() for gn in
                  game.genres.values_list('genre_name', flat=True)}
        mnames = {mn.lower() for mn in
                  game.moods.values_list('mood_name', flat=True)}

        # 배제 무드를 하나라도 가진 게임은 완전히 제외 (예: "공포 말고")
        if exclude_moods & mnames:
            continue
        # 실제 속성 일치 점수 — 분위기(무드) 최우선 > 장르 > 인원 > 키워드
        content = 40 * len(want_moods & mnames)                # 무드 일치 (최우선)
        # 구체 소재(예: 토끼)를 콕 집어 요청했으면 → 제목+설명에 그 단어가 '실제로' 있을
        # 때만 가산한다. 없으면 큰분류(동물) 가산도 주지 않아, 토끼 아닌 동물 게임이
        # 100%로 뜨는 걸 막는다. (큰 분류 소재만 말했으면 기존 표지 매칭 사용)
        if subject_terms:
            game_text = ' '.join(filter(None, [
                game.title, game.title_ko, game.description, game.description_ko,
            ])).lower()
            if any(t in game_text for t in subject_terms):
                content += 45
        else:
            content += 35 * len(want_subjects & set(game.thumbnail_subjects or []))
        content += 25 * len(want_genres & gnames)              # 장르 일치
        if 'single' in want_modes and game.is_singleplayer:    # 인원 일치
            content += 20
        if 'multi' in want_modes and game.is_multiplayer:
            content += 20
        if 'coop' in want_modes and game.is_coop:
            content += 20
        title = (game.title or '').lower()
        content += 10 * sum(1 for k in keywords if k in title)  # 제목 키워드
        desc = (game.description or '').lower()
        content += 4 * sum(1 for k in keywords if k in desc)    # 설명 키워드(약하게)

        # 속성 일치가 전혀 없으면 후보에서 제외 (평점만 높은 무관 게임 배제)
        if content <= 0:
            continue

        score = content
        if game.metacritic_score:                              # 평점은 동점 정렬용 가산만
            score += min(game.metacritic_score, 100) // 20
        scored.append((game, min(score, 100)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def _generate_reasons(prompt, candidates):
    """
    ③ 후보 전체를 한 번의 호출로 보내 {game_id: (reason, match)} 생성.
    - reason: 한국어 한 문장 추천 이유.
    - match: LLM 이 직접 매긴 관련도(0~100). 요청을 다 충족할수록 높게, 일부만 맞으면 낮게.
      → ②의 합산점수가 만점에서 잘려 다 100%로 뭉치는 문제를 LLM 차등으로 해소.
    """
    if not candidates:
        return {}
    listing = [
        {
            'game_id': g.game_id,
            'title': g.title,
            'genres': list(g.genres.values_list('genre_name', flat=True)),
        }
        for g, _ in candidates
    ]
    system = (
        '너는 게임 추천 전문가다. 사용자의 취향 문장과 후보 게임 목록을 보고, 각 게임에 대해 '
        '(1) 왜 어울리는지 한국어 한 문장(40자 내외)의 reason, '
        '(2) 요청과 얼마나 맞는지 match(0~100 정수 관련도)를 매긴다. '
        'match 규칙: 요청의 모든 요소(분위기·소재·장르 등)를 충족할수록 높게, 일부만 맞으면 낮게. '
        '후보마다 분명히 다른 값으로 차등을 줘라(전부 100 같은 만점 남발 금지). '
        'JSON 으로만 답한다. 형식: '
        '{"items": [{"game_id": int, "reason": str, "match": int}, ...]}'
    )
    user_msg = json.dumps({'prompt': prompt, 'games': listing},
                          ensure_ascii=False)
    try:
        data = gms.chat_json(
            [{'role': 'system', 'content': system},
             {'role': 'user', 'content': user_msg}],
            temperature=0.5,
        )
        out = {}
        for r in data.get('items', []):
            if 'game_id' in r:
                out[r['game_id']] = (r.get('reason', ''), r.get('match'))
        return out
    except Exception as e:  # 이유/점수 생성만 실패해도 후보는 살린다(②점수로 폴백)
        logger.warning('추천 이유·관련도 생성 실패: %s', e)
        return {}


# ── 폴백(랜덤) 경로 — LLM 자체가 꺼졌거나 호출 실패일 때만 ───────────
def _random_recommendations(prompt, limit=5):
    """LLM 미사용/실패 시: 무작위 게임 + 더미 이유/점수."""
    results = []
    for rank, game in enumerate(Game.objects.order_by('?')[:limit]):
        results.append({
            'game_id': game.game_id,
            'reason': _fallback_reason(prompt),
            'match_score': max(50, 95 - rank * 8),
        })
    return results


def _fallback_reason(prompt):
    return f'"{prompt[:20]}" 취향과 잘 맞을 만한 게임이에요.'
