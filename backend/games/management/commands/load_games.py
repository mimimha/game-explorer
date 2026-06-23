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
)
from games.services import rawg, steam_price, youtube


class Command(BaseCommand):
    help = 'RAWG + Steam + YouTube 로 게임 데이터를 적재한다.'

    def add_arguments(self, parser):
        parser.add_argument('--pages', type=int, default=1,
                            help='가져올 RAWG 페이지 수')
        parser.add_argument('--page-size', type=int, default=20)
        parser.add_argument('--ordering', type=str, default='-added')
        parser.add_argument('--dates', type=str, default=None,
                            help="출시일 범위 예: 2023-01-01,2023-12-31")
        parser.add_argument('--no-steam', action='store_true',
                            help='Steam 가격 수집 생략')
        parser.add_argument('--no-youtube', action='store_true',
                            help='YouTube 영상 수집 생략')
        parser.add_argument('--sleep', type=float, default=0.3,
                            help='API 호출 간 대기(초) — rate limit 보호')

    def handle(self, *args, **opts):
        total = 0
        for page in range(1, opts['pages'] + 1):
            self.stdout.write(f'\n=== RAWG page {page} ===')
            try:
                games = rawg.fetch_game_list(
                    page=page, page_size=opts['page_size'],
                    ordering=opts['ordering'], dates=opts['dates'],
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'목록 호출 실패: {e}'))
                break

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

    @transaction.atomic
    def _load_one(self, rawg_id, opts):
        # 1) RAWG 상세
        detail = rawg.fetch_game_detail(rawg_id)
        fields = rawg.parse_game_fields(detail)

        # 2) Steam appid → 가격
        if not opts['no_steam']:
            appid = rawg.fetch_steam_appid(rawg_id)
            if appid:
                fields['steam_id'] = appid
                price = steam_price.fetch_price(appid)
                fields.update(price)  # initial_price/final_price/is_korean/offline

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

        # 5) 스크린샷 (기존 것 비우고 새로)
        shots = rawg.fetch_screenshots(rawg_id)
        if shots:
            game.screenshots.all().delete()
            Screenshot.objects.bulk_create([
                Screenshot(game=game, image_url=url) for url in shots
            ])

        # 6) 영상 — YouTube 검색 (없으면 RAWG 트레일러 폴백)
        if not opts['no_youtube']:
            vids = youtube.search_videos(game.title)
            if not vids:
                vids = [
                    {'title': m['name'], 'video_url': m['url'], 'thumbnail': ''}
                    for m in rawg.fetch_movies(rawg_id)
                ]
            if vids:
                game.videos.all().delete()
                GameVideo.objects.bulk_create([
                    GameVideo(
                        game=game, title=v['title'],
                        video_url=v['video_url'], thumbnail=v['thumbnail'],
                    ) for v in vids
                ])