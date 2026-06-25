"""YouTube Data API 검색 → 게임 영상 추출. (스트리밍 영상 소스)

키 여러 개를 지원한다(settings.YOUTUBE_DATA_API_KEYS). 한 키가 일일 쿼터를
소진하면(403 quotaExceeded / 429) 자동으로 다음 키로 넘어간다.
"""
import html
import re
import requests
from django.conf import settings

SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

# 제목에 한글이 있으면 "한국 제작 영상"으로 본다(완벽하진 않지만 실용적 판별).
_HANGUL = re.compile(r'[가-힣]')

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
                  max_results=3, video_duration=None,
                  order='relevance', region_code=None, relevance_language=None):
    """
    게임 제목으로 YouTube 검색 → 영상 리스트.
    - query_terms: 제목 뒤에 붙일 검색어 (트레일러 'gameplay trailer',
      공략 '공략 walkthrough' 등)
    - video_duration: None | 'short'(<4분) | 'medium'(4~20분) | 'long'(20분+)
    - order: 'relevance'(기본) | 'viewCount'(조회수순) | 'date' 등
    - region_code: 'KR' 등 ISO 국가코드(검색 결과를 해당 지역 기준으로 편향)
    - relevance_language: 'ko' 등 ISO 언어코드(해당 언어 영상 우선)
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
        'order': order,
    }
    if video_duration:
        params['videoDuration'] = video_duration
    if region_code:
        params['regionCode'] = region_code
    if relevance_language:
        params['relevanceLanguage'] = relevance_language

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


def _name_match(video_title, *names):
    """영상 제목에 게임명(공백/대소문자 무시)이 들어있는지 — 엉뚱한 게임 영상 배제용."""
    vt = video_title.replace(' ', '').lower()
    return any(n and n.replace(' ', '').lower() in vt for n in names if n)


def _take(out, seen, candidates, n):
    """candidates(조회수순)에서 중복 제외하고 out 에 n 개까지 채운다."""
    for v in candidates:
        if v['video_url'] not in seen:
            out.append(v)
            seen.add(v['video_url'])
            if len(out) >= n:
                return True
    return False


def search_walkthroughs(title, title_ko=None, n=3):
    """
    공략(스트리밍/게임플레이) 영상 n개를 추출한다.
    우선순위: ① 한국 제작(제목에 한글) 영상을 조회수 높은 순으로,
             ② 부족하면 그 뒤에 해외(영어권 등) 영상을 조회수순으로 채운다.
    각 단계에서 게임명이 제목에 들어간 영상을 먼저(조회수순 유지) → 엉뚱한 게임 배제.
    검색 횟수: 한국 1회 (+부족 시 해외 1회) = 게임당 1~2회.
    """
    out, seen = [], set()

    # ① 한국 영상: '영문 제목'으로 KR/ko + 조회수순 검색 → 한글 제목만
    #    (한글 음차로 검색하면 흔한 단어와 충돌. 예: GRIS의 "그리스"로 검색하면
    #     게임이 아니라 국가 Greece 영상이 잡힘 → 영문 제목으로 검색해 풀을 깨끗하게)
    kr = [v for v in search_videos(
        title, query_terms='공략 게임플레이',
        max_results=n + 6, video_duration='long',
        order='viewCount', region_code='KR', relevance_language='ko',
    ) if _HANGUL.search(v['title'])]
    # 게임명 매칭되는 한국 영상 먼저(조회수순), 그다음 나머지 한국 영상
    kr_named = [v for v in kr if _name_match(v['title'], title_ko, title)]
    if not _take(out, seen, kr_named, n):
        _take(out, seen, kr, n)

    # ② 부족분: 해외 영상(영문 제목 검색) 조회수순으로 채움 (게임명 매칭 우선)
    if len(out) < n:
        intl = search_videos(
            title, query_terms='walkthrough gameplay',
            max_results=n + 6, video_duration='long', order='viewCount',
        )
        intl_named = [v for v in intl if _name_match(v['title'], title)]
        if not _take(out, seen, intl_named, n):
            _take(out, seen, intl, n)

    return out[:n]


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
