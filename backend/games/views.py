from django.db.models import F
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny

from .models import Game, Genre
from .serializers import (
    GameCardSerializer, GameDetailSerializer, GenreSerializer,
)


class GameListView(generics.ListAPIView):
    """
    GET /games/  목록 + 필터·정렬·검색
    필터: genre, platform, price_lte, is_korean, offline
    정렬: ordering=-metacritic_score / release_date / final_price
    검색: q (제목)
    """
    permission_classes = [AllowAny]
    serializer_class = GameCardSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['metacritic_score', 'release_date', 'final_price']
    ordering = ['-game_id']

    def get_queryset(self):
        qs = Game.objects.prefetch_related('genres', 'platforms').all()
        p = self.request.query_params

        genres = p.getlist('genre')          # tag_id 기준
        if genres:
            qs = qs.filter(genres__tag_id__in=genres).distinct()

        platform = p.get('platform')         # platform_id 또는 이름
        if platform:
            if platform.isdigit():
                qs = qs.filter(platforms__platform_id=platform).distinct()
            else:
                qs = qs.filter(
                    platforms__platform_name__icontains=platform
                ).distinct()

        price_lte = p.get('price_lte')
        if price_lte:
            qs = qs.filter(final_price__lte=price_lte)

        is_korean = p.get('is_korean')
        if is_korean is not None:
            qs = qs.filter(is_korean=is_korean.lower() == 'true')

        offline = p.get('offline')
        if offline is not None:
            qs = qs.filter(offline=offline.lower() == 'true')

        q = p.get('q')
        if q:
            qs = qs.filter(title__icontains=q)

        return qs


class GameDetailView(generics.RetrieveAPIView):
    """GET /games/{game_id}/"""
    permission_classes = [AllowAny]
    serializer_class = GameDetailSerializer
    lookup_field = 'game_id'
    lookup_url_kwarg = 'game_id'
    queryset = Game.objects.prefetch_related(
        'genres', 'platforms', 'screenshots', 'videos'
    )


class GamePostsView(generics.ListAPIView):
    """GET /games/{game_id}/posts/  이 게임 관련 글"""
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        from community.serializers import PostListSerializer
        return PostListSerializer

    def get_queryset(self):
        from community.models import Post
        return Post.objects.filter(game_id=self.kwargs['game_id'])\
                           .select_related('user', 'game')\
                           .prefetch_related('comments')


class RecommendedGamesView(APIView):
    """GET /games/recommended/  오늘의 추천 (홈 01)"""
    permission_classes = [AllowAny]

    def get(self, request):
        games = Game.objects.order_by('?')[:5]
        return Response(GameCardSerializer(
            games, many=True, context={'request': request}).data)


class OnSaleGamesView(APIView):
    """GET /games/on-sale/  할인 중 (홈 02)"""
    permission_classes = [AllowAny]

    def get(self, request):
        games = Game.objects.filter(
            final_price__isnull=False,
            initial_price__gt=F('final_price'),
        ).order_by('-initial_price')[:20]
        return Response(GameCardSerializer(
            games, many=True, context={'request': request}).data)


class NewReleaseGamesView(APIView):
    """GET /games/new-releases/  최근 출시 (홈 03)"""
    permission_classes = [AllowAny]

    def get(self, request):
        games = Game.objects.exclude(release_date__isnull=True)\
                            .order_by('-release_date')[:20]
        return Response(GameCardSerializer(
            games, many=True, context={'request': request}).data)


class GenreListView(generics.ListAPIView):
    """GET /genres/  분류 목록"""
    permission_classes = [AllowAny]
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    pagination_class = None