"""게임 번역 — 설명(무료 Google) + 제목(GMS LLM 음차)을 한 커맨드로.

설명(description_ko): deep-translator(Google). 무료·키 불필요. 완전한 문장이라 안정적.
제목(title_ko): GMS LLM. ⚠️ 호출당 과금. Google과 달리 LLM은 "게임 제목은 직역 말고
  음차"를 이해한다(Dead Space→"데드 스페이스" O, "죽은 공간" X). 제목은 짧아 한 콜에 많이 묶음.

기본은 '설명만'(무료). 제목은 `--titles`(설명+제목) 또는 `--titles-only` 로 명시할 때만.

사용:
  python manage.py translate_games                 # 설명만 (무료 Google)
  python manage.py translate_games --titles        # 설명(무료) + 제목(GMS 과금)
  python manage.py translate_games --titles-only   # 제목만 (GMS 과금)
  python manage.py translate_games --limit 100 --ids 12,45
"""
import json
import re
import time
from django.core.management.base import BaseCommand

from games.models import Game
from recommendations import gms

MIN_LEN = 20          # 이보다 짧은 설명은 제목 같은 텍스트 → 스킵(오역 방지)
MAX_CHUNK = 4500      # Google 1회 요청 한도(5000자) 보호
_HANGUL = re.compile(r'[가-힣]')


def _needs_translation(ko):
    """번역본(_ko)이 비었거나 한글이 하나도 없으면(영어 등이 들어감) → 번역 필요."""
    return not ko or _HANGUL.search(ko) is None

TITLE_SYSTEM = (
    '너는 영어 게임 제목을 한국어 표기로 바꾸는 전문가다. 입력은 게임 제목 목록(JSON 배열).\n'
    '규칙:\n'
    '- 공식 한국어 제목이 있으면 그것을 쓴다.\n'
    '- 없으면 발음 그대로 한글로 음차(transliteration)한다.\n'
    '- 절대 "뜻"을 직역하지 마라. 예: "Dead Space"→"데드 스페이스"(O) "죽은 공간"(X), '
    '"Half-Life"→"하프라이프"(O) "반감기"(X), "Counter-Strike"→"카운터 스트라이크"(O) "반격"(X).\n'
    '- 숫자·부제·기호는 자연스럽게 유지. 예: "Portal 2"→"포탈 2".\n'
    '- 한국 게이머가 알아볼 수 있게.\n'
    'JSON 으로만 답한다. 형식: {"titles": [{"id": <id>, "ko": "<한국어 제목>"}, ...]}'
)


def _google_translate(translator, text):
    """긴 텍스트는 문장 경계로 잘라 번역 후 합친다(5000자 한도 회피)."""
    text = text.strip()
    if len(text) <= MAX_CHUNK:
        return translator.translate(text)
    chunks, buf = [], ''
    for part in text.split('. '):
        piece = part + '. '
        if len(buf) + len(piece) > MAX_CHUNK:
            chunks.append(buf)
            buf = piece
        else:
            buf += piece
    if buf:
        chunks.append(buf)
    return ' '.join(translator.translate(c) for c in chunks if c.strip())


class Command(BaseCommand):
    help = '게임 번역 — 설명(무료 Google) + 제목(GMS LLM 음차, --titles). 기본은 설명만.'

    def add_arguments(self, parser):
        parser.add_argument('--titles', action='store_true',
                            help='설명 + 제목까지 번역 (제목은 GMS 과금)')
        parser.add_argument('--titles-only', action='store_true',
                            help='제목만 번역 (GMS 과금)')
        parser.add_argument('--limit', type=int, default=None)
        parser.add_argument('--ids', type=str, default=None,
                            help='특정 game_id 만 (콤마)')
        parser.add_argument('--retranslate', action='store_true',
                            help='이미 번역된 것도 다시')
        parser.add_argument('--sleep', type=float, default=0.4,
                            help='설명 번역 요청 간 대기(초)')
        parser.add_argument('--batch', type=int, default=80,
                            help='제목 GMS 콜당 묶음 수 (콜 수 = 대상/batch)')
        parser.add_argument('--model', type=str, default='gpt-4.1-nano',
                            help='제목 번역 GMS 모델 (기본 nano=1크레딧/콜)')

    def _ids_filter(self, qs, opts):
        if opts['ids']:
            ids = [int(x) for x in opts['ids'].split(',') if x.strip().isdigit()]
            qs = qs.filter(game_id__in=ids)
        return qs

    def handle(self, *args, **opts):
        if not opts['titles_only']:
            self._translate_descriptions(opts)
        if opts['titles'] or opts['titles_only']:
            self._translate_titles(opts)

    # ── 설명: 무료 Google ──────────────────────────────────────────
    def _translate_descriptions(self, opts):
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='en', target='ko')

        qs = Game.objects.exclude(description='').filter(translation_locked=False)
        qs = self._ids_filter(qs, opts).order_by('game_id')
        games = list(qs)
        if not opts['retranslate']:   # 빈 것 + 한글 아닌 것(영어 등) 재번역
            games = [g for g in games if _needs_translation(g.description_ko)]
        if opts['limit']:
            games = games[:opts['limit']]
        self.stdout.write(f'[설명] 대상 {len(games)}개 (무료 Google, 제목 미포함)')

        done = skipped = failed = 0
        for g in games:
            if len((g.description or '').strip()) < MIN_LEN:   # 짧은 텍스트 스킵
                skipped += 1
                continue
            ko = None
            for attempt in range(3):
                try:
                    ko = _google_translate(translator, g.description)
                    break
                except Exception as e:
                    self.stderr.write(self.style.WARNING(
                        f'  ! {g.title[:30]} 시도{attempt + 1}: {e}'))
                    time.sleep(2 * (attempt + 1))
            if ko:
                g.description_ko = ko
                g.save(update_fields=['description_ko'])
                done += 1
            else:
                failed += 1
            time.sleep(opts['sleep'])
        self.stdout.write(self.style.SUCCESS(
            f'[설명] 완료: {done} 번역 · {skipped} 스킵(짧음) · {failed} 실패'))

    # ── 제목: GMS LLM 음차 (⚠️ 과금) ───────────────────────────────
    def _translate_titles(self, opts):
        qs = Game.objects.exclude(title='').filter(translation_locked=False)
        qs = self._ids_filter(qs, opts).order_by('game_id')
        games = list(qs)
        if not opts['retranslate']:   # 빈 것 + 한글 아닌 것(영어 등) 재번역
            games = [g for g in games if _needs_translation(g.title_ko)]
        if opts['limit']:
            games = games[:opts['limit']]

        batch = max(1, opts['batch'])
        calls = (len(games) + batch - 1) // batch
        self.stdout.write(
            f'[제목] 대상 {len(games)}개 → GMS 콜 ~{calls}회 '
            f'(모델 {opts["model"]}, ⚠️ 호출당 과금)')

        done = 0
        for i in range(0, len(games), batch):
            chunk = games[i:i + batch]
            payload = [{'id': g.game_id, 'title': g.title} for g in chunk]
            try:
                data = gms.chat_json(
                    [{'role': 'system', 'content': TITLE_SYSTEM},
                     {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
                    temperature=0.1,
                    model=opts['model'],
                )
                tmap = {t['id']: (t.get('ko') or '').strip()
                        for t in data.get('titles', []) if 'id' in t}
                n = 0
                for g in chunk:
                    ko = tmap.get(g.game_id)
                    if ko:
                        g.title_ko = ko
                        g.save(update_fields=['title_ko'])
                        done += 1
                        n += 1
                self.stdout.write(f'  콜 {i // batch + 1}/{calls}: {n}/{len(chunk)}개')
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'  콜 {i // batch + 1} 실패: {e}'))
        self.stdout.write(self.style.SUCCESS(f'[제목] 완료: {done}개 음차 번역'))
