# games/admin.py
from django.contrib import admin
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