"""Steam appdetails 호출 → 가격 + 플레이 인원/모드 추출. (가격·인원 보강 소스)"""
import requests
from django.conf import settings

DETAIL_URL = settings.STEAM_APP_DETAIL_URL  # https://store.steampowered.com/api/appdetails

# Steam categories(영문) → 플레이 모드 판정 (소문자 비교).
_STEAM_SINGLE = {'single-player'}
_STEAM_MULTI = {
    'multi-player', 'pvp', 'online pvp', 'shared/split screen pvp',
    'cross-platform multiplayer', 'mmo',
}
_STEAM_COOP = {
    'co-op', 'online co-op', 'lan co-op', 'shared/split screen co-op',
}


def _modes_from_categories(cats):
    """Steam categories 리스트 → {'single','multi','coop'} 또는 None(근거 없음)."""
    names = {c.get('description', '').lower() for c in (cats or [])}
    single = bool(names & _STEAM_SINGLE)
    multi = bool(names & _STEAM_MULTI)
    coop = bool(names & _STEAM_COOP)
    if not (single or multi or coop):
        return None
    return {'single': single, 'multi': multi, 'coop': coop}


def fetch_app_details(appid):
    """
    Steam appid → 가격 + 인원 dict.
    반환: {'initial_price', 'final_price', 'is_korean', 'modes'}
      - modes: {'single','multi','coop'} 또는 None
    실패 시 {} (모두 알 수 없음).
    영문 locale(l='english')로 받아 categories 매칭을 안정화한다.
    """
    params = {
        'appids': appid,
        'cc': 'kr',                 # 한국 가격(원) — 통화는 cc 로 결정
        'l': 'english',             # categories/언어명을 영문으로 → 안정적 매칭
        'filters': 'price_overview,supported_languages,categories',
    }
    try:
        resp = requests.get(DETAIL_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return {}

    app = data.get(str(appid), {})
    if not app.get('success'):
        return {}

    info = app.get('data', {})
    result = {}

    # 가격 (price_overview 없으면 무료이거나 미정)
    price = info.get('price_overview')
    if price:
        # Steam은 최소 화폐단위(원*100)로 줌 → 100 나눠 원 단위로
        result['initial_price'] = price.get('initial', 0) / 100
        result['final_price'] = price.get('final', 0) / 100
    else:
        # price_overview 없음 = 무료 게임으로 간주
        result['initial_price'] = 0
        result['final_price'] = 0

    # 한국어 지원 (supported_languages 문자열에 'Korean' 포함 여부)
    langs = info.get('supported_languages', '') or ''
    result['is_korean'] = 'Korean' in langs

    # 플레이 인원/모드
    result['modes'] = _modes_from_categories(info.get('categories'))

    return result


# 하위호환: 가격 필드만 필요할 때.
def fetch_price(appid):
    d = fetch_app_details(appid)
    return {k: d[k] for k in ('initial_price', 'final_price', 'is_korean') if k in d}
