"""
GMS(AI 게이트웨이) 호출 클라이언트.

OpenAI 호환 규격(POST {BASE}/chat/completions, Bearer 인증)을 가정한다.
settings.GMS_MODEL 만 바꾸면 gpt / gemini / claude 모델을 교체할 수 있다.

⚠️ 실제 호출은 settings.RECOMMEND_USE_LLM 이 True 이고 키·BASE_URL 이
   설정돼 있을 때만 services.py 에서 일어난다. (그 전까지 토큰 0)
"""
import json

import requests
from django.conf import settings


class GMSError(Exception):
    """GMS 호출/파싱 관련 오류. services 에서 잡아 랜덤으로 폴백한다."""


def _endpoint():
    base = (settings.GMS_BASE_URL or '').rstrip('/')
    if not base:
        raise GMSError('GMS_BASE_URL 이 설정되지 않았습니다.')
    return f'{base}/chat/completions'


def chat(messages, *, temperature=0.4, json_mode=False, timeout=20):
    """
    OpenAI 호환 chat/completions 호출 → 응답 본문 텍스트(content) 반환.
    messages: [{'role': 'system'|'user'|'assistant', 'content': str}, ...]
    """
    if not settings.GMS_API_KEY:
        raise GMSError('GMS_API_KEY(SSAFY_GMS_KEY) 가 없습니다.')

    payload = {
        'model': settings.GMS_MODEL,
        'messages': messages,
        'temperature': temperature,
    }
    if json_mode:
        # OpenAI 계열에서 JSON 강제. 미지원 모델이면 호출이 실패→상위에서 폴백.
        payload['response_format'] = {'type': 'json_object'}

    try:
        resp = requests.post(
            _endpoint(),
            headers={
                'Authorization': f'Bearer {settings.GMS_API_KEY}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data['choices'][0]['message']['content']
    except (requests.RequestException, KeyError, ValueError) as e:
        raise GMSError(f'GMS 호출 실패: {e}')


def chat_json(messages, **kwargs):
    """chat() 응답을 JSON(dict) 으로 파싱해 반환. 실패 시 GMSError."""
    kwargs.setdefault('json_mode', True)
    raw = chat(messages, **kwargs)
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as e:
        raise GMSError(f'JSON 파싱 실패: {e} / 원문 앞부분: {str(raw)[:200]}')
