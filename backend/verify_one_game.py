"""한 게임에 대해 새 영상 파이프라인(트레일러1+공략2)을 실행해 결과 확인 (임시)."""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from games.models import Game, GameVideo
from games.services import youtube

title = sys.argv[1] if len(sys.argv) > 1 else 'The Witcher 3: Wild Hunt'
game = Game.objects.filter(title=title).first()
if not game:
    print('게임 못 찾음:', title); sys.exit(1)

rows = []
trailers = youtube.search_videos(game.title, query_terms='gameplay trailer', max_results=1)
rows += [(v, GameVideo.TRAILER) for v in trailers[:1]]
walkthroughs = youtube.search_videos(game.title, query_terms='공략 walkthrough',
                                     max_results=2, video_duration='long')
rows += [(v, GameVideo.WALKTHROUGH) for v in walkthroughs[:2]]

game.videos.all().delete()
GameVideo.objects.bulk_create([
    GameVideo(game=game, video_type=t, title=v['title'], video_url=v['video_url'],
              thumbnail=v['thumbnail'], channel=v.get('channel', ''),
              published_at=v.get('published_at', '')) for v, t in rows
])

print(f'\n=== {game.title} — 저장된 영상 ===')
for vv in game.videos.all():
    print(f"  [{vv.video_type:11}] {vv.title[:50]:50} | {vv.channel[:18]:18} | thumb={'O' if vv.thumbnail else 'X'} | {vv.video_url}")
