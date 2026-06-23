from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Follow, Medal, UserMedal


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['id', 'username', 'email', 'nickname', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('nickname', 'birth_date', 'profile_img')}),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follow_id', 'follower', 'following']


class UserMedalInline(admin.TabularInline):
    model = UserMedal
    extra = 1


@admin.register(Medal)
class MedalAdmin(admin.ModelAdmin):
    list_display = ['medal_id', 'medal_name', 'description']
    search_fields = ['medal_name']
    inlines = [UserMedalInline]


@admin.register(UserMedal)
class UserMedalAdmin(admin.ModelAdmin):
    list_display = ['user', 'medal', 'earned_at']