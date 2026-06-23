from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from games.models import Game
from .models import Wishlist
from .serializers import WishlistItemSerializer


class WishlistView(generics.ListAPIView):
    """GET /wishlist/  내 찜 목록 (토큰 필요)"""
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistItemSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)\
                               .select_related('game')\
                               .prefetch_related('game__genres')


class WishlistToggleView(APIView):
    """
    POST   /games/{game_id}/wishlist/  찜 추가
    DELETE /games/{game_id}/wishlist/  찜 해제
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id):
        game = get_object_or_404(Game, pk=game_id)
        Wishlist.objects.get_or_create(user=request.user, game=game)
        return Response({
            'is_wishlisted': True,
            'wishlist_count': game.wishlisted_by.count(),
        })

    def delete(self, request, game_id):
        game = get_object_or_404(Game, pk=game_id)
        Wishlist.objects.filter(user=request.user, game=game).delete()
        return Response({
            'is_wishlisted': False,
            'wishlist_count': game.wishlisted_by.count(),
        })