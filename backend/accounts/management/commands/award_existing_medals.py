"""
기존 사용자에게 현재 활동 데이터 기준으로 메달 소급 지급.

  python manage.py award_existing_medals
"""
from django.core.management.base import BaseCommand

from accounts.medal_service import award_medal
from accounts.models import User


class Command(BaseCommand):
    help = '기존 유저에게 달성 조건을 충족한 메달을 소급 지급합니다.'

    def handle(self, *args, **options):
        users = User.objects.prefetch_related('user_medals', 'wishlists', 'posts', 'comments')
        total = 0

        for user in users:
            awarded = []

            # 발자국 시작 — 가입한 사람 모두
            if award_medal(user, '발자국 시작'):
                awarded.append('발자국 시작')

            # 첫 번째 발걸음 — 찜 1개 이상
            if user.wishlists.exists():
                if award_medal(user, '첫 번째 발걸음'):
                    awarded.append('첫 번째 발걸음')

            # 수집광 — 찜 10개 이상
            if user.wishlists.count() >= 10:
                if award_medal(user, '수집광'):
                    awarded.append('수집광')

            # 첫 교신 — 게시글 1개 이상
            if user.posts.exists():
                if award_medal(user, '첫 교신'):
                    awarded.append('첫 교신')

            # 댓글 요정 — 댓글 20개 이상
            if user.comments.count() >= 20:
                if award_medal(user, '댓글 요정'):
                    awarded.append('댓글 요정')

            # 탐험대의 일원은 프로필 수정 이력을 알 수 없어 소급 불가

            if awarded:
                total += len(awarded)
                self.stdout.write(f'  {user.nickname}: {", ".join(awarded)}')

        self.stdout.write(self.style.SUCCESS(f'\n총 {total}개 메달 지급 완료'))
