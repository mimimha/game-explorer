"""YouTube Data API 검색 → 게임 영상 추출. (스트리밍 영상 소스)"""
import html
import requests
from django.conf import settings

SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
KEY = settings.YOUTUBE_DATA_API_KEY


def search_videos(game_title, query_terms='gameplay trailer',
                  max_results=3, video_duration=None):
    """
    게임 제목으로 YouTube 검색 → 영상 리스트.
    - query_terms: 제목 뒤에 붙일 검색어 (트레일러용 'gameplay trailer',
      공략용 '공략 walkthrough' 등)
    - video_duration: None | 'short'(<4분) | 'medium'(4~20분) | 'long'(20분+)
      공략은 길어서 'long' 으로 거르면 트레일러/쇼츠가 자연히 배제됨.
    반환: [{'title', 'video_url', 'thumbnail', 'channel', 'published_at'}]
    """
    if not KEY:
        return []

    params = {
        'key': KEY,
        'q': f'{game_title} {query_terms}',
        'part': 'snippet',
        'type': 'video',
        'maxResults': max_results,
        'order': 'relevance',
    }
    if video_duration:
        params['videoDuration'] = video_duration
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