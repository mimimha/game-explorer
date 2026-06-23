"""
추천 계산 로직.

현재는 동작 확인용 임시(placeholder) 구현이다.
추후 F06 에서 2층 구조로 교체:
  1) content 기반 필터 → 후보 게임 + match_score
  2) LLM → 각 후보의 reason(추천 이유) 생성
"""
from games.models import Game


def generate_recommendations(prompt: str, user=None, limit: int = 5):
    """
    prompt(취향 문장)를 받아 추천 목록을 반환.
    반환 형식: [{'game_id': int, 'reason': str, 'match_score': int}, ...]

    ※ 임시: 무작위 게임 몇 개에 더미 이유/점수를 붙여 반환.
       실제 추천 알고리즘으로 교체 예정.
    """
    games = Game.objects.order_by('?')[:limit]
    results = []
    for rank, game in enumerate(games):
        results.append({
            'game_id': game.game_id,
            'reason': f'"{prompt[:20]}" 취향과 잘 맞을 만한 게임이에요.',  # TODO: LLM
            'match_score': max(50, 95 - rank * 8),  # TODO: content 필터 점수
        })
    return results