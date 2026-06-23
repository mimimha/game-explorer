# games/admin.py
import io

from django.contrib import admin, messages
from django.core.management import call_command
from django.shortcuts import redirect
from django.urls import path

from .models import (
    Game, Genre, Platform, GameTag, GamePlatform, Screenshot, GameVideo,
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
    list_display = ['game_id', 'title', 'final_price',
                    'metacritic_score', 'release_date']
    list_filter = ['is_korean', 'offline']
    search_fields = ['title']
    inlines = [GameTagInline, GamePlatformInline,
               ScreenshotInline, GameVideoInline]
    # 목록 상단에 "RAWG 신작 가져오기" 버튼을 추가한 템플릿
    change_list_template = 'admin/games/game/change_list.html'

    def get_urls(self):
        """기본 admin URL 에 신작 적재용 커스텀 URL 을 끼워넣는다."""
        custom = [
            path(
                'fetch-new/',
                self.admin_site.admin_view(self.fetch_new_games),
                name='games_game_fetch_new',
            ),
        ]
        return custom + super().get_urls()

    def fetch_new_games(self, request):
        """
        RAWG 에서 신작(출시일 최신순)을 받아 DB 에 upsert.
        load_games 관리 명령을 그대로 재사용한다.
        (요청 안에서 동기 실행되므로 데모용으로 소량만 가져온다.)
        """
        out = io.StringIO()
        try:
            call_command(
                'load_games',
                pages=1, page_size=6,
                ordering='-released', no_youtube=True,
                stdout=out,
            )
            self.message_user(
                request,
                f'RAWG 신작을 가져왔습니다. 현재 DB 게임 수: {Game.objects.count()}개',
                level=messages.SUCCESS,
            )
        except Exception as e:  # 네트워크·rate limit 등 실패 시 메시지로 표시
            self.message_user(
                request, f'적재 중 오류가 발생했습니다: {e}',
                level=messages.ERROR,
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


admin.site.register(Screenshot)
admin.site.register(GameVideo)