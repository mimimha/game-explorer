from rest_framework import serializers
from .models import Game, Genre, Platform, Mood, Screenshot, GameVideo


class GenreSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag_id', read_only=True)
    name = serializers.CharField(source='genre_name', read_only=True)

    class Meta:
        model = Genre
        fields = ['id', 'name']


class MoodSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='mood_id', read_only=True)
    name = serializers.CharField(source='mood_name', read_only=True)

    class Meta:
        model = Mood
        fields = ['id', 'name']


class PlatformSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='platform_id', read_only=True)
    name = serializers.CharField(source='platform_name', read_only=True)

    class Meta:
        model = Platform
        fields = ['id', 'name']


class ScreenshotSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='screenshot_id', read_only=True)

    class Meta:
        model = Screenshot
        fields = ['id', 'image_url']


class GameVideoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='video_id', read_only=True)

    class Meta:
        model = GameVideo
        fields = ['id', 'video_type', 'title', 'video_url', 'thumbnail', 'channel', 'published_at']


class GameCardSerializer(serializers.ModelSerializer):
    """목록·홈용 카드."""
    id = serializers.IntegerField(source='game_id', read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)
    moods = MoodSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'title_ko', 'capsule_url',
            'initial_price', 'final_price',
            'metacritic_score', 'release_date',
            'is_korean', 'playtime',
            'is_singleplayer', 'is_multiplayer', 'is_coop',
            'genres', 'platforms', 'moods',
        ]


class GameDetailSerializer(serializers.ModelSerializer):
    """상세용."""
    id = serializers.IntegerField(source='game_id', read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)
    moods = MoodSerializer(many=True, read_only=True)
    screenshots = ScreenshotSerializer(many=True, read_only=True)
    videos = GameVideoSerializer(many=True, read_only=True)
    is_wishlisted = serializers.SerializerMethodField()
    is_price_synced = serializers.BooleanField(read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'title_ko', 'capsule_url',
            'description', 'description_ko',
            'initial_price', 'final_price', 'is_price_synced',
            'metacritic_score', 'release_date',
            'is_korean', 'required_age', 'offline', 'playtime',
            'is_singleplayer', 'is_multiplayer', 'is_coop',
            'rawg_id', 'steam_id',
            'is_wishlisted', 'genres', 'platforms', 'moods',
            'screenshots', 'videos',
        ]

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        mgr = getattr(obj, 'wishlisted_by', None)
        if mgr is None:
            return False
        return mgr.filter(user=request.user).exists()