from django.contrib import admin
from .models import RecommendationLog, RecommendationResult


class RecommendationResultInline(admin.TabularInline):
    model = RecommendationResult
    extra = 0


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    list_display = ['log_id', 'user', 'prompt_input', 'created_at']
    search_fields = ['prompt_input', 'user__nickname']
    inlines = [RecommendationResultInline]


@admin.register(RecommendationResult)
class RecommendationResultAdmin(admin.ModelAdmin):
    list_display = ['result_id', 'log', 'game', 'match_score']
