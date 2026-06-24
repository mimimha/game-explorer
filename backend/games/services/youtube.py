"""YouTube Data API 검색 → 게임 영상 추출. (스트리밍 영상 소스)

키 여러 개를 지원한다(settings.YOUTUBE_DATA_API_KEYS). 한 키가 일일 쿼터를
소진하면(403 quotaExceeded / 429) 자동으로 다음 키로 넘어간다.
"""
import html
import requests
from django.conf import settings

SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

# 사용할 키 목록 + 현재 키 인덱스(소진된 키는 건너뜀). 프로세스 단위로 유지.
_KEYS = list(getattr(settings, 'YOUTUBE_DATA_API_KEYS', None)
             or ([settings.YOUTUBE_DATA_API_KEY] if settings.YOUTUBE_DATA_API_KEY else []))
_idx = 0


def _is_quota_error(resp):
    """쿼터/한도 소진 응답인지 판별 (403 quotaExceeded 또는 429)."""
    if resp.status_code == 429:
        return True
    if resp.status_code == 403:
        try:
            reasons = [e.get('reason') for e in
                       resp.json().get('error', {}).get('errors', [])]
        except ValueError:
            return True
        return any(r in ('quotaExceeded', 'dailyLimitExceeded', 'rateLimitExceeded')
                   for r in reasons)
    return False


def search_videos(game_title, query_terms='gameplay trailer',
                  max_results=3, video_duration=None):
    """
    게임 제목으로 YouTube 검색 → 영상 리스트.
    - query_terms: 제목 뒤에 붙일 검색어 (트레일러 'gameplay trailer',
      공략 '공략 walkthrough' 등)
    - video_duration: None | 'short'(<4분) | 'medium'(4~20분) | 'long'(20분+)
    반환: [{'title','video_url','thumbnail','channel','published_at'}]
    키가 모두 소진되면 [] 반환.
    """
    global _idx
    if not _KEYS:
        return []

    params = {
        'q': f'{game_title} {query_terms}',
        'part': 'snippet',
        'type': 'video',
        'maxResults': max_results,
        'order': 'relevance',
    }
    if video_duration:
        params['videoDuration'] = video_duration

    # 현재 키부터 시도, 소진되면 다음 키로 전환
    while _idx < len(_KEYS):
        try:
            resp = requests.get(
                SEARCH_URL, params={**params, 'key': _KEYS[_idx]}, timeout=15,
            )
        except requests.RequestException:
            return []

        if _is_quota_error(resp):
            _idx += 1   # 이 키는 소진 → 다음 키로
            continue
        try:
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            return []
        return _parse(data)

    return []   # 모든 키 소진


def _parse(data):
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
