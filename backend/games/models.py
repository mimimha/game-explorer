# games/models.py
from django.db import models


class Genre(models.Model):
    """
    ERD 기준: PK = tag_id, 컬럼 = genre_name.
    (Game_Tag 조인을 통해 Game 과 M:N)
    """
    tag_id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'genre'

    def __str__(self):
        return self.genre_name


class Game(models.Model):
    game_id = models.AutoField(primary_key=True)

    title = models.CharField(max_length=200)
    # 가격: ERD는 DECIMAL(10,2). 단 '미연동'과 '무료(0)' 구분 위해 nullable.
    initial_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    final_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    capsule_url = models.CharField(max_length=255, blank=True)   # 커버 이미지
    metacritic_score = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    is_korean = models.BooleanField(default=False)
    required_age = models.IntegerField(default=0)
    platform = models.CharField(max_length=100, blank=True)
    offline = models.BooleanField(default=False)

    # 외부 식별자
    rawg_id = models.IntegerField(unique=True, null=True, blank=True)
    steam_id = models.IntegerField(unique=True, null=True, blank=True)

    # 분류: Game_Tag 를 through 로 명시
    genres = models.ManyToManyField(
        Genre, through='GameTag', related_name='games', blank=True
    )

    class Meta:
        db_table = 'game'
        ordering = ['-game_id']

    @property
    def is_price_synced(self):
        """Steam 가격 연동 여부 (steam_id 매칭 + 가격 수집 완료)."""
        return self.steam_id is not None and self.final_price is not None

    def __str__(self):
        return self.title


class GameTag(models.Model):
    """ERD의 Game_Tag — Game ↔ Genre M:N 조인 테이블."""
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, db_column='game_id'
    )
    tag = models.ForeignKey(
        Genre, on_delete=models.CASCADE, db_column='tag_id'
    )

    class Meta:
        db_table = 'game_tag'
        constraints = [
            models.UniqueConstraint(
                fields=['game', 'tag'], name='unique_game_tag'
            ),
        ]

    def __str__(self):
        return f'{self.game.title} - {self.tag.genre_name}'


class Screenshot(models.Model):
    """ERD의 SCREENSHOT — 게임플레이 스크린샷. Game 과 1:N."""
    screenshot_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE,
        related_name='screenshots', db_column='game_id'
    )
    image_url = models.CharField(max_length=255)

    class Meta:
        db_table = 'screenshot'

    def __str__(self):
        return f'{self.game.title} screenshot {self.screenshot_id}'


class GameVideo(models.Model):
    """ERD의 Game_Video — title·video_url·thumbnail 보유. Game 과 1:N."""
    video_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE,
        related_name='videos', db_column='game_id'
    )
    title = models.CharField(max_length=200, blank=True)
    video_url = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'game_video'

    def __str__(self):
        return f'{self.game.title} - {self.title}'