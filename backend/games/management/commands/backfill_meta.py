"""
기존 게임에 playtime / 플레이인원 / 무드만 백필한다. (YouTube·스크린샷 미호출 → 쿼터 보호)

사용:
  python manage.py backfill_meta              # rawg_id 있는 전체
  python manage.py backfill_meta --limit 20
  python manage.py backfill_meta --no-steam   # Steam 인원 폴백 생략
"""
import time
from django.core.management.base import BaseCommand
from django.db import transaction

from games.models import Game, Mood, GameMood
from games.services import rawg, steam_price


class Command(BaseCommand):
    help = 'playtime/플레이인원/무드 백필 (영상·스크린샷 제외).'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None)
        parser.add_argument('--no-steam', action='store_true')
        parser.add_argument('--moods-only', action='store_true',
                            help='무드만 갱신 (playtime·인원 미변경)')
        parser.add_argument('--sleep', type=float, default=0.3)

    def handle(self, *args, **opts):
        qs = Game.objects.exclude(rawg_id__isnull=True).order_by('game_id')
        if opts['limit']:
            qs = qs[:opts['limit']]

        total = ok = 0
        for game in qs:
            total += 1
            try:
                self._backfill_one(game, opts)
                ok += 1
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'  ! {game.title} 실패: {e}'))
            time.sleep(opts['sleep'])

        self.stdout.write(self.style.SUCCESS(f'\n완료: {ok}/{total} 백필'))

    @transaction.atomic
    def _backfill_one(self, game, opts):
        detail = rawg.fetch_game_detail(game.rawg_id)

        if not opts['moods_only']:
            # playtime
            pt = detail.get('playtime')
            game.playtime = pt if pt else None

            # 플레이 인원/모드 — RAWG 우선, 없으면 Steam 폴백
            modes = rawg.extract_player_modes(detail)
            if modes is None and not opts['no_steam']:
                appid = game.steam_id or rawg.fetch_steam_appid(game.rawg_id)
                if appid:
                    if not game.steam_id:
                        game.steam_id = appid
                    modes = steam_price.fetch_app_details(appid).get('modes')
            if modes is not None:
                game.is_singleplayer = modes['single']
                game.is_multiplayer = modes['multi']
                game.is_coop = modes['coop']
                game.offline = modes['single']

            game.save(update_fields=[
                'playtime', 'is_singleplayer', 'is_multiplayer', 'is_coop',
                'offline', 'steam_id',
            ])

        # 무드 (기존 연결 비우고 새로)
        GameMood.objects.filter(game=game).delete()
        for name in rawg.extract_mood_names(detail):
            mood, _ = Mood.objects.get_or_create(mood_name=name)
            GameMood.objects.get_or_create(game=game, mood=mood)

        pm = ''.join(['S' if game.is_singleplayer else '·',
                      'M' if game.is_multiplayer else '·',
                      'C' if game.is_coop else '·'])
        self.stdout.write(
            f'  ↻ {game.title[:40]:40} pt={game.playtime or "-":>3} [{pm}] '
            f'moods={game.moods.count()}'
        )
