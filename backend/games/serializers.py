from rest_framework import serializers
from .models import Game, Genre, Platform, Screenshot, GameVideo


class GenreSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag_id', read_only=True)
    name = serializers.CharField(source='genre_name', read_only=True)

    class Meta:
        model = Genre
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
        fields = ['id', 'title', 'video_url', 'thumbnail']


class GameCardSerializer(serializers.ModelSerializer):
    """목록·홈용 카드."""
    id = serializers.IntegerField(source='game_id', read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'capsule_url',
            'initial_price', 'final_price',
            'is_korean', 'genres', 'platforms',
        ]


class GameDetailSerializer(serializers.ModelSerializer):
    """상세용."""
    id = serializers.IntegerField(source='game_id', read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)
    screenshots = ScreenshotSerializer(many=True, read_only=True)
    videos = GameVideoSerializer(many=True, read_only=True)
    is_wishlisted = serializers.SerializerMethodField()
    is_price_synced = serializers.BooleanField(read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'capsule_url',
            'initial_price', 'final_price', 'is_price_synced',
            'metacritic_score', 'release_date',
            'is_korean', 'required_age', 'offline',
            'rawg_id', 'steam_id',
            'is_wishlisted', 'genres', 'platforms', 'screenshots', 'videos',
        ]

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        mgr = getattr(obj, 'wishlisted_by', None)
        if mgr is None:
            return False
        return mgr.filter(user=request.user).exists()