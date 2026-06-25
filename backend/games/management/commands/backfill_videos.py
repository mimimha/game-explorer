"""
영상(트레일러 1 + 공략 3)만 채운다. RAWG 상세/스팀/스크린샷은 호출하지 않아
YouTube 쿼터만 소비한다. (load_games 의 영상 단계만 떼어낸 것)
공략은 한국 제작(조회수순) 우선 → 부족하면 해외(영어권 등) 영상으로 채운다.

기본 대상: 공략(walkthrough)이 없는 게임.
  python manage.py backfill_videos --limit 10
  python manage.py backfill_videos --only-empty      # 영상이 아예 없는 게임만
  python manage.py backfill_videos                   # 공략 없는 게임 전체

키가 여러 개면(settings.YOUTUBE_DATA_API_KEYS) 한 키 소진 시 자동으로 다음 키 사용.
게임당 YouTube 검색 2~3회(트레일러 1 + 공략 1~2). 일일 쿼터 10,000 units = 100검색/키.
"""
import time
from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from games.models import Game, GameVideo
from games.services import rawg, youtube


class Command(BaseCommand):
    help = '트레일러 1 + 공략 2 영상만 백필 (YouTube 쿼터만 사용, 키 자동 전환).'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None)
        parser.add_argument('--only-empty', action='store_true',
                            help='영상이 아예 없는 게임만 대상')
        parser.add_argument('--refresh', action='store_true',
                            help='이미 영상이 있어도 새로 받아 교체 (관리자 리뉴얼용)')
        parser.add_argument('--ids', type=str, default=None,
                            help='특정 game_id 만 갱신 (콤마, 예: 12,45,77)')
        parser.add_argument('--trailer-only', action='store_true',
                            help='트레일러만(공략 생략) → 게임당 YouTube 검색 1회로 쿼터 절반')
        parser.add_argument('--walkthrough-only', action='store_true',
                            help='기존 영상(트레일러) 보존 + 공략만 덧붙임 → 검색 1회/게임')
        parser.add_argument('--sleep', type=float, default=0.3)

    def handle(self, *args, **opts):
        if opts['ids']:                       # 특정 게임만 교체
            id_list = [int(x) for x in opts['ids'].split(',') if x.strip().isdigit()]
            qs = Game.objects.filter(game_id__in=id_list)
        elif opts['refresh']:                 # 전체를 새 영상으로 교체 (리뉴얼)
            qs = Game.objects.all()
        elif opts['only_empty']:              # 영상이 아예 없는 게임만
            qs = Game.objects.annotate(v=Count('videos')).filter(v=0)
        else:                                 # (기본) 공략이 없는 게임만
            qs = Game.objects.annotate(
                w=Count('videos', filter=Q(videos__video_type='walkthrough'))
            ).filter(w=0)
        qs = qs.exclude(rawg_id__isnull=True).order_by('game_id')
        if opts['limit']:
            qs = qs[:opts['limit']]

        games = list(qs)
        self.stdout.write(f'대상 {len(games)}개\n')
        total = ok = 0
        for g in games:
            total += 1
            try:
                n = self._fill_one(g, trailer_only=opts['trailer_only'],
                                   walkthrough_only=opts['walkthrough_only'])
                ok += 1
                self.stdout.write(f'  ✓ {g.title[:40]:40} 영상 {n}개')
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'  ! {g.title} 실패: {e}'))
            time.sleep(opts['sleep'])

        self.stdout.write(self.style.SUCCESS(f'\n완료: {ok}/{total}'))

    def _fill_one(self, game, trailer_only=False, walkthrough_only=False):
        rows = []  # (video_dict, video_type)

        # 트레일러 1개 (없으면 RAWG 트레일러 폴백) — walkthrough_only면 생략(기존 보존)
        if not walkthrough_only:
            trailers = youtube.search_videos(
                game.title, query_terms='gameplay trailer', max_results=1,
            )
            if not trailers:
                trailers = [
                    {'title': m['name'], 'video_url': m['url'], 'thumbnail': ''}
                    for m in rawg.fetch_movies(game.rawg_id)[:1]
                ]
            rows += [(v, GameVideo.TRAILER) for v in trailers[:1]]

        # 공략 4개 — 한국 제작(조회수순) 우선, 부족 시 해외 영상. trailer_only면 생략
        # (트레일러 1 + 공략 4 = 게임당 영상 5개)
        if not trailer_only:
            walkthroughs = youtube.search_walkthroughs(
                game.title, game.title_ko, n=4,
            )
            rows += [(v, GameVideo.WALKTHROUGH) for v in walkthroughs[:4]]

        if rows:
            # walkthrough_only면 기존 영상(트레일러)을 지우지 않고 덧붙인다
            if not walkthrough_only:
                game.videos.all().delete()
            GameVideo.objects.bulk_create([
                GameVideo(
                    game=game, video_type=vtype, title=v['title'],
                    video_url=v['video_url'], thumbnail=v['thumbnail'],
                    channel=v.get('channel', ''),
                    published_at=v.get('published_at', ''),
                ) for v, vtype in rows
            ])
        return len(rows)
