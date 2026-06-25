"""
추천 계산 로직 (2층 구조).

  ① LLM(GMS)으로  prompt → 구조화된 의도(JSON) 추출
  ② 그 의도로 우리 Game DB 를 필터·점수화 (후보 선정)   ← "프롬프트 단어 ↔ 적재 게임" 연결 지점
  ③ LLM 으로 후보별 추천 이유(reason) 생성

settings.RECOMMEND_USE_LLM 이 False 거나 LLM 호출이 실패하면
기존 랜덤 placeholder 로 안전하게 폴백한다. (키 없이도 동작/시연 가능)
"""
import json
import logging

from django.conf import settings

from games.models import Game, Genre, Mood
from . import gms

logger = logging.getLogger(__name__)


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
    reasons = _generate_reasons(prompt, candidates)   # ③ 이유 생성

    results = []
    for rank, (game, score) in enumerate(candidates):
        results.append({
            'game_id': game.game_id,
            'reason': reasons.get(game.game_id) or _fallback_reason(prompt),
            'match_score': score if score is not None else max(50, 95 - rank * 8),
        })
    return results


def _extract_intent(prompt):
    """① 자유 문장 → {genres, price_max, is_korean, platforms, keywords}."""
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
        '(4) 불명확하면 비운다. 키: '
        'genres(배열, 반드시 아래 장르 목록 중에서만), '
        'moods(배열, 반드시 아래 무드 목록 중에서만 — 분위기·테마·감정), '
        'exclude_moods(배열, 배제할 무드 — 반드시 아래 무드 목록 중에서만), '
        "player_modes(배열, 'single'/'multi'/'coop' 중에서만 — 싱글/멀티/협동), "
        'subjects(배열, 표지에 보이길 원하는 시각 소재 — 반드시 아래 소재 목록 중에서만, '
        '예: "동물 나오는 게임"→["동물"]), '
        'price_max(정수 KRW 또는 null), '
        'is_korean(불리언 또는 null), '
        'platforms(배열), '
        'keywords(제목 검색용 영어 단어 배열). '
        f'사용 가능한 장르: {", ".join(genre_names) or "(없음)"}. '
        f'사용 가능한 무드: {", ".join(mood_names) or "(없음)"}. '
        f'사용 가능한 소재: {", ".join(SUBJECT_VOCAB)}'
    )
    data = gms.chat_json(
        [{'role': 'system', 'content': system},
         {'role': 'user', 'content': prompt}],
        temperature=0.2,
    )
    return {
        'genres': data.get('genres') or [],
        'moods': data.get('moods') or [],
        'exclude_moods': data.get('exclude_moods') or [],
        'player_modes': data.get('player_modes') or [],
        'subjects': data.get('subjects') or [],
        'price_max': data.get('price_max'),
        'is_korean': data.get('is_korean'),
        'platforms': data.get('platforms') or [],
        'keywords': data.get('keywords') or [],
    }


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
    want_subjects = set(intent.get('subjects', []))   # 표지 시각 소재(한국어)
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
        # 표지에 해당 소재가 보이면 강한 가산 (예: "동물" → 표지에 동물)
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
    """③ 후보 전체를 한 번의 호출로 보내 {game_id: reason} 생성 (토큰 절약)."""
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
        '너는 게임 추천 카피라이터다. 사용자의 취향 문장과 후보 게임 목록을 보고 '
        '각 게임이 왜 어울리는지 한국어 한 문장(40자 내외)으로 설명한다. '
        'JSON 으로만 답한다. 형식: '
        '{"reasons": [{"game_id": int, "reason": str}, ...]}'
    )
    user_msg = json.dumps({'prompt': prompt, 'games': listing},
                          ensure_ascii=False)
    try:
        data = gms.chat_json(
            [{'role': 'system', 'content': system},
             {'role': 'user', 'content': user_msg}],
            temperature=0.6,
        )
        return {r['game_id']: r.get('reason', '')
                for r in data.get('reasons', []) if 'game_id' in r}
    except Exception as e:  # 이유 생성만 실패해도 후보는 살린다
        logger.warning('추천 이유 생성 실패: %s', e)
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
