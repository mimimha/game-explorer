from rest_framework import serializers
from games.serializers import GenreSerializer
from .models import RecommendationLog, RecommendationResult


class ResultGameSerializer(serializers.Serializer):
    """추천 결과에 박히는 게임 요약 카드."""
    id = serializers.IntegerField(source='game_id')
    title = serializers.CharField()
    capsule_url = serializers.CharField(allow_blank=True)
    final_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True
    )
    genres = GenreSerializer(many=True)


class RecommendationResultSerializer(serializers.ModelSerializer):
    """추천 결과 한 건 (게임 + 이유 + 점수)."""
    game = ResultGameSerializer(read_only=True)

    class Meta:
        model = RecommendationResult
        fields = ['game', 'reason', 'match_score']


class RecommendationLogSerializer(serializers.ModelSerializer):
    """추천 받기 응답 · 기록 상세 (결과 nested)."""
    results = RecommendationResultSerializer(many=True, read_only=True)

    class Meta:
        model = RecommendationLog
        fields = ['log_id', 'prompt_input', 'created_at', 'results']


class RecommendationLogListSerializer(serializers.ModelSerializer):
    """최근 추천 기록 목록 (결과 개수만)."""
    result_count = serializers.IntegerField(
        source='results.count', read_only=True
    )

    class Meta:
        model = RecommendationLog
        fields = ['log_id', 'prompt_input', 'result_count', 'created_at']