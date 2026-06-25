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


def fetch_game_list(page=1, page_size=20, ordering='-added', dates=None, tags=None):
    """게임 목록 한 페이지. results 배열 반환.
    tags: RAWG 태그 슬러그(콤마 구분, 예: 'cute,cozy') — 특정 스타일만 받을 때."""
    params = {'page': page, 'page_size': page_size, 'ordering': ordering}
    if dates:
        params['dates'] = dates       # 예: '2023-01-01,2023-12-31'
    if tags:
        params['tags'] = tags         # 예: 'cute' → 귀여운 스타일 게임만
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
    (genres·platforms·moods 는 별도 처리하므로 여기선 제외)
    """
    released = detail.get('released')   # 'YYYY-MM-DD' or None
    playtime = detail.get('playtime')   # 평균 시간(정수). 0/없음이면 정보 없음.
    return {
        'rawg_id': detail['id'],
        'title': detail.get('name', '')[:200],
        'capsule_url': detail.get('background_image') or '',
        'description': detail.get('description_raw') or '',  # 일반 텍스트 소개
        'metacritic_score': detail.get('metacritic'),
        'release_date': released or None,
        'required_age': 0,
        'playtime': playtime if playtime else None,  # 0 → null(알 수 없음)
    }


# RAWG 영문 태그 → 한국어 무드 라벨 (분위기/무드 화이트리스트).
# 장르성 태그(RPG, Open World 등)는 제외하고 '분위기'에 해당하는 것만 큐레이션.
MOOD_TAG_MAP = {
    'Atmospheric': '분위기 있는',
    'Great Soundtrack': '음악이 좋은',
    'Story Rich': '스토리 중심',
    'Funny': '유쾌한',
    'Comedy': '코미디',
    'Relaxing': '편안한',
    'Cozy': '아늑한',
    'Dark': '어두운',
    'Dark Fantasy': '다크 판타지',
    'Horror': '공포',
    'Psychological Horror': '심리 공포',
    'Tense': '긴장감 있는',
    'Emotional': '감성적인',
    'Sad': '슬픈',
    'Cute': '귀여운',
    'Beautiful': '아름다운',
    'Colorful': '화사한',
    'Epic': '웅장한',
    'Mystery': '미스터리',
    'Surreal': '초현실적인',
    'Minimalist': '미니멀',
    'Retro': '레트로',
    'Violent': '폭력적인',
    # 실데이터 전수 집계로 추가한 무드 (빈도순)
    'Gore': '잔혹한',
    'Cinematic': '영화 같은',
    'Difficult': '어려운',
    'Post-apocalyptic': '종말 이후',
    'Dystopian': '디스토피아',
    'Survival Horror': '생존 공포',
    'Futuristic': '미래적인',
    'Pixel Graphics': '픽셀 그래픽',   # 픽셀/도트 스타일
    # 전체 태그 전수 분류로 일괄 추가 — 세팅/테마
    'Sci-fi': 'SF',
    'Fantasy': '판타지',
    'Cyberpunk': '사이버펑크',
    'Steampunk': '스팀펑크',
    'Space': '우주',
    'Medieval': '중세',
    'Historical': '역사',
    'War': '전쟁',
    'Military': '밀리터리',
    'Western': '서부극',
    'Gothic': '고딕',
    'Noir': '누아르',
    'Mythology': '신화',
    'Supernatural': '초자연',
    'Lovecraftian': '러브크래프트풍',
    'Zombies': '좀비',
    'Aliens': '외계인',
    'Robots': '로봇',
    'Dinosaurs': '공룡',
    'Dragons': '용',
    'Ninja': '닌자',
    'Pirates': '해적',
    'Superhero': '슈퍼히어로',
    'Crime': '범죄',
    'Detective': '탐정',
    'Conspiracy': '음모',
    'Political': '정치',
    'Time Travel': '시간여행',
    'Underwater': '수중',
    'Alternate History': '대체역사',
    'Cold War': '냉전',
    # 미감(비주얼)
    '2D': '2D 그래픽',
    'Hand-drawn': '손그림',
    'Anime': '애니메이션풍',
    'Cartoony': '만화풍',
    'Cartoon': '만화풍',
    'Realistic': '사실적',
    'Photorealistic': '사실적',
    'Psychedelic': '사이키델릭',
    'Abstract': '추상적',
    'Comic Book': '코믹북풍',
    # 톤/감성
    'Dark Humor': '블랙코미디',
    'Memes': '밈',
    'Satire': '풍자',
    'Drama': '드라마',
    'Romance': '로맨스',
    'Thriller': '스릴러',
    'Psychological': '심리적',
    'Masterpiece': '명작',
    'Family Friendly': '가족친화',
    'Fast-Paced': '빠른 전개',
    'Lore-Rich': '풍부한 세계관',
}

# 플레이 인원/모드 판정용 RAWG 태그 (소문자 비교).
_RAWG_SINGLE = {'singleplayer', 'single player'}
_RAWG_MULTI = {
    'multiplayer', 'online multiplayer', 'local multiplayer',
    'massively multiplayer', 'pvp', 'online pvp', 'cross-platform multiplayer',
}
_RAWG_COOP = {
    'co-op', 'online co-op', 'local co-op', 'co-op campaign',
    'split screen', 'online co-op', 'local co-op campaign',
}


def _eng_tag_names(detail):
    """RAWG 상세에서 영문 태그 이름 리스트."""
    return [
        t['name'] for t in (detail.get('tags') or [])
        if t.get('name') and t.get('language') == 'eng'
    ]


def extract_mood_names(detail):
    """RAWG 태그 중 무드 화이트리스트에 매칭되는 한국어 라벨 리스트(중복 제거)."""
    names = []
    for tag in _eng_tag_names(detail):
        label = MOOD_TAG_MAP.get(tag)
        if label and label not in names:
            names.append(label)
    return names


def extract_player_modes(detail):
    """
    RAWG 태그에서 플레이 인원/모드 추출.
    반환: {'single', 'multi', 'coop'} (각 bool) 또는 None(판정 근거 태그가 전혀 없음).
    """
    tags = {t.lower() for t in _eng_tag_names(detail)}
    single = bool(tags & _RAWG_SINGLE)
    multi = bool(tags & _RAWG_MULTI)
    coop = bool(tags & _RAWG_COOP)
    if not (single or multi or coop):
        return None      # RAWG 근거 없음 → Steam 폴백에 맡김
    return {'single': single, 'multi': multi, 'coop': coop}


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