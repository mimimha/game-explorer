# games/admin.py
import io
import json
import os
import tempfile

from django.contrib import admin, messages
from django.core.management import call_command
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path

from .models import (
    Game, Genre, Platform, Mood, GameTag, GamePlatform, Screenshot, GameVideo,
    SearchLog,
)


class GameTagInline(admin.TabularInline):
    model = GameTag
    extra = 1


class GamePlatformInline(admin.TabularInline):
    model = GamePlatform
    extra = 1


class ScreenshotInline(admin.TabularInline):
    model = Screenshot
    extra = 1


class GameVideoInline(admin.TabularInline):
    model = GameVideo
    extra = 1


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'title', 'title_ko', 'translation_locked',
                    'final_price', 'metacritic_score', 'release_date']
    # 목록에서 한글 제목·잠금을 바로 수정 (LLM 오역 교정용)
    list_editable = ['title_ko', 'translation_locked']
    list_filter = ['is_korean', 'offline', 'translation_locked']
    search_fields = ['title', 'title_ko']
    inlines = [GameTagInline, GamePlatformInline,
               ScreenshotInline, GameVideoInline]
    # 목록 상단에 "RAWG 신작 가져오기" 버튼을 추가한 템플릿
    change_list_template = 'admin/games/game/change_list.html'
    actions = ['refresh_videos_action']

    def get_urls(self):
        """기본 admin URL 에 신작 적재·영상 채우기 커스텀 URL 을 끼워넣는다."""
        custom = [
            path(
                'add-games/',
                self.admin_site.admin_view(self.add_more_games),
                name='games_game_add_more',
            ),
            path(
                'fill-videos/',
                self.admin_site.admin_view(self.fill_missing_videos),
                name='games_game_fill_videos',
            ),
            path(
                'refresh-prices/',
                self.admin_site.admin_view(self.refresh_prices_view),
                name='games_game_refresh_prices',
            ),
        ]
        return custom + super().get_urls()

    def refresh_prices_view(self, request):
        """Steam 가격을 다시 긁어 갱신(가격 변동·할인 반영). steam_id 있는 게임 중
        랜덤 150개씩(Steam rate limit 보호). 전체 갱신은 터미널 `refresh_prices`.
        """
        out = io.StringIO()
        try:
            call_command('refresh_prices', limit=150, stdout=out)
            last = out.getvalue().strip().splitlines()[-1] if out.getvalue().strip() else ''
            self.message_user(
                request,
                f'Steam 가격을 갱신했습니다. {last} '
                f'(전체 갱신은 터미널 `python manage.py refresh_prices`)',
                level=messages.SUCCESS,
            )
        except Exception as e:
            self.message_user(
                request, f'가격 재수집 실패: {e}', level=messages.ERROR)
        return redirect('admin:games_game_changelist')

    @admin.action(description='선택한 게임의 유튜브 영상 새로고침(리뉴얼)')
    def refresh_videos_action(self, request, queryset):
        """선택한 게임들의 영상을 새 것으로 교체한다(관리자 리뉴얼)."""
        ids = ','.join(str(g.game_id) for g in queryset)
        out = io.StringIO()
        try:
            call_command('backfill_videos', ids=ids, stdout=out)
            self.message_user(
                request, f'{queryset.count()}개 게임의 유튜브 영상을 새로 받았습니다.',
                level=messages.SUCCESS,
            )
        except Exception as e:
            self.message_user(
                request, f'영상 갱신 실패: {e}', level=messages.ERROR,
            )

    def fill_missing_videos(self, request):
        """영상이 없는(새로 추가된) 게임에만 영상을 채운다. 한 번에 최대 25개."""
        out = io.StringIO()
        try:
            call_command('backfill_videos', only_empty=True, limit=25, stdout=out)
            from django.db.models import Count
            remaining = (Game.objects.annotate(v=Count('videos'))
                         .filter(v=0).count())
            msg = '빠진 영상을 채웠습니다.'
            if remaining:
                msg += f' 아직 영상 없는 게임 {remaining}개 — 더 채우려면 다시 클릭하세요.'
            self.message_user(request, msg, level=messages.SUCCESS)
        except Exception as e:
            self.message_user(
                request, f'영상 채우기 실패: {e}', level=messages.ERROR,
            )
        return redirect('admin:games_game_changelist')

    def add_more_games(self, request):
        """RAWG 인기순(-added)에서 '다음 100개'를 이어받아 DB 에 추가한다.

        현재 DB 게임 수로 시작 페이지를 계산하므로, 누를 때마다 새 100개가 들어온다.
        (요청 안에서 동기 실행 → 100개면 1~2분 걸릴 수 있다. 그동안 페이지는 로딩 상태.
         YouTube 영상은 수집하지 않고, 각 게임을 처음 열 때 lazy 로 채워진다.)
        """
        PAGE_SIZE = 20
        PAGES = 5                                  # 20 × 5 = 100개
        before = Game.objects.count()
        start_page = before // PAGE_SIZE + 1       # 이미 받은 만큼 건너뛰고 다음부터
        out = io.StringIO()
        try:
            call_command(
                'load_games',
                pages=PAGES, page_size=PAGE_SIZE, start_page=start_page,
                ordering='-added', no_youtube=True,
                stdout=out,
            )
            # 새 게임 자동 번역: 설명=무료 Google, 제목=GMS 음차(--titles).
            call_command('translate_games', titles=True, stdout=out)
            added = Game.objects.count() - before
            self.message_user(
                request,
                f'게임 {added}개 추가 + 설명·제목 자동 번역 완료. (현재 총 {Game.objects.count()}개) '
                f'영상은 각 게임을 처음 열 때 자동으로 채워집니다.',
                level=messages.SUCCESS,
            )
        except Exception as e:
            self.message_user(
                request, f'적재 중 오류가 발생했습니다: {e}', level=messages.ERROR,
            )
        return redirect('admin:games_game_changelist')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['tag_id', 'genre_name']
    search_fields = ['genre_name']


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['platform_id', 'platform_name']
    search_fields = ['platform_name']


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ['mood_id', 'mood_name']
    search_fields = ['mood_name']


admin.site.register(Screenshot)
admin.site.register(GameVideo)


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'keyword', 'result_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'keyword']
    readonly_fields = ['user', 'keyword', 'result_game_ids', 'created_at']

    @admin.display(description='결과 수')
    def result_count(self, obj):
        return len(obj.result_game_ids or [])