# games/services/rawg.py
"""RAWG API 호출·파싱. (메타데이터 본체 소스)"""
import time
import requests
from django.conf import settings

BASE = settings.RAWG_API_URL          # https://api.rawg.io/api/games
KEY = settings.RAWG_API_KEY


def _get(url, params=None):
    """RAWG GET 공통. key 자동 주입 + 가벼운 에러 처리."""
    params = params or {}
    params['key'] = KEY
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_game_list(page=1, page_size=20, ordering='-added', dates=None):
    """게임 목록 한 페이지. results 배열 반환."""
    params = {'page': page, 'page_size': page_size, 'ordering': ordering}
    if dates:
        params['dates'] = dates       # 예: '2023-01-01,2023-12-31'
    data = _get(BASE, params)
    return data.get('results', [])


def fetch_game_detail(rawg_id):
    """게임 상세 (description, website 등)."""
    return _get(f'{BASE}/{rawg_id}')


def fetch_screenshots(rawg_id):
    """스크린샷 image url 리스트."""
    data = _get(f'{BASE}/{rawg_id}/screenshots')
    return [s['image'] for s in data.get('results', []) if s.get('image')]


def fetch_steam_appid(rawg_id):
    """
    stores 에서 Steam 스토어 URL → appid 추출.
    Steam URL 형식: https://store.steampowered.com/app/{appid}/...
    """
    data = _get(f'{BASE}/{rawg_id}/stores')
    for store in data.get('results', []):
        url = store.get('url', '')
        if 'store.steampowered.com/app/' in url:
            try:
                # .../app/<appid>/... 에서 appid 추출
                part = url.split('/app/')[1]
                appid = part.split('/')[0]
                return int(appid)
            except (IndexError, ValueError):
                continue
    return None


def fetch_movies(rawg_id):
    """RAWG 트레일러 영상 (있으면). [{name, url}] 형태."""
    try:
        data = _get(f'{BASE}/{rawg_id}/movies')
    except requests.HTTPError:
        return []
    movies = []
    for m in data.get('results', []):
        url = (m.get('data') or {}).get('max') or (m.get('data') or {}).get('480')
        if url:
            movies.append({'name': m.get('name', ''), 'url': url})
    return movies


def parse_game_fields(detail):
    """
    RAWG 상세 응답 → Game 모델 필드 dict.
    (genres·platforms 는 별도 처리하므로 여기선 제외)
    """
    released = detail.get('released')   # 'YYYY-MM-DD' or None
    return {
        'rawg_id': detail['id'],
        'title': detail.get('name', '')[:200],
        'capsule_url': detail.get('background_image') or '',
        'description': detail.get('description_raw') or '',  # 일반 텍스트 소개
        'metacritic_score': detail.get('metacritic'),
        'release_date': released or None,
        'required_age': 0,
    }


def extract_genre_names(detail):
    """상세 응답에서 장르 이름 리스트."""
    return [g['name'] for g in detail.get('genres', []) if g.get('name')]


def extract_platform_names(detail):
    """상세 응답에서 플랫폼 이름 리스트. (detail['platforms'][i]['platform']['name'])"""
    names = []
    for p in detail.get('platforms', []) or []:
        plat = p.get('platform') or {}
        name = plat.get('name')
        if name:
            names.append(name)
    return names