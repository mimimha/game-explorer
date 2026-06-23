from django.conf import settings
from django.db import models


class RecommendationLog(models.Model):
    """
    추천 행위 1건 (누가·언제·무슨 prompt).
    실제 추천된 게임들은 RecommendationResult 로 N개 매달린다.
    """
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='recommendation_logs', db_column='user_id',
    )
    prompt_input = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendation_log'
        ordering = ['-log_id']

    def __str__(self):
        return f'{self.user} - {self.prompt_input[:20]}'


class RecommendationResult(models.Model):
    """추천 결과 한 건 (로그 1 : 결과 N). 게임 + LLM 이유 + 일치도."""
    result_id = models.AutoField(primary_key=True)
    log = models.ForeignKey(
        RecommendationLog, on_delete=models.CASCADE,
        related_name='results', db_column='log_id',
    )
    game = models.ForeignKey(
        'games.Game', on_delete=models.CASCADE,
        related_name='recommendation_results', db_column='game_id',
    )
    reason = models.TextField(blank=True)          # LLM 생성 추천 이유
    match_score = models.IntegerField(null=True, blank=True)  # 일치도 0~100

    class Meta:
        db_table = 'recommendation_result'
        ordering = ['-match_score']

    def __str__(self):
        return f'log {self.log_id} - {self.game.title}'
