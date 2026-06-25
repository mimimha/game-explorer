"""
RAWG(메타) + Steam(가격) + YouTube(영상)을 합쳐 Game 을 적재한다.

사용:
  python manage.py load_games --pages 1 --page-size 20
  python manage.py load_games --pages 3 --dates 2023-01-01,2023-12-31
  python manage.py load_games --no-steam --no-youtube   # 일부 소스 생략
"""
import time
from django.core.management.base import BaseCommand
from django.db import transaction

from games.models import (
    Game, Genre, GameTag, Platform, GamePlatform, Screenshot, GameVideo,
    Mood, GameMood,
)
from games.services import rawg, steam_price, youtube


class Command(BaseCommand):
    help = 'RAWG + Steam + YouTube 로 게임 데이터를 적재한다.'

    def add_arguments(self, parser):
        parser.add_argument('--pages', type=int, default=1,
                            help='가져올 RAWG 페이지 수')
        parser.add_argument('--start-page', type=int, default=1,
                            help='시작 페이지(이어받기용). 예: 9 → 9페이지부터 pages만큼')
        parser.add_argument('--page-size', type=int, default=20)
        parser.add_argument('--ordering', type=str, default='-added')
        parser.add_argument('--dates', type=str, default=None,
                            help="출시일 범위 예: 2023-01-01,2023-12-31")
        parser.add_argument('--genres', type=str, default=None,
                            help="RAWG 장르 슬러그(콤마). 예: indie")
        parser.add_argument('--tags', type=str, default=None,
                            help="RAWG 태그 슬러그(콤마). 예: cute,cozy — 특정 스타일만")
        parser.add_argument('--no-steam', action='store_true',
                            help='Steam 가격 수집 생략')
        parser.add_argument('--no-youtube', action='store_true',
                            help='YouTube 영상 수집 생략')
        parser.add_argument('--translate', action='store_true',
                            help='적재 후 미번역 설명을 무료 자동 번역(Google)')
        parser.add_argument('--sleep', type=float, default=0.3,
                            help='API 호출 간 대기(초) — rate limit 보호')

    def handle(self, *args, **opts):
        total = 0
        start = opts['start_page']
        for page in range(start, start + opts['pages']):
            self.stdout.write(f'\n=== RAWG page {page} ===')
            games = None
            for attempt in range(3):       # 일시적 502 등은 재시도
                try:
                    games = rawg.fetch_game_list(
                        page=page, page_size=opts['page_size'],
                        ordering=opts['ordering'], dates=opts['dates'],
                        genres=opts['genres'], tags=opts['tags'],
                    )
                    break
                except Exception as e:
                    self.stderr.write(self.style.WARNING(
                        f'목록 호출 실패(page {page}, 시도 {attempt + 1}/3): {e}'))
                    time.sleep(2 * (attempt + 1))
            if games is None:              # 3번 다 실패 → 이 페이지만 건너뛰고 계속(중단 X)
                self.stderr.write(self.style.ERROR(f'page {page} 건너뜀'))
                continue

            for stub in games:
                try:
                    self._load_one(stub['id'], opts)
                    total += 1
                except Exception as e:
                    self.stderr.write(
                        self.style.WARNING(f"  ! {stub.get('name')} 실패: {e}")
                    )
                time.sleep(opts['sleep'])

        self.stdout.write(self.style.SUCCESS(f'\n완료: {total}개 게임 적재/갱신'))

        if opts.get('translate'):     # 적재 후 미번역 설명 자동 번역(무료 Google)
            from django.core.management import call_command
            self.stdout.write('\n설명 자동 번역(Google, 무료) 시작...')
            call_command('translate_games', stdout=self.stdout)

    @transaction.atomic
    def _load_one(self, rawg_id, opts):
        # 1) RAWG 상세
        detail = rawg.fetch_game_detail(rawg_id)
        fields = rawg.parse_game_fields(detail)

        # 표지(capsule) 없는 게임은 적재하지 않는다 — 화면에 빈 표지 junk 로 뜨는 것 방지
        if not fields.get('capsule_url'):
            raise ValueError('표지 없음 — 스킵')

        # 2) 플레이 인원/모드 — RAWG tags 우선
        modes = rawg.extract_player_modes(detail)

        # 2-2) Steam appid → 가격(+ 인원 폴백)
        if not opts['no_steam']:
            appid = rawg.fetch_steam_appid(rawg_id)
            if appid:
                fields['steam_id'] = appid
                steam = steam_price.fetch_app_details(appid)
                for k in ('initial_price', 'final_price', 'is_korean'):
                    if k in steam:
                        fields[k] = steam[k]
                if modes is None:                 # RAWG 근거 없을 때만 Steam 폴백
                    modes = steam.get('modes')

        # 2-3) 인원 모드 확정 (둘 다 없으면 null 유지)
        if modes is not None:
            fields['is_singleplayer'] = modes['single']
            fields['is_multiplayer'] = modes['multi']
            fields['is_coop'] = modes['coop']
            fields['offline'] = modes['single']   # offline == 싱글플레이 가능

        # 3) upsert (rawg_id 기준)
        game, created = Game.objects.update_or_create(
            rawg_id=fields['rawg_id'],
            defaults=fields,
        )
        flag = '＋ 신규' if created else '↻ 갱신'
        self.stdout.write(f'  {flag}: {game.title}')

        # 4) 장르 (Genre upsert → GameTag 연결)
        for name in rawg.extract_genre_names(detail):
            genre, _ = Genre.objects.get_or_create(genre_name=name)
            GameTag.objects.get_or_create(game=game, tag=genre)

        # 4-2) 플랫폼 (Platform upsert → GamePlatform 연결)
        for name in rawg.extract_platform_names(detail):
            platform, _ = Platform.objects.get_or_create(platform_name=name)
            GamePlatform.objects.get_or_create(game=game, platform=platform)

        # 4-3) 무드 (RAWG 태그 화이트리스트 → Mood upsert → GameMood 연결)
        for name in rawg.extract_mood_names(detail):
            mood, _ = Mood.objects.get_or_create(mood_name=name)
            GameMood.objects.get_or_create(game=game, mood=mood)

        # 5) 스크린샷 (기존 것 비우고 새로)
        shots = rawg.fetch_screenshots(rawg_id)
        if shots:
            game.screenshots.all().delete()
            Screenshot.objects.bulk_create([
                Screenshot(game=game, image_url=url) for url in shots
            ])

        # 6) 영상 — 트레일러 1개 + 공략(스트리밍) 3개(한국 제작 조회수순 우선)
        #    이미 영상이 있으면 건너뛴다(쿼터 보호). 새 걸로 교체는 admin 리뉴얼 버튼.
        if not opts['no_youtube'] and not game.videos.exists():
            rows = []  # (video_dict, video_type)

            # 6-1) 트레일러 1개 (없으면 RAWG 트레일러 폴백)
            trailers = youtube.search_videos(
                game.title, query_terms='gameplay trailer', max_results=1,
            )
            if not trailers:
                trailers = [
                    {'title': m['name'], 'video_url': m['url'], 'thumbnail': ''}
                    for m in rawg.fetch_movies(rawg_id)[:1]
                ]
            rows += [(v, GameVideo.TRAILER) for v in trailers[:1]]

            # 6-2) 공략 3개 — 한국 제작(조회수순) 우선, 부족 시 해외 영상
            walkthroughs = youtube.search_walkthroughs(
                game.title, game.title_ko, n=3,
            )
            rows += [(v, GameVideo.WALKTHROUGH) for v in walkthroughs[:3]]

            if rows:
                game.videos.all().delete()
                GameVideo.objects.bulk_create([
                    GameVideo(
                        game=game, video_type=vtype, title=v['title'],
                        video_url=v['video_url'], thumbnail=v['thumbnail'],
                        channel=v.get('channel', ''),
                        published_at=v.get('published_at', ''),
                    ) for v, vtype in rows
                ])