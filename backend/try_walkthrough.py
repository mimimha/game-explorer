"""
공략 영상 검색어 실험용 (임시 스크립트 — DB/모델 변경 없음).

실행:
  cd backend
  python try_walkthrough.py                # DB에서 게임 3개 자동 선택
  python try_walkthrough.py "Elden Ring"   # 특정 게임 제목 지정

여러 검색어 변형의 결과를 나란히 출력해 어떤 쿼리가 좋은지 눈으로 비교한다.
결과가 마음에 들면 그때 youtube.py/모델/load_games 에 반영한다.
"""
import os
import sys
import html
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from django.conf import settings

SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
KEY = settings.YOUTUBE_DATA_API_KEY

# 비교할 검색어 변형: (라벨, q 접미사, videoDuration)
#   videoDuration: None | 'short'(<4분) | 'medium'(4~20분) | 'long'(>20분)
VARIANTS = [
    ('① 공략+walkthrough (길이무관)', '공략 walkthrough', None),
    ('② 공략+walkthrough (long 20분+)', '공략 walkthrough', 'long'),
    ('③ walkthrough guide (영어, long)', 'walkthrough guide', 'long'),
    ('④ 공략 (한국어만)', '공략', None),
]


def search(title, q_suffix, duration, max_results=5):
    if not KEY:
        print('!! YOUTUBE_DATA_API_KEY 가 설정되지 않음 (.env 확인)')
        return []
    params = {
        'key': KEY,
        'q': f'{title} {q_suffix}',
        'part': 'snippet',
        'type': 'video',
        'maxResults': max_results,
        'order': 'relevance',
    }
    if duration:
        params['videoDuration'] = duration
    try:
        resp = requests.get(SEARCH_URL, params=params, timeout=15)
        resp.raise_for_status()
        items = resp.json().get('items', [])
    except (requests.RequestException, ValueError) as e:
        print(f'   (검색 실패: {e})')
        return []
    out = []
    for it in items:
        vid = (it.get('id') or {}).get('videoId')
        sn = it.get('snippet', {})
        if not vid:
            continue
        out.append({
            'title': html.unescape(sn.get('title', '')),
            'channel': html.unescape(sn.get('channelTitle', '')),
            'url': f'https://youtu.be/{vid}',
        })
    return out


def pick_titles():
    if len(sys.argv) > 1:
        return [sys.argv[1]]
    from games.models import Game
    return list(Game.objects.values_list('title', flat=True)[:3])


def main():
    titles = pick_titles()
    for title in titles:
        print('\n' + '=' * 70)
        print(f'게임: {title}')
        print('=' * 70)
        for label, q_suffix, duration in VARIANTS:
            print(f'\n  [{label}]  q="{title} {q_suffix}"')
            rows = search(title, q_suffix, duration)
            if not rows:
                print('     (결과 없음)')
            for r in rows:
                print(f"     - {r['title'][:55]:55}  | {r['channel'][:18]:18} | {r['url']}")


if __name__ == '__main__':
    main()
