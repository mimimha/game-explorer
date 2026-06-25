from datetime import date

from django.db.models import F, Count, Min, Max, Case, When, BooleanField, FloatField, Value, ExpressionWrapper
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny

from .models import Game, Genre, Platform, Mood
from .serializers import (
    GameCardSerializer, GameDetailSerializer, GenreSerializer,
)


def _calc_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def _apply_age_filter(qs, request):
    """로그인 유저의 생년월일 기준으로 이용 불가 게임 제외."""
    if not request.user.is_authenticated:
        return qs
    bd = getattr(request.user, 'birth_date', None)
    if not bd:
        return qs
    return qs.filter(required_age__lte=_calc_age(bd))


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
    ordering_fields = ['metacritic_score', 'release_date', 'final_price', 'playtime']
    ordering = ['-game_id']
    pagination_class = None

    # 플레이타임 버킷 경계(시간)
    PLAYTIME_BUCKETS = {
        'short': (None, 10),     # 10시간 미만
        'medium': (10, 40),      # 10~40시간
        'long': (40, None),      # 40시간 이상
    }

    def get_queryset(self):
        qs = _apply_age_filter(
            Game.objects.prefetch_related('genres', 'platforms', 'moods').all(),
            self.request,
        )
        p = self.request.query_params

        genres = p.getlist('genre')          # tag_id 기준 (다중 선택 → AND 교집합)
        for genre in genres:
            qs = qs.filter(genres__tag_id=genre)
        if genres:
            qs = qs.distinct()

        moods = p.getlist('mood')            # mood_id 기준 (다중 선택 → AND 교집합)
        for mood in moods:
            qs = qs.filter(moods__mood_id=mood)
        if moods:
            qs = qs.distinct()

        platforms = p.getlist('platform')    # platform_id 또는 이름 (다중 선택 → AND 교집합)
        for platform in platforms:
            if platform.isdigit():
                qs = qs.filter(platforms__platform_id=platform)
            else:
                qs = qs.filter(platforms__platform_name=platform)
        if platforms:
            qs = qs.distinct()

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

        # 플레이타임 — 버킷(short/medium/long) 또는 직접 범위(gte/lte)
        bucket = p.get('playtime_bucket')
        if bucket in self.PLAYTIME_BUCKETS:
            lo, hi = self.PLAYTIME_BUCKETS[bucket]
            qs = qs.filter(playtime__isnull=False)
            if lo is not None:
                qs = qs.filter(playtime__gte=lo)
            if hi is not None:
                qs = qs.filter(playtime__lt=hi)
        if p.get('playtime_gte'):
            qs = qs.filter(playtime__gte=p.get('playtime_gte'))
        if p.get('playtime_lte'):
            qs = qs.filter(playtime__lte=p.get('playtime_lte'))

        # 플레이 인원 — single/multi/coop (다중 선택 → AND 교집합)
        modes = p.getlist('player_mode')
        if modes:
            if 'single' in modes:
                qs = qs.filter(is_singleplayer=True)
            if 'multi' in modes:
                qs = qs.filter(is_multiplayer=True)
            if 'coop' in modes:
                qs = qs.filter(is_coop=True)

        q = p.get('q')
        if q:
            from django.db.models import Q
            # 제목(영/한) + 설명(영/한) 동시 검색 → "동물" 같은 단어도 설명에서 매칭
            qs = qs.filter(
                Q(title__icontains=q) | Q(title_ko__icontains=q)
                | Q(description__icontains=q) | Q(description_ko__icontains=q)
            ).distinct()

        # 할인순: 할인율 annotation 추가 (order_by는 filter_queryset 오버라이드에서 처리)
        if p.get('ordering') == 'discount':
            qs = qs.annotate(
                discount_rate=Case(
                    When(
                        final_price__isnull=False,
                        initial_price__gt=F('final_price'),
                        then=ExpressionWrapper(
                            (F('initial_price') - F('final_price')) * 1.0 / F('initial_price'),
                            output_field=FloatField(),
                        ),
                    ),
                    default=Value(0.0),
                    output_field=FloatField(),
                )
            )

        return qs

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        # OrderingFilter가 기본 정렬(-game_id)로 덮어쓴 뒤 여기서 재적용
        if self.request.query_params.get('ordering') == 'discount':
            queryset = queryset.order_by('-discount_rate', 'title')
        return queryset

    # 의도(키워드/필터)가 있는 검색만 취향 신호로 기록
    INTENT_KEYS = [
        'q', 'genre', 'mood', 'player_mode', 'platform', 'playtime_bucket',
        'playtime_gte', 'playtime_lte', 'metacritic_gte', 'free', 'on_sale',
        'price_lte', 'price_gte', 'is_korean', 'offline',
    ]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        try:
            self._log_search(request, response)
        except Exception:   # 로깅 실패가 검색을 막지 않도록
            pass
        return response

    def _log_search(self, request, response):
        user = request.user
        if not user.is_authenticated:
            return
        p = request.query_params
        if not any(p.getlist(k) for k in self.INTENT_KEYS):
            return   # 의도 없는 '전체 목록'은 기록 안 함
        data = response.data
        items = data if isinstance(data, list) else data.get('results', [])
        ids = [g['id'] for g in items[:12] if isinstance(g, dict) and 'id' in g]
        if ids:
            from .models import SearchLog
            SearchLog.objects.create(
                user=user, keyword=(p.get('q') or '').strip()[:200],
                result_game_ids=ids,
            )


class GameDetailView(generics.RetrieveAPIView):
    """GET /games/{game_id}/"""
    permission_classes = [AllowAny]
    serializer_class = GameDetailSerializer
    lookup_field = 'game_id'
    lookup_url_kwarg = 'game_id'
    queryset = Game.objects.prefetch_related(
        'genres', 'platforms', 'moods', 'screenshots', 'videos'
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
    """
    GET /games/recommended/  홈 01
    로그인 + (AI 추천 기록 또는 찜)이 있으면 → 취향 분석 추천,
    없으면(비로그인 등) → 무작위 '오늘의 추천'.

    취향 분석: 사용자의 AI 추천 기록 게임 + 찜 게임의 무드·장르를
    가중 집계(AI 0.8 : 찜 0.2)해 프로파일을 만들고, 아직 안 본 게임 중
    그 프로파일에 가장 잘 맞는 것을 추천한다.
    """
    permission_classes = [AllowAny]
    N = 5
    AI_WEIGHT = 0.5     # AI 추천 검색 기록 우선
    WISH_WEIGHT = 0.5    # 찜 목록
    SEARCH_WEIGHT = 0.4  # 라이브러리 검색 기록
    SEARCH_LOG_LIMIT = 30  # 최근 검색 N개만 반영

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            games = self._taste_based(user)
            if games:
                return Response(GameCardSerializer(
                    games, many=True, context={'request': request}).data)
        # 폴백: 무작위 (오늘의 추천)
        games = Game.objects.order_by('?')[:self.N]
        return Response(GameCardSerializer(
            games, many=True, context={'request': request}).data)

    def _taste_based(self, user):
        from collections import defaultdict

        from .models import SearchLog

        ai_ids = list(Game.objects.filter(
            recommendation_results__log__user=user
        ).distinct().values_list('game_id', flat=True))
        wish_ids = list(Game.objects.filter(
            wishlisted_by__user=user
        ).values_list('game_id', flat=True))
        # 최근 라이브러리 검색 결과 게임들(상위 결과 id 모음)
        search_ids = []
        for log in (SearchLog.objects.filter(user=user)
                    .order_by('-created_at')[:self.SEARCH_LOG_LIMIT]):
            search_ids.extend(log.result_game_ids or [])

        if not ai_ids and not wish_ids and not search_ids:
            return []   # 시그널 없음 → 폴백

        # 가중 무드/장르 프로파일 (무드 1.0, 장르 0.5 비중)
        profile = defaultdict(float)

        def accumulate(ids, weight):
            qs = Game.objects.filter(game_id__in=ids).prefetch_related('moods', 'genres')
            for g in qs:
                for m in g.moods.all():
                    profile[('m', m.mood_id)] += weight
                for ge in g.genres.all():
                    profile[('g', ge.tag_id)] += weight * 0.5

        accumulate(ai_ids, self.AI_WEIGHT)
        accumulate(wish_ids, self.WISH_WEIGHT)
        accumulate(search_ids, self.SEARCH_WEIGHT)
        if not profile:
            return []

        # 후보: 이미 본(추천받은·찜한) 게임 제외 → 새로운 발견 위주
        seen = set(ai_ids) | set(wish_ids)
        scored = []
        for g in (Game.objects.exclude(game_id__in=seen)
                  .prefetch_related('moods', 'genres')):
            score = sum(profile.get(('m', m.mood_id), 0) for m in g.moods.all())
            score += sum(profile.get(('g', ge.tag_id), 0) for ge in g.genres.all())
            if score > 0:
                scored.append((g, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [g for g, _ in scored[:self.N]]


class OnSaleGamesView(APIView):
    """GET /games/on-sale/  할인 중 (홈 02)"""
    permission_classes = [AllowAny]

    def get(self, request):
        games = _apply_age_filter(Game.objects.all(), request).filter(
            final_price__isnull=False,
            initial_price__gt=F('final_price'),
        ).order_by('-initial_price')[:20]
        return Response(GameCardSerializer(
            games, many=True, context={'request': request}).data)


class NewReleaseGamesView(APIView):
    """GET /games/new-releases/  최근 출시 (홈 03)"""
    permission_classes = [AllowAny]

    def get(self, request):
        games = _apply_age_filter(Game.objects.all(), request)\
                    .exclude(release_date__isnull=True)\
                    .order_by('-release_date')[:20]
        return Response(GameCardSerializer(
            games, many=True, context={'request': request}).data)


class GameSuggestView(APIView):
    """GET /games/suggest/?q=  제목 자동완성 (최대 8건)"""
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response([])
        from django.db.models import Q
        games = _apply_age_filter(Game.objects.all(), request).filter(
            Q(title__icontains=q) | Q(title_ko__icontains=q)
        ).only('game_id', 'title', 'title_ko')[:8]
        return Response([
            {'game_id': g.game_id, 'title': g.title, 'title_ko': g.title_ko}
            for g in games
        ])


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
        moods = (
            Mood.objects.annotate(count=Count('games'))
            .filter(count__gt=0).order_by('-count')
        )
        agg = Game.objects.aggregate(
            price_min=Min('final_price'), price_max=Max('final_price'),
            score_min=Min('metacritic_score'), score_max=Max('metacritic_score'),
            playtime_min=Min('playtime'), playtime_max=Max('playtime'),
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
            'moods': [
                {'id': m.mood_id, 'name': m.mood_name, 'count': m.count}
                for m in moods
            ],
            'price': {
                'min': agg['price_min'],
                'max': agg['price_max'],
                'free_count': Game.objects.filter(final_price=0).count(),
            },
            'metacritic': {'min': agg['score_min'], 'max': agg['score_max']},
            'playtime': {
                'min': agg['playtime_min'], 'max': agg['playtime_max'],
                'buckets': {
                    'short': Game.objects.filter(playtime__gt=0, playtime__lt=10).count(),
                    'medium': Game.objects.filter(playtime__gte=10, playtime__lt=40).count(),
                    'long': Game.objects.filter(playtime__gte=40).count(),
                },
            },
            'player_mode': {
                'single': Game.objects.filter(is_singleplayer=True).count(),
                'multi': Game.objects.filter(is_multiplayer=True).count(),
                'coop': Game.objects.filter(is_coop=True).count(),
            },
            'on_sale_count': on_sale_count,
        })