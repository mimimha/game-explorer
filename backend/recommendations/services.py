"""
AI 추천 계산 로직 — GMS(LLM) "카탈로그 픽" 단일 호출 방식.

흐름:
  1) 우리 Game 카탈로그(id·제목·장르·짧은 소개)를 구성
  2) 사용자 요청 + 카탈로그를 GMS 에 한 번 보내, 목록 안에서만 N개를 고르게 함
     → "도트 느낌의 공포게임" 같은 모호한 표현도 LLM 이 판단해 매칭
  3) 반환된 game_id 를 검증(목록 밖 = 환각 → 폐기)하고 결과로 변환

settings.RECOMMEND_USE_LLM 이 False 거나 GMS 호출이 실패하면
랜덤 placeholder 로 안전하게 폴백한다. (키 없이도 동작/시연 가능)

⚠️ 토큰: _pick_games() 안의 gms.chat_json() 호출에서만 GMS 토큰이 소비된다.
   RECOMMEND_USE_LLM=False 이면 호출 자체가 없어 토큰 0.
"""
import json
import logging

from django.conf import settings

from games.models import Game
from . import gms

logger = logging.getLogger(__name__)

# 카탈로그에 게임 소개(description)를 포함할지 — True 면 매칭 품질↑·토큰↑,
# False 면 제목+장르만(토큰 약 절반).
CATALOG_WITH_DESC = True      # GMS는 호출당 과금이라 소개 포함해도 추가비용 0 → 품질↑
DESC_CHARS = 90               # 소개를 보낼 때 게임당 최대 글자수


def generate_recommendations(prompt: str, user=None, limit: int = 5):
    """
    prompt(요청 문장) → [{'game_id': int, 'reason': str, 'match_score': int}, ...]
    LLM 경로 실패 시 어떤 예외든 잡아 랜덤으로 폴백한다.
    """
    if settings.RECOMMEND_USE_LLM:
        try:
            return _llm_recommendations(prompt, limit=limit)
        except Exception as e:  # 네트워크/파싱/키 등 모든 실패 → 폴백
            logger.warning('LLM 추천 실패, 랜덤 폴백: %s', e)

    return _random_recommendations(prompt, limit=limit)


# ── LLM 경로 ─────────────────────────────────────────────────────
def _llm_recommendations(prompt, limit=5):
    catalog = _build_catalog()
    picks = _pick_games(prompt, catalog, limit)        # GMS 1회 호출

    # 목록에 실제로 존재하는 game_id 만 사용(환각 방지)
    valid = set(Game.objects.values_list('game_id', flat=True))
    results = []
    for rank, p in enumerate(picks):
        gid = p.get('game_id')
        if gid in valid:
            results.append({
                'game_id': gid,
                'reason': (p.get('reason') or _fallback_reason(prompt)).strip(),
                'match_score': max(50, 95 - rank * 9),  # 순위 기반 점수
            })
        if len(results) >= limit:
            break

    return results or _random_recommendations(prompt, limit=limit)


def _build_catalog():
    """LLM 에 보낼 우리 게임 목록. (토큰 절약 위해 최소 필드만)"""
    qs = Game.objects.prefetch_related('genres').all()
    catalog = []
    for g in qs:
        item = {
            'id': g.game_id,
            'title': g.title,
            'genres': list(g.genres.values_list('genre_name', flat=True)),
        }
        if CATALOG_WITH_DESC and g.description:
            item['desc'] = g.description[:DESC_CHARS]
        catalog.append(item)
    return catalog


def _pick_games(prompt, catalog, limit):
    """
    GMS 단일 호출: 요청 + 카탈로그 → [{game_id, reason}].
    ⚠️ 여기서만 토큰 소비.
    """
    system = (
        '너는 인디 게임 추천 큐레이터다. 아래 [게임 목록] 안에서만 사용자 요청에 '
        '잘 맞는 게임을 골라라.\n'
        '규칙:\n'
        f'- 1순위: 요청에 "정확히" 맞는 게임을 고른다. 사용자가 아트스타일(예: 도트/픽셀)과 '
        '분위기·장르(예: 공포)를 함께 요구하면, 그 조건을 모두 충족하는 게임이 정확히 맞는 것이다.\n'
        f'- 정확히 맞는 게임이 {limit}개보다 적으면, 분위기나 스타일이 비슷한 게임으로 '
        f'{limit}개까지 채운다. 단 요청과 전혀 무관한 게임은 넣지 마라.\n'
        '- 정확히 맞는 게임의 reason 은 자연스럽게 쓰고, 비슷해서(정확히는 아니지만) 채운 게임은 '
        'reason 을 "비슷한 분위기 · " 로 시작해 구분되게 쓴다.\n'
        '- 반드시 목록에 있는 game_id(id 필드)만 사용한다. 목록에 없는 게임은 절대 만들지 않는다.\n'
        '- "도트/픽셀 느낌", "공포", "힐링" 같은 분위기·아트스타일·장르 표현은 '
        '제목·장르·소개와 네가 아는 게임 지식을 종합해 판단한다.\n'
        '- reason 은 "고른 바로 그 게임"에 대한 설명이어야 한다. '
        '목록에 없는 다른 게임 이름을 reason 에 절대 언급하지 마라.\n'
        '- reason 은 한국어 한 문장(40자 내외)으로, 그 게임이 요청과 어떻게 맞는지 설명한다.\n'
        '- JSON 으로만 답한다. 형식: '
        '{"recommendations": [{"game_id": <id>, "reason": "<한국어 문장>"}, ...]}'
    )
    user_msg = json.dumps(
        {'request': prompt, 'count': limit, 'games': catalog},
        ensure_ascii=False,
    )
    data = gms.chat_json(
        [{'role': 'system', 'content': system},
         {'role': 'user', 'content': user_msg}],
        temperature=0.3,
    )
    return data.get('recommendations', []) or []


# ── 폴백(랜덤) 경로 ───────────────────────────────────────────────
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
