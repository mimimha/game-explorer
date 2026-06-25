"""
표지(썸네일) 비전 분석으로 thumbnail_subjects 를 채운다. (GMS 비전 모델 사용)

  python manage.py backfill_thumbnails           # 아직 분석 안 된 게임만
  python manage.py backfill_thumbnails --refresh # 전체 재분석
  python manage.py backfill_thumbnails --limit 10

게임당 비전 호출 1회. capsule_url 없는 게임은 건너뜀.
"""
import time
from django.core.management.base import BaseCommand

from games.models import Game
from games.services import vision


class Command(BaseCommand):
    help = '표지 이미지 시각 소재(thumbnail_subjects) 태깅 (GMS 비전).'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None)
        parser.add_argument('--refresh', action='store_true',
                            help='이미 태깅된 것도 다시 분석')
        parser.add_argument('--sleep', type=float, default=0.3)

    def handle(self, *args, **opts):
        qs = Game.objects.exclude(capsule_url='').order_by('game_id')
        if not opts['refresh']:
            qs = qs.filter(thumbnail_subjects=[])   # 아직 분석 안 된 것만
        if opts['limit']:
            qs = qs[:opts['limit']]

        games = list(qs)
        self.stdout.write(f'대상 {len(games)}개\n')
        total = ok = 0
        for g in games:
            total += 1
            try:
                subs = vision.analyze_subjects(g.capsule_url)
                g.thumbnail_subjects = subs
                g.save(update_fields=['thumbnail_subjects'])
                ok += 1
                self.stdout.write(f'  ✓ {g.title[:38]:38} {subs}')
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'  ! {g.title} 실패: {e}'))
            time.sleep(opts['sleep'])

        self.stdout.write(self.style.SUCCESS(f'\n완료: {ok}/{total} 태깅'))
