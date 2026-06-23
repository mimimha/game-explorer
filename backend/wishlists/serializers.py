# wishlists/serializers.py
from rest_framework import serializers
from games.serializers import GenreSerializer
from .models import Wishlist


class WishlistItemSerializer(serializers.ModelSerializer):
    """
    내 찜 목록 항목. 게임 카드 필드를 평탄화하고 wishlisted_at 추가.
    (Wishlist 인스턴스 기준 → game.* 를 끌어온다)
    """
    id = serializers.IntegerField(source='game.game_id', read_only=True)
    title = serializers.CharField(source='game.title', read_only=True)
    capsule_url = serializers.CharField(source='game.capsule_url', read_only=True)
    initial_price = serializers.DecimalField(
        source='game.initial_price', max_digits=10, decimal_places=2,
        read_only=True, allow_null=True,
    )
    final_price = serializers.DecimalField(
        source='game.final_price', max_digits=10, decimal_places=2,
        read_only=True, allow_null=True,
    )
    genres = GenreSerializer(source='game.genres', many=True, read_only=True)
    wishlisted_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            'id', 'title', 'capsule_url',
            'initial_price', 'final_price', 'genres', 'wishlisted_at',
        ]