"""YouTube Data API 검색 → 게임 영상 추출. (스트리밍 영상 소스)"""
import html
import requests
from django.conf import settings

SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
KEY = settings.YOUTUBE_DATA_API_KEY


def search_videos(game_title, max_results=3):
    """
    게임 제목으로 YouTube 검색 → 영상 리스트.
    반환: [{'title', 'video_url', 'thumbnail'}]
    """
    if not KEY:
        return []

    params = {
        'key': KEY,
        'q': f'{game_title} gameplay trailer',
        'part': 'snippet',
        'type': 'video',
        'maxResults': max_results,
        'order': 'relevance',
    }
    try:
        resp = requests.get(SEARCH_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    videos = []
    for item in data.get('items', []):
        vid = (item.get('id') or {}).get('videoId')
        snippet = item.get('snippet', {})
        if not vid:
            continue
        thumbs = snippet.get('thumbnails', {})
        thumb = (thumbs.get('high') or thumbs.get('default') or {}).get('url', '')
        videos.append({
            # YouTube 제목은 HTML escape 되어 옴(&quot; 등) → 디코드
            'title': html.unescape(snippet.get('title', ''))[:200],
            'video_url': f'https://www.youtube.com/watch?v={vid}',
            'thumbnail': thumb,
            'channel': html.unescape(snippet.get('channelTitle', ''))[:100],
            'published_at': (snippet.get('publishedAt') or '')[:10],  # YYYY-MM-DD
        })
    return videos