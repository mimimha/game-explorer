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

from games.models import Game, Genre
from . import gms

logger = logging.getLogger(__name__)


def generate_recommendations(prompt: str, user=None, limit: int = 5):
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
    if not candidates:                                # 매칭 0건이면 채우기
        candidates = _random_games(limit)
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
    genre_names = list(Genre.objects.values_list('genre_name', flat=True))
    system = (
        '너는 게임 추천 시스템의 의도 분석기다. 사용자 문장에서 선호를 추출해 '
        'JSON 으로만 답한다. 키: '
        'genres(배열, 반드시 아래 목록 중에서만), '
        'price_max(정수 KRW 또는 null), '
        'is_korean(불리언 또는 null), '
        'platforms(배열), '
        'keywords(제목 검색용 영어 단어 배열). '
        f'사용 가능한 장르: {", ".join(genre_names) or "(없음)"}'
    )
    data = gms.chat_json(
        [{'role': 'system', 'content': system},
         {'role': 'user', 'content': prompt}],
        temperature=0.2,
    )
    return {
        'genres': data.get('genres') or [],
        'price_max': data.get('price_max'),
        'is_korean': data.get('is_korean'),
        'platforms': data.get('platforms') or [],
        'keywords': data.get('keywords') or [],
    }


def _filter_games(intent, limit=5):
    """
    ② intent 로 Game 필터 + 장르/키워드 겹침으로 점수화.
    반환: [(game, match_score 0~100), ...]  (점수 내림차순, 상위 limit)
    """
    qs = Game.objects.prefetch_related('genres').all()

    # 하드 필터 (조건이 명시됐을 때만)
    if intent.get('price_max') is not None:
        qs = qs.filter(final_price__isnull=False,
                       final_price__lte=intent['price_max'])
    if intent.get('is_korean') is True:
        qs = qs.filter(is_korean=True)

    want_genres = {g.lower() for g in intent.get('genres', [])}
    keywords = [k.lower() for k in intent.get('keywords', []) if k]

    scored = []
    for game in qs:
        gnames = {gn.lower() for gn in
                  game.genres.values_list('genre_name', flat=True)}
        score = 30 * len(want_genres & gnames)                 # 장르 일치
        title = (game.title or '').lower()
        score += 10 * sum(1 for k in keywords if k in title)   # 제목 키워드
        if game.metacritic_score:                              # 평점 가산(0~5)
            score += min(game.metacritic_score, 100) // 20
        if score > 0:
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


# ── 폴백(랜덤) 경로 — 기존 placeholder 동작 그대로 ────────────────
def _random_games(limit):
    return [(g, None) for g in Game.objects.order_by('?')[:limit]]


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
