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
                'fetch-new/',
                self.admin_site.admin_view(self.fetch_new_games),
                name='games_game_fetch_new',
            ),
            path(
                'fill-videos/',
                self.admin_site.admin_view(self.fill_missing_videos),
                name='games_game_fill_videos',
            ),
            path(
                'export-translations/',
                self.admin_site.admin_view(self.export_translations_view),
                name='games_game_export_translations',
            ),
            path(
                'import-translations/',
                self.admin_site.admin_view(self.import_translations_view),
                name='games_game_import_translations',
            ),
        ]
        return custom + super().get_urls()

    def export_translations_view(self, request):
        """미번역 게임(id/title/description)을 JSON 파일로 다운로드한다."""
        qs = (Game.objects.filter(translation_locked=False)
              .filter(Q(title_ko='') | Q(description_ko=''))
              .order_by('game_id'))
        rows = [
            {'id': g.game_id, 'title': g.title, 'description': g.description}
            for g in qs
        ]
        payload = json.dumps(rows, ensure_ascii=False, indent=2)
        resp = HttpResponse(payload, content_type='application/json; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename="to_translate.json"'
        return resp

    def import_translations_view(self, request):
        """업로드한 번역 JSON 을 title_ko/description_ko 에 반영한다."""
        if request.method == 'POST' and request.FILES.get('file'):
            up = request.FILES['file']
            with tempfile.NamedTemporaryFile(
                'wb', suffix='.json', delete=False) as tmp:
                for chunk in up.chunks():
                    tmp.write(chunk)
                path_ = tmp.name
            out = io.StringIO()
            try:
                call_command('import_translations', path_, stdout=out)
                last = out.getvalue().strip().splitlines()[-1] if out.getvalue().strip() else ''
                self.message_user(
                    request, f'번역 JSON 을 반영했습니다. {last}',
                    level=messages.SUCCESS,
                )
            except Exception as e:
                self.message_user(
                    request, f'가져오기 실패: {e}', level=messages.ERROR)
            finally:
                os.remove(path_)
            return redirect('admin:games_game_changelist')

        # GET → 업로드 폼
        context = {
            **self.admin_site.each_context(request),
            'title': '번역 JSON 가져오기',
            'opts': self.model._meta,
        }
        return render(request, 'admin/games/game/import_translations.html', context)

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