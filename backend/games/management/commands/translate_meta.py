"""
GMS로 게임 소개(description, 영문)를 한국어로 번역해 description_ko 를 채운다.

⚠️ GMS는 호출당 과금이라, 여러 게임을 한 번에 묶어(batch) 번역해 크레딧을 아낀다.
   예) 112개를 batch=10 으로 → 약 12회 호출.

사용:
  python manage.py translate_meta                      # 미번역 전체, 기본 모델
  python manage.py translate_meta --model gpt-4.1-nano # 저렴한 모델로
  python manage.py translate_meta --batch 10 --limit 20
  python manage.py translate_meta --retranslate        # 이미 번역된 것도 다시
"""
import json
from django.core.management.base import BaseCommand

from games.models import Game
from recommendations import gms


class Command(BaseCommand):
    help = 'GMS로 description → description_ko 번역 (배치 호출)'

    def add_arguments(self, parser):
        parser.add_argument('--batch', type=int, default=10,
                            help='한 번의 GMS 호출에 묶을 게임 수 (호출 수 = 대상/batch)')
        parser.add_argument('--limit', type=int, default=0,
                            help='번역할 최대 게임 수 (0이면 전체)')
        parser.add_argument('--model', type=str, default=None,
                            help='번역에 쓸 GMS 모델 (미지정 시 settings.GMS_MODEL)')
        parser.add_argument('--retranslate', action='store_true',
                            help='이미 번역된 것(description_ko 있음)도 다시 번역')

    def handle(self, *args, **opts):
        qs = Game.objects.exclude(description='')
        if not opts['retranslate']:
            qs = qs.filter(description_ko='')
        games = list(qs)
        if opts['limit']:
            games = games[:opts['limit']]

        batch = max(1, opts['batch'])
        calls = (len(games) + batch - 1) // batch
        self.stdout.write(
            f'번역 대상: {len(games)}개 | batch={batch} → 예상 GMS 호출 {calls}회'
        )

        system = (
            '너는 게임 소개 번역가다. 입력은 게임 소개 목록(JSON 배열)이다. '
            '각 항목의 desc 를 자연스러운 한국어로 번역하라. '
            '게임 제목·고유명사·캐릭터명은 원문(영문) 그대로 둬도 된다. '
            'JSON 으로만 답한다. 형식: '
            '{"translations": [{"id": <id>, "ko": "<한국어 번역>"}, ...]}'
        )

        done = 0
        for i in range(0, len(games), batch):
            chunk = games[i:i + batch]
            payload = [{'id': g.game_id, 'desc': g.description} for g in chunk]
            try:
                data = gms.chat_json(
                    [{'role': 'system', 'content': system},
                     {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
                    temperature=0.2,
                    model=opts['model'],
                )
                tmap = {t['id']: (t.get('ko') or '')
                        for t in data.get('translations', []) if 'id' in t}
                n = 0
                for g in chunk:
                    ko = tmap.get(g.game_id)
                    if ko:
                        g.description_ko = ko
                        g.save(update_fields=['description_ko'])
                        done += 1
                        n += 1
                self.stdout.write(f'  호출 {i // batch + 1}/{calls}: {n}/{len(chunk)}개 번역')
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'  호출 {i // batch + 1} 실패: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n완료: {done}개 번역 저장'))
