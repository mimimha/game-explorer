from django.db.models import F, Count, Min, Max
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny

from .models import Game, Genre, Platform
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

        genres = p.getlist('genre')          # tag_id 기준 (다중 선택)
        if genres:
            qs = qs.filter(genres__tag_id__in=genres).distinct()

        platforms = p.getlist('platform')    # platform_id 또는 이름 (다중 선택)
        if platforms:
            ids = [v for v in platforms if v.isdigit()]
            names = [v for v in platforms if not v.isdigit()]
            cond = None
            if ids:
                from django.db.models import Q
                cond = Q(platforms__platform_id__in=ids)
            if names:
                from django.db.models import Q
                name_cond = Q(platforms__platform_name__in=names)
                cond = name_cond if cond is None else cond | name_cond
            if cond is not None:
                qs = qs.filter(cond).distinct()

        # 가격 구간
        price_gte = p.get('price_gte')
        if price_gte:
            qs = qs.filter(final_price__gte=price_gte)
        price_lte = p.get('price_lte')
        if price_lte:
            qs = qs.filter(final_price__lte=price_lte)
        if p.get('free') == 'true':          # 무료(가격 0)
            qs = qs.filter(final_price=0)

        # 할인 중 (정가 > 할인가)
        if p.get('on_sale') == 'true':
            qs = qs.filter(
                final_price__isnull=False, initial_price__gt=F('final_price')
            )

        # 평점(메타크리틱) 이상
        metacritic_gte = p.get('metacritic_gte')
        if metacritic_gte:
            qs = qs.filter(metacritic_score__gte=metacritic_gte)

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


class FilterOptionsView(APIView):
    """
    GET /games/filter-options/
    실제 적재된 데이터 기준 필터 옵션. (프론트 필터 UI 구성용)
    하드코딩이 아니라 DB 에 존재하는 장르·플랫폼·가격/평점 범위만 내려준다.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        genres = (
            Genre.objects.annotate(count=Count('games'))
            .filter(count__gt=0).order_by('-count')
        )
        platforms = (
            Platform.objects.annotate(count=Count('games'))
            .filter(count__gt=0).order_by('-count')
        )
        agg = Game.objects.aggregate(
            price_min=Min('final_price'), price_max=Max('final_price'),
            score_min=Min('metacritic_score'), score_max=Max('metacritic_score'),
        )
        on_sale_count = Game.objects.filter(
            final_price__isnull=False, initial_price__gt=F('final_price')
        ).count()

        return Response({
            'genres': [
                {'id': g.tag_id, 'name': g.genre_name, 'count': g.count}
                for g in genres
            ],
            'platforms': [
                {'id': p.platform_id, 'name': p.platform_name, 'count': p.count}
                for p in platforms
            ],
            'price': {
                'min': agg['price_min'],
                'max': agg['price_max'],
                'free_count': Game.objects.filter(final_price=0).count(),
            },
            'metacritic': {'min': agg['score_min'], 'max': agg['score_max']},
            'on_sale_count': on_sale_count,
        })