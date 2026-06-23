# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    """
    AbstractUser 상속 (PK는 기본 id 유지 — 인증 라이브러리 호환).
    ERD User 의 추가 필드만 얹는다.
    """
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_img = models.CharField(max_length=255, blank=True)  # ERD: VARCHAR(255)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.nickname or self.username

    @property
    def follower_count(self):
        # 나를 팔로우하는 관계 수
        return self.follower_relations.count()

    @property
    def following_count(self):
        # 내가 팔로우하는 관계 수
        return self.following_relations.count()


class Follow(models.Model):
    """ERD Follow(follow_id, follower_id, following_id). 방향 있는 관계."""
    follow_id = models.AutoField(primary_key=True)
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='following_relations', db_column='follower_id',
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='follower_relations', db_column='following_id',
    )

    class Meta:
        db_table = 'follow'
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'], name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='prevent_self_follow',
            ),
        ]

    def __str__(self):
        return f'{self.follower} → {self.following}'


class Medal(models.Model):
    """
    ERD Medal(medal_id, user_id, medal_name) — 단일 테이블.
    유저가 메달을 획득하면 이 테이블에 행이 하나 생긴다.
    """
    medal_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='medals', db_column='user_id',
    )
    medal_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'medal'

    def __str__(self):
        return f'{self.user} - {self.medal_name}'