"""
번역할 게임 데이터(id/title/description)를 JSON 파일로 내보낸다.
이 파일을 LLM 에 넘겨 번역 → import_translations 로 다시 로드한다.

기본은 '아직 번역 안 된' 게임만(빈 title_ko 또는 빈 description_ko, 잠금 제외).
  python manage.py export_translations
  python manage.py export_translations --all          # 전체
  python manage.py export_translations -o out.json     # 출력 경로 지정

출력 형식:
  [{"id": 1, "title": "Half-Life 2", "description": "..."}, ...]

LLM 에게 시킬 일(예):
  "각 항목에 title_ko(한국 게이머가 쓰는 한글명/음역, 의역 금지 — Half-Life→하프라이프),
   description_ko(자연스러운 한국어 번역)를 더해 같은 JSON 배열로 돌려줘."
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db.models import Q

from games.models import Game


class Command(BaseCommand):
    help = '번역할 게임(id/title/description)을 JSON 으로 내보낸다.'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true',
                            help='미번역분만이 아니라 전체 내보내기')
        parser.add_argument('-o', '--output', type=str,
                            default='games/fixtures/to_translate.json')

    def handle(self, *args, **opts):
        qs = Game.objects.filter(translation_locked=False).order_by('game_id')
        if not opts['all']:
            qs = qs.filter(Q(title_ko='') | Q(description_ko=''))

        rows = [
            {'id': g.game_id, 'title': g.title, 'description': g.description}
            for g in qs
        ]

        out = Path(opts['output'])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        self.stdout.write(self.style.SUCCESS(
            f'{len(rows)}개 게임을 {out} 로 내보냈습니다.'
        ))
        if rows:
            self.stdout.write(
                'LLM 에 넘겨 각 항목에 title_ko / description_ko 를 추가한 JSON 을 받아\n'
                'python manage.py import_translations <받은파일.json> 로 로드하세요.'
            )
