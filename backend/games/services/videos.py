"""상세 조회 시 영상이 없으면 그 순간 YouTube 에서 가져와 저장하는 lazy 로더.

eager(미리 전부 적재)와 달리, 사용자가 실제로 연 게임만 — 게임당 한 번 —
호출해 GameVideo 로 저장한다. 다음 조회부터는 DB 에서 바로 나가 호출 0.
(backfill_videos._fill_one 의 기본 fetch 로직과 동일. 한 곳에서만 부르는 lazy 경로라
 기존 영상 삭제 없이 '비어 있을 때만' 채운다.)
"""
import logging

from games.models import GameVideo
from games.services import youtube

logger = logging.getLogger(__name__)


def fetch_videos_for(game, *, include_trailer=True, include_walkthrough=True):
    """game 의 영상을 YouTube 에서 가져와 저장하고 저장 개수를 반환.

    ⚠️ 이 호출 시점에 YouTube 쿼터를 소비한다(트레일러 1 + 공략 검색).
    호출자는 '영상이 비어 있을 때만' 부르는 책임을 진다.
    """
    rows = []  # (video_dict, video_type)

    if include_trailer:
        # 트레일러는 YouTube 만 사용. 없으면 표시 안 함(RAWG/Steam 폴백 미사용)
        # → 영상이 하나도 없으면 화면엔 "추후 업데이트 예정"이 뜬다.
        trailers = youtube.search_videos(
            game.title, query_terms='gameplay trailer', max_results=1,
        )
        rows += [(v, GameVideo.TRAILER) for v in trailers[:1]]

    if include_walkthrough:
        walkthroughs = youtube.search_walkthroughs(game.title, game.title_ko, n=4)
        rows += [(v, GameVideo.WALKTHROUGH) for v in walkthroughs[:4]]

    if rows:
        GameVideo.objects.bulk_create([
            GameVideo(
                game=game, video_type=vtype, title=v['title'],
                video_url=v['video_url'], thumbnail=v['thumbnail'],
                channel=v.get('channel', ''), published_at=v.get('published_at', ''),
            ) for v, vtype in rows
        ])
    logger.info('lazy 영상 로드 game=%s (%s) → %d개', game.game_id, game.title, len(rows))
    return len(rows)
