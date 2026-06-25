# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    """AbstractUser 상속 (PK 기본 id 유지 — 인증 라이브러리 호환)."""
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True)
    birth_date = models.DateField()
    profile_img = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # createsuperuser 가 username·password 외에 이 필드들도 입력받게 한다.
    # (DB 컬럼이 아니라 '입력 받을 목록'이라 마이그레이션 불필요 — 기존 DB 그대로)
    # email·nickname·birth_date 가 모두 NOT NULL 이라, 빠지면 IntegrityError 가 난다.
    REQUIRED_FIELDS = ['email', 'nickname', 'birth_date']

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.nickname or self.username

    @property
    def follower_count(self):
        return self.follower_relations.count()

    @property
    def following_count(self):
        return self.following_relations.count()


class Follow(models.Model):
    """ERD Follow(follow_id, follower_id, following_id)."""
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
    ERD Medal(medal_id, medal_name, description, icon_url) — 메달 카탈로그(종류).
    User_Medal 조인을 통해 User 와 M:N.
    """
    medal_id = models.AutoField(primary_key=True)
    medal_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon_url = models.CharField(max_length=255, blank=True)

    holders = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='UserMedal',
        related_name='medals', blank=True,
    )

    class Meta:
        db_table = 'medal'

    def __str__(self):
        return self.medal_name


class UserMedal(models.Model):
    """ERD User_Medal(user_id, medal_id, earned_at) — 획득 기록 조인."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        db_column='user_id', related_name='user_medals',
    )
    medal = models.ForeignKey(
        Medal, on_delete=models.CASCADE,
        db_column='medal_id', related_name='user_medals',
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_medal'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'medal'], name='unique_user_medal'
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.medal}'


class Notification(models.Model):
    class Type(models.TextChoices):
        FOLLOW = 'follow', '팔로우'
        NEW_POST = 'new_post', '새 게시글'
        NEW_WISHLIST = 'new_wishlist', '찜 추가'
        MEDAL = 'medal', '메달 획득'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications', db_column='recipient_id',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='sent_notifications', db_column='actor_id',
        null=True, blank=True,
    )
    notif_type = models.CharField(max_length=20, choices=Type.choices)
    target_id = models.IntegerField(null=True, blank=True)
    target_title = models.CharField(max_length=200, blank=True)
    message = models.CharField(max_length=300)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.notif_type}] → {self.recipient}'