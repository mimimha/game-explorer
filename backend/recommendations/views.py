from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from games.models import Game
from .models import RecommendationLog, RecommendationResult
from .serializers import (
    RecommendationLogSerializer, RecommendationLogListSerializer,
)
from .services import generate_recommendations


class RecommendView(APIView):
    """
    POST /recommend/  AI 추천 받기
    prompt_input → 추천 결과 + 로그 저장
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = (request.data.get('prompt_input') or '').strip()
        if not prompt:
            return Response(
                {'prompt_input': ['이 필드는 필수입니다.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1) 로그 저장
        log = RecommendationLog.objects.create(
            user=request.user, prompt_input=prompt
        )

        # 2) 추천 계산 (content 필터 + LLM 설명)
        #    → [{game_id, reason, match_score}, ...]
        recs = generate_recommendations(prompt, user=request.user)

        # 3) 결과 저장
        results = [
            RecommendationResult(
                log=log,
                game_id=r['game_id'],
                reason=r.get('reason', ''),
                match_score=r.get('match_score'),
            )
            for r in recs
            if Game.objects.filter(pk=r['game_id']).exists()
        ]
        RecommendationResult.objects.bulk_create(results)

        # 4) 저장된 형태로 응답
        log.refresh_from_db()
        serializer = RecommendationLogSerializer(
            log, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecommendLogListView(generics.ListAPIView):
    """GET /recommend/logs/  최근 추천 기록 (본인 것)"""
    permission_classes = [IsAuthenticated]
    serializer_class = RecommendationLogListSerializer

    def get_queryset(self):
        return RecommendationLog.objects.filter(user=self.request.user)\
                                        .prefetch_related('results')


class RecommendLogDetailView(generics.RetrieveAPIView):
    """GET /recommend/logs/{log_id}/  추천 기록 상세 (본인 것만)"""
    permission_classes = [IsAuthenticated]
    serializer_class = RecommendationLogSerializer
    lookup_url_kwarg = 'log_id'

    def get_queryset(self):
        # 본인 로그만 조회 가능 → 남의 것 접근 시 404
        return RecommendationLog.objects.filter(user=self.request.user)\
            .prefetch_related('results__game__genres')
