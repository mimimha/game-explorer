"""표지(썸네일) 이미지 → 주요 시각 소재 태그. 비전 모델은 settings.GMS_VISION_MODEL(.env)."""
from django.conf import settings

from recommendations import gms

# 허용 소재 어휘 (검색·추천에 쓰일 한국어 태그). 목록 밖 응답은 버린다.
SUBJECT_VOCAB = [
    '동물', '사람', '괴물', '로봇', '메카', '무기', '차량', '풍경',
    '도시', '건물', '우주', '바다', '판타지 생물', '캐릭터', '음식', '식물',
]

SYSTEM = (
    '너는 게임 표지 이미지를 보고 주요 시각 소재를 분류하는 분석기다. '
    'JSON 으로만 답한다.'
)


def analyze_subjects(image_url, timeout=30):
    """표지 URL → 시각 소재 태그 리스트(어휘 내). 실패/없음이면 []."""
    if not image_url:
        return []
    user_content = [
        {'type': 'text', 'text': (
            '이 게임 표지에 뚜렷하게 보이는 주요 소재를 아래 목록에서만 골라 '
            'JSON 으로 답해. 해당 없으면 빈 배열. '
            '형식: {"subjects": ["동물", "풍경"]}. '
            f'목록: {", ".join(SUBJECT_VOCAB)}'
        )},
        {'type': 'image_url', 'image_url': {'url': image_url}},
    ]
    try:
        data = gms.chat_json(
            [{'role': 'system', 'content': SYSTEM},
             {'role': 'user', 'content': user_content}],
            temperature=0.0, timeout=timeout,
            model=settings.GMS_VISION_MODEL,   # 비전 전용 모델(.env)
        )
    except gms.GMSError:
        return []
    subjects = data.get('subjects') or []
    # 어휘 화이트리스트로 정제 (중복 제거, 순서 유지)
    seen, out = set(), []
    for s in subjects:
        if s in SUBJECT_VOCAB and s not in seen:
            seen.add(s)
            out.append(s)
    return out
