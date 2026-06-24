# accounts/medal_service.py
"""메달 수여 유틸리티. 각 뷰/시리얼라이저에서 조건 충족 시 호출한다."""

NON_MASTER_MEDALS = [
    '발자국 시작',
    '첫 번째 발걸음',
    '탐험대의 일원',
    '첫 교신',
    '수집광',
    '댓글 요정',
]
MASTER_MEDAL = '전설의 탐험가'


def award_medal(user, medal_name: str) -> bool:
    """
    user 에게 medal_name 메달을 수여한다.
    이미 보유 중이거나 Medal 카탈로그에 없으면 조용히 무시한다.
    수여가 새로 일어났으면 True 반환 후 마스터 메달 조건도 확인한다.
    """
    from .models import Medal, UserMedal

    try:
        medal = Medal.objects.get(medal_name=medal_name)
    except Medal.DoesNotExist:
        return False

    _, created = UserMedal.objects.get_or_create(user=user, medal=medal)
    if created:
        _check_master_medal(user)
    return created


def _check_master_medal(user) -> None:
    """비마스터 메달 6개 모두 획득 시 마스터 메달 수여."""
    from .models import Medal, UserMedal

    earned_count = user.user_medals.filter(
        medal__medal_name__in=NON_MASTER_MEDALS
    ).count()
    if earned_count >= len(NON_MASTER_MEDALS):
        try:
            master = Medal.objects.get(medal_name=MASTER_MEDAL)
        except Medal.DoesNotExist:
            return
        UserMedal.objects.get_or_create(user=user, medal=master)
