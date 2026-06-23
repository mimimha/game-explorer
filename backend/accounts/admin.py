# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Follow, Medal


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['id', 'username', 'email', 'nickname', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('nickname', 'birth_date', 'profile_img')}),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follow_id', 'follower', 'following']


@admin.register(Medal)
class MedalAdmin(admin.ModelAdmin):
    list_display = ['medal_id', 'user', 'medal_name']
    search_fields = ['medal_name']