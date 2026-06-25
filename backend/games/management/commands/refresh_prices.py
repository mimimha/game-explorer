"""적재된 게임의 Steam 가격을 다시 긁어 갱신한다 (Steam 가격 변동·할인 반영).

steam_id 있는 게임만 → steam_price.fetch_app_details → initial_price/final_price/is_korean 갱신.
RAWG·YouTube 미사용, Steam 만 호출.

[갱신 순서] 가장 오래 갱신 안 된 게임부터 처리한다(price_updated_at 오름차순, null 최우선).
   → 버튼/명령을 여러 번 나눠 돌리면 전체가 빠짐없이 골고루 최신화된다.
   (랜덤이 아니라 '오래된 것 우선'이라, 방금 갱신한 건 당분간 다시 안 건드림)

⚠️ Steam appdetails 는 IP당 rate limit(대략 5분에 200회)이 있어, 한 번에 수백 개까지만 안전.
   전체(수천 개)는 --sleep 을 키워 여러 번 나눠 돌린다.

사용:
  python manage.py refresh_prices              # 오래된 것부터 전체
  python manage.py refresh_prices --limit 150  # 오래된 것부터 150개
  python manage.py refresh_prices --ids 12,45
"""
import time
from django.core.management.base import BaseCommand
from django.utils import timezone

from games.models import Game
from games.services import steam_price


class Command(BaseCommand):
    help = 'Steam 가격 재수집 (steam_id 있는 게임의 가격·할인·한국어지원 갱신).'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None)
        parser.add_argument('--ids', type=str, default=None,
                            help='특정 game_id 만 (콤마)')
        parser.add_argument('--sleep', type=float, default=0.4,
                            help='호출 간 대기(초) — Steam rate limit 보호')

    def handle(self, *args, **opts):
        qs = Game.objects.exclude(steam_id__isnull=True)
        if opts['ids']:
            ids = [int(x) for x in opts['ids'].split(',') if x.strip().isdigit()]
            qs = qs.filter(game_id__in=ids)
        else:
            # 가장 오래 갱신 안 된 것부터(null=아직 한 번도 안 함 → 맨 앞).
            # 나눠 돌릴 때마다 다음으로 오래된 게임이 자동으로 대상이 된다.
            qs = qs.order_by('price_updated_at')
        if opts['limit']:
            qs = qs[:opts['limit']]
        games = list(qs)
        self.stdout.write(f'가격 재수집 대상 {len(games)}개 (오래된 것부터)')

        ok = changed = 0
        for g in games:
            try:
                d = steam_price.fetch_app_details(g.steam_id)
                fields = [k for k in ('initial_price', 'final_price', 'is_korean')
                          if k in d]
                # 호출에 성공했으면(가격 변동이 없더라도) 갱신 시각은 항상 찍는다.
                # → 다음 실행에서 이 게임을 '방금 한 것'으로 보고 뒤로 미룬다.
                for k in fields:
                    setattr(g, k, d[k])
                g.price_updated_at = timezone.now()
                g.save(update_fields=fields + ['price_updated_at'])
                if fields:
                    changed += 1
                ok += 1
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'  ! {g.title[:30]} 실패: {e}'))
            time.sleep(opts['sleep'])
        self.stdout.write(self.style.SUCCESS(
            f'완료: {ok}/{len(games)} 호출, {changed}개 가격 갱신'))