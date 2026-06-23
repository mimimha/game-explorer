"""Steam appdetails 호출 → 가격(price_overview)만 추출. (가격 보강 소스)"""
import requests
from django.conf import settings

DETAIL_URL = settings.STEAM_APP_DETAIL_URL  # https://store.steampowered.com/api/appdetails


def fetch_price(appid):
    """
    Steam appid → 가격 dict 반환.
    실패하거나 무료/가격없음이면 부분 dict.
    반환: {'initial_price', 'final_price', 'is_korean', 'offline'}
    """
    params = {
        'appids': appid,
        'cc': 'kr',                 # 한국 가격(원)
        'l': 'korean',              # 한국어 설명
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

    # 오프라인(싱글플레이) 여부 — categories 에 single-player 있으면
    cats = info.get('categories', []) or []
    result['offline'] = any(
        c.get('description', '').lower().startswith('single')
        for c in cats
    )

    return result