# games/admin.py
from django.contrib import admin
from .models import Game, Genre, GameTag, Screenshot, GameVideo


class GameTagInline(admin.TabularInline):
    model = GameTag
    extra = 1


class ScreenshotInline(admin.TabularInline):
    model = Screenshot
    extra = 1


class GameVideoInline(admin.TabularInline):
    model = GameVideo
    extra = 1


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'title', 'platform', 'final_price',
                    'metacritic_score', 'release_date']
    list_filter = ['platform', 'is_korean', 'offline']
    search_fields = ['title']
    inlines = [GameTagInline, ScreenshotInline, GameVideoInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['tag_id', 'genre_name']
    search_fields = ['genre_name']


admin.site.register(Screenshot)
admin.site.register(GameVideo)