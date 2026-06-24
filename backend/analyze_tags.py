"""
보유 게임 전체의 RAWG 태그를 전수 집계 → 빈도순 출력 + 무드 화이트리스트 매칭 현황.
(임시 분석용. DB 변경 없음. RAWG 무료 호출.)

실행:  cd backend && python analyze_tags.py
"""
import os, time, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from collections import Counter
from games.models import Game
from games.services import rawg
from games.services.rawg import MOOD_TAG_MAP

games = list(Game.objects.exclude(rawg_id__isnull=True).order_by('game_id'))
print(f'대상 게임: {len(games)}개\n태그 수집 중...')

counter = Counter()
fail = 0
for i, g in enumerate(games, 1):
    try:
        detail = rawg.fetch_game_detail(g.rawg_id)
        for name in rawg._eng_tag_names(detail):
            counter[name] += 1
    except Exception as e:
        fail += 1
    if i % 20 == 0:
        print(f'  {i}/{len(games)}')
    time.sleep(0.2)

print(f'\n수집 완료 (실패 {fail}개). 고유 태그 {len(counter)}종.\n')

in_map = set(MOOD_TAG_MAP.keys())

print('=' * 60)
print('[A] 이미 무드 화이트리스트에 있는 태그 (빈도)')
print('=' * 60)
for name, c in counter.most_common():
    if name in in_map:
        print(f'  {c:3}  {name:30} → {MOOD_TAG_MAP[name]}')

print('\n' + '=' * 60)
print('[B] 화이트리스트에 없는 태그 — 빈도 상위 50 (무드 후보 검토용)')
print('=' * 60)
shown = 0
for name, c in counter.most_common():
    if name not in in_map:
        print(f'  {c:3}  {name}')
        shown += 1
        if shown >= 50:
            break

# 화이트리스트에 있는데 실제로 한 번도 안 나온 것
unused = [k for k in in_map if k not in counter]
print('\n' + '=' * 60)
print(f'[C] 화이트리스트에 있으나 실데이터에 없는 태그 ({len(unused)}개)')
print('=' * 60)
print('  ', ', '.join(sorted(unused)) or '(없음)')
