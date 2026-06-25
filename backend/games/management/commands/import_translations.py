"""
LLM 이 번역한 JSON 을 읽어 Game.title_ko / description_ko 에 로드한다.

  python manage.py import_translations translated.json
  python manage.py import_translations translated.json --overwrite-locked

입력 형식 (둘 다 허용):
  [{"id": 1, "title_ko": "하프라이프 2", "description_ko": "..."}, ...]
  {"games": [ ... 위와 동일 ... ]}

규칙:
  - id 로 매칭. translation_locked=True 인 게임은 건너뜀(--overwrite-locked 면 무시하고 덮어씀).
  - title_ko 가 있으면 갱신. description_ko 는 비어있지 않을 때만 갱신(부분 번역 보호).
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError

from games.models import Game


class Command(BaseCommand):
    help = '번역된 JSON 을 title_ko/description_ko 로 로드한다.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='번역된 JSON 파일 경로')
        parser.add_argument('--overwrite-locked', action='store_true',
                            help='translation_locked 게임도 덮어씀')

    def handle(self, *args, **opts):
        path = Path(opts['path'])
        if not path.exists():
            raise CommandError(f'파일 없음: {path}')
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise CommandError(f'JSON 파싱 실패: {e}')

        rows = data.get('games', data) if isinstance(data, dict) else data
        if not isinstance(rows, list):
            raise CommandError('최상위가 배열 또는 {"games": [...]} 형식이어야 합니다.')

        updated = skipped_lock = missing = 0
        for r in rows:
            try:
                gid = int(r['id'])
            except (KeyError, ValueError, TypeError):
                continue
            try:
                game = Game.objects.get(game_id=gid)
            except Game.DoesNotExist:
                missing += 1
                continue
            if game.translation_locked and not opts['overwrite_locked']:
                skipped_lock += 1
                continue

            fields = []
            title_ko = (r.get('title_ko') or '').strip()
            if title_ko:
                game.title_ko = title_ko[:200]
                fields.append('title_ko')
            desc_ko = (r.get('description_ko') or '').strip()
            if desc_ko:
                game.description_ko = desc_ko
                fields.append('description_ko')

            if fields:
                game.save(update_fields=fields)
                updated += 1
                self.stdout.write(f'  {game.title[:40]:40} → {game.title_ko}')

        self.stdout.write(self.style.SUCCESS(
            f'\n완료: {updated}개 갱신'
            + (f', 잠금 건너뜀 {skipped_lock}' if skipped_lock else '')
            + (f', 매칭 실패 {missing}' if missing else '')
        ))
