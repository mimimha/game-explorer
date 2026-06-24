# games/models.py
from django.db import models


class Genre(models.Model):
    """ERD Genre(tag_id, genre_name) — Game_Tag 조인으로 Game 과 M:N."""
    tag_id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'genre'

    def __str__(self):
        return self.genre_name


class Platform(models.Model):
    """ERD Platform(platform_id, platform_name) — Game_Platform 조인으로 Game 과 M:N."""
    platform_id = models.AutoField(primary_key=True)
    platform_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'platform'

    def __str__(self):
        return self.platform_name


class Mood(models.Model):
    """분위기/무드 — Game_Mood 조인으로 Game 과 M:N. (RAWG 태그 화이트리스트에서 적재)"""
    mood_id = models.AutoField(primary_key=True)
    mood_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'mood'

    def __str__(self):
        return self.mood_name


class Game(models.Model):
    game_id = models.AutoField(primary_key=True)

    title = models.CharField(max_length=200)
    initial_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    final_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    capsule_url = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, default='')  # RAWG description_raw
    metacritic_score = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    is_korean = models.BooleanField(default=False)
    required_age = models.IntegerField(default=0)
    offline = models.BooleanField(default=False)

    # 평균 플레이타임(시간) — RAWG playtime. 정보 없으면 null.
    playtime = models.IntegerField(null=True, blank=True)

    # 플레이 인원/모드 — RAWG tags 우선, 없으면 Steam categories 폴백.
    # 둘 다 정보가 없으면 null (= 알 수 없음, False 와 구분).
    is_singleplayer = models.BooleanField(null=True, blank=True, default=None)
    is_multiplayer = models.BooleanField(null=True, blank=True, default=None)
    is_coop = models.BooleanField(null=True, blank=True, default=None)

    # 외부 식별자
    rawg_id = models.IntegerField(unique=True, null=True, blank=True)
    steam_id = models.IntegerField(unique=True, null=True, blank=True)

    # 분류: 각각 through 조인
    genres = models.ManyToManyField(
        Genre, through='GameTag', related_name='games', blank=True
    )
    platforms = models.ManyToManyField(
        Platform, through='GamePlatform', related_name='games', blank=True
    )
    moods = models.ManyToManyField(
        Mood, through='GameMood', related_name='games', blank=True
    )

    class Meta:
        db_table = 'game'
        ordering = ['-game_id']

    @property
    def is_price_synced(self):
        return self.steam_id is not None and self.final_price is not None

    def __str__(self):
        return self.title


class GameTag(models.Model):
    """ERD Game_Tag — Game ↔ Genre M:N 조인."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, db_column='game_id')
    tag = models.ForeignKey(Genre, on_delete=models.CASCADE, db_column='tag_id')

    class Meta:
        db_table = 'game_tag'
        constraints = [
            models.UniqueConstraint(fields=['game', 'tag'], name='unique_game_tag'),
        ]

    def __str__(self):
        return f'{self.game.title} - {self.tag.genre_name}'


class GamePlatform(models.Model):
    """ERD Game_Platform — Game ↔ Platform M:N 조인."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, db_column='game_id')
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, db_column='platform_id'
    )

    class Meta:
        db_table = 'game_platform'
        constraints = [
            models.UniqueConstraint(
                fields=['game', 'platform'], name='unique_game_platform'
            ),
        ]

    def __str__(self):
        return f'{self.game.title} - {self.platform.platform_name}'


class GameMood(models.Model):
    """Game ↔ Mood M:N 조인."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, db_column='game_id')
    mood = models.ForeignKey(Mood, on_delete=models.CASCADE, db_column='mood_id')

    class Meta:
        db_table = 'game_mood'
        constraints = [
            models.UniqueConstraint(fields=['game', 'mood'], name='unique_game_mood'),
        ]

    def __str__(self):
        return f'{self.game.title} - {self.mood.mood_name}'


class Screenshot(models.Model):
    """ERD Screenshot — Game 과 1:N."""
    screenshot_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE,
        related_name='screenshots', db_column='game_id',
    )
    image_url = models.CharField(max_length=255)

    class Meta:
        db_table = 'screenshot'

    def __str__(self):
        return f'{self.game.title} screenshot {self.screenshot_id}'


class GameVideo(models.Model):
    """ERD Game_Video — Game 과 1:N."""
    video_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE,
        related_name='videos', db_column='game_id',
    )
    title = models.CharField(max_length=200, blank=True)
    video_url = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255, blank=True)
    channel = models.CharField(max_length=100, blank=True, default='')      # 업로드 채널명
    published_at = models.CharField(max_length=10, blank=True, default='')  # YYYY-MM-DD
    # 영상 종류: 트레일러 / 공략(스트리밍). 상세 페이지에서 구분 표시.
    TRAILER = 'trailer'
    WALKTHROUGH = 'walkthrough'
    VIDEO_TYPE_CHOICES = [
        (TRAILER, '트레일러'),
        (WALKTHROUGH, '공략'),
    ]
    video_type = models.CharField(
        max_length=20, choices=VIDEO_TYPE_CHOICES, default=TRAILER,
    )

    class Meta:
        db_table = 'game_video'

    def __str__(self):
        return f'{self.game.title} - {self.title}'