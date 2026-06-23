# games/serializers.py
from rest_framework import serializers
from .models import Game, Genre, Screenshot, GameVideo


class GenreSerializer(serializers.ModelSerializer):
    # ERD: PK=tag_id, 컬럼=genre_name. 프론트 호환 위해 id/name 으로도 노출.
    id = serializers.IntegerField(source='tag_id', read_only=True)
    name = serializers.CharField(source='genre_name', read_only=True)

    class Meta:
        model = Genre
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
    """목록·홈(추천/할인/신작)용 가벼운 카드."""
    id = serializers.IntegerField(source='game_id', read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'capsule_url',
            'initial_price', 'final_price',
            'platform', 'is_korean', 'genres',
        ]


class GameDetailSerializer(serializers.ModelSerializer):
    """상세용. genre·screenshot·video nested + is_wishlisted."""
    id = serializers.IntegerField(source='game_id', read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
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
            'is_korean', 'required_age', 'offline', 'platform',
            'rawg_id', 'steam_id',
            'is_wishlisted', 'genres', 'screenshots', 'videos',
        ]

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        mgr = getattr(obj, 'wishlisted_by', None)
        if mgr is None:
            return False
        return mgr.filter(user=request.user).exists()